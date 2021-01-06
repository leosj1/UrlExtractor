from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
from dateutil.parser import parse
from tld import get_tld
import random, string
import urllib.parse
import requests
import datetime

from UrlExtractor.utils import links_to_json, tags_to_json, get_links
from UrlExtractor.sql import get_connection, commit_to_db

token = "fc7ea3a02234f4589f5042bfcf9d637f"
LOGS = []


def diff_get_article(url, paging=True, count=0):
    #Checking for redirects
    try:
        r = requests.get(url)
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        LOGS.append({"url":url, "error": "Max retries exceeded with url. Caused by SSLError(SSLError('bad handshake: SysCallError(10054, 'WSAECONNRESET')"})
        return []
    except requests.exceptions.InvalidSchema:
        LOGS.append({"url":url, "error": "Invalid URL Schema. Check the URL"})
        return []
    #Sending Diffbot request
    diff_check_account_balance()
    if get_tld(r.url, as_object=True).domain in url:
        diff_endpoint = "https://api.diffbot.com/v3/analyze?token={}&url={}&paging={}".format(token, urllib.parse.quote(url), paging)
        try:
            r = requests.get(diff_endpoint, timeout=60*5)
        except requests.exceptions.Timeout:
            LOGS.append({"url":url, "error": "The diffbot request timed out."})
            return []
        if r.status_code in (504,):
            if count > 2: 
                LOGS.append({"url":url, "error": r.text})
                return []
            else: return diff_get_article(url, count=count+1)
        request = r.json()
    else:
        print("\nThis URL is redirecting: {}".format(url))
        LOGS.append({"url":url, "error":"Redirecting URL"})
        return []
    #Catching errors  
    if 'error' in request: 
        if "Automatic page concatenation exceeded timeout" in request['error']:
            print(f"\nRetrying with paging off due to failed page concatenation: {url}")
            return diff_get_article(url, paging=False)
        elif '404' in request['error'] or '502' in request['error']:
            LOGS.append({"url":url, "error":request['error']})
        else: 
            print("\n{} url: {}".format(request['error'], url))
            LOGS.append({"url":url, "error":request['error']})
        return []
    #Returing Data
    diff_data = request['objects']
    return process_diff_data(diff_data)

def diff_billing_cycle(day_renews: int=8, dnow: datetime=None,) -> int:
    """Caculates the number of days in the current diffbot billing cycle. 
    Currently, we renew on the 8th. dnow should be left as None, exposed only for testing

    Args:
        day_renews (int, optional): Day the billing cycle resets each month. Defaults to 8.
        dnow (datetime, optional): Current day. Leave as NONE, exposed only for testing

    Returns:
        int: The number of days in the current billing cycle. Can be used for queriing the diffbot accounts API. 
    """
    #Getting billing cycle timeframe (currently 8th)
    day_renews = 8
    dnow = datetime.datetime.now() if not dnow else dnow
    if dnow.day >= day_renews:
        #same month
        drenew = datetime.datetime(dnow.year, dnow.month, day_renews)
    else:
        #last month
        drenew = datetime.datetime(dnow.year, dnow.month, day_renews) - relativedelta(months=1)
    delta = dnow - drenew
    days = delta.days + 1 #+1 for inclusive days
    return days

def diff_check_account_balance():
    days = diff_billing_cycle(day_renews=8)
    r = requests.get(f"https://api.diffbot.com/v4/account?token={token}&days={days}")
    api_calls = r.json()
    total_usage = sum([x['credits'] for x in api_calls['usage']])
    percentage = (total_usage/api_calls["planCredits"])*100
    if total_usage >= api_calls["planCredits"]:
        raise Exception(f"""You have exceeded the API limit for this key!!
        Over the last 30 days you have used {total_usage:,} credits. Stop Now!!!""")
    elif percentage in [50,60,70,80,85,90,95,97,98,99]:
        print(f"\nCurrent Diffbot credit usage: {int(percentage)}%")
    return total_usage

def process_diff_data(diff_data):
    articles = []
    for data in diff_data: 
        if 'pageUrl' in data:
            #Cleaning
            domain = urlparse(data['pageUrl']).netloc.replace("www.","")
            if 'date' in data:
                if 'timestamp' in data['date']:
                    try: 
                        published_date = datetime.datetime.fromtimestamp(data['date']['timestamp']/1000) 
                    except OSError:
                        published_date = None
                else: 
                    published_date = parse(data['date'])
            else: 
                published_date = None
            html_content = data['html'] if 'html' in data else None
            links = get_links(html_content) if html_content else None
            author = data['author'] if 'author' in data else None
            tags = tags_to_json([x['label'] for x in data['tags']]) if 'tags' in data else None
            #adding Post
            if 'text' in data and '<?xml' not in data['text'] and good_url(data['pageUrl']):
                sql_query = """INSERT INTO posts (domain, url, author, title, published_date, content, content_html, links, tags) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE domain = %s, author = %s, title = %s, 
                        published_date = %s, content = %s, content_html = %s, links = %s, tags = %s, crawled_time = CURRENT_TIMESTAMP()"""
                sql_data = (domain, data['pageUrl'], author, data['title'], published_date, data['text'], html_content, links, tags, 
                            domain, author, data['title'], published_date, data['text'], html_content, links, tags)
                commit_to_db(sql_query, sql_data)
                #Formating for return
                articles.append({
                    'domain': domain, 
                    'url':data['pageUrl'],
                    'author':author,
                    'title':data['title'], 
                    'title_sentiment':None,
                    'title_toxicity':None,
                    'published_date':published_date,
                    'content':data['text'],
                    'content_sentiment':None,
                    'content_toxicity':None,
                    'content_html':html_content,
                    'language':None, 
                    'links':links,
                    'tags':tags,
                    'crawled_time':datetime.datetime.now()
                })
                #Checking for comments
                if 'discussion' in data:
                    #Doing all non-reply comments first, then adding reply comments sorted by id (so we can get the comment_id from the db)
                    comment_data = [x for x in data['discussion']['posts'] if 'parentId' not in x] + \
                        sorted([x for x in data['discussion']['posts'] if 'parentId' in x], key=lambda k: k['id'])
                    for c in comment_data:
                        comment = {}
                        comment['domain'] = domain
                        comment['url'] = data['pageUrl']
                        comment['username'] = c['author'] if 'author' in c else None
                        comment['comment'] = c['text'] if 'text' in c else ""
                        comment['comment_original'] = c['html'] if 'html' in c else None
                        if 'date' not in c: comment['published_date'] = None
                        elif type(c['date']) == dict: comment['published_date'] = parse(c['date']['str'].replace("d",""))
                        else: comment['published_date'] = parse(c['date'])
                        comment['links'] = get_links(c['html']) if 'html' in c else None
                        comment['reply_count'] = len([x for x in comment_data if 'parentId' in x and c['id'] == x['parentId']])
                        parent_comment = [x for x in comment_data if 'parentId' in c and c['parentId'] == x['id']]
                        comment['reply_to'] = get_reply_to(parent_comment[0], data['pageUrl']) if parent_comment else None
                        insert_comment(comment)
    return articles

    
def get_reply_to(parent_comment, url):
    username = parent_comment['author'] if 'author' in parent_comment else None 
    date = parse(parent_comment['date'], ignoretz=True) if 'date' in parent_comment else None
    connection = get_connection()
    with connection.cursor() as cursor:
        if date: cursor.execute('''Select comment_id from comments where
                url=%s and username=%s and published_date=%s ''',(url, username, date))
        else: cursor.execute('''Select comment_id from comments where
                url=%s and username=%s and published_date is NULL and comment=%s ''',(url, username, parent_comment['text']))
        record = cursor.fetchall()
    connection.close()
    if len(record) > 1: raise IOError("Identified multiple parent comments, we only want 1. Modify the get_repy_to query. ")
    return record[0]['comment_id']


def insert_comment(comment):
    """Checks if the comment is already in database, then updates. 
        If not, generate unique key and update"""
    #Getitng id
    connection = get_connection()
    with connection.cursor() as cursor:
        if comment['published_date']: cursor.execute('''Select comment_id from comments where
                         url=%s and username=%s and published_date=%s ''', 
                         (comment['url'], comment['username'], comment['published_date']))
        else: cursor.execute('''Select comment_id from comments where
                url=%s and username=%s and published_date is NULL and comment=%s ''',
                (comment['url'], comment['username'], comment['comment']))
        record = cursor.fetchall()
        c_id = record[0]['comment_id'] if record else gen_comment_id()
    connection.close()
    #Adding to database
    sql_query = """INSERT INTO comments (domain, url, comment_id, username, comment, 
                    comment_original, links, published_date, reply_count, reply_to) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE domain=%s, username=%s, reply_count=%s,
                    crawled_time = CURRENT_TIMESTAMP()"""
    sql_data = (comment['domain'], comment['url'], c_id, comment['username'], 
                comment['comment'], comment['comment_original'], comment['links'],
                comment['published_date'], comment['reply_count'], comment['reply_to'],
                comment['domain'], comment['username'], comment['reply_count'])
    commit_to_db(sql_query, sql_data)

def good_url(url:str) -> bool:
    """Checks the URL to see if is a valid blog URL. URL's that could point to invalid blog pages will return False

    Args:
        url (str): The blog URL to be checked

    Returns:
        bool: True for a valid blog URL, False for invalid URL
    """
    if any([
        x for x in [
            "archive.html", "/author/","/category/", "/tag/",
            "search?updated-max", "&max-results=", "index.php?","/tagged/",
            "html?page=", "/page/", "/search/", "index.html", "/profile/",
            "?ak_action=reject_mobile", "subscribe.html", "/publications/"
        ] if x in url]): return False
    elif "archive" in url and url[-1].isdigit(): return False
    else: return True

def gen_comment_id():
    return ''.join(random.choices(string.ascii_letters.lower() + string.digits, k=16))
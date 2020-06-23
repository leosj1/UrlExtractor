from urllib.parse import urlparse
from dateutil.parser import parse
import random, string
import requests
import datetime

from UrlExtractor.utils import links_to_json, tags_to_json, get_links
from UrlExtractor.sql import get_connection, commit_to_db

token = "fc7ea3a02234f4589f5042bfcf9d637f"


def diff_get_article(url):  
    diff_endpoint = "https://api.diffbot.com/v3/analyze?token={}&url={}".format(token, url)
    request = requests.get(diff_endpoint).json()
    if 'error' in request: 
        print("\n{} url: {}".format(request['error'], url))
        return []
    diff_data = request['objects']
    return process_diff_data(diff_data)


def process_diff_data(diff_data):
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
            if '<?xml' not in data['text']:
                sql_query = """INSERT INTO posts (domain, url, author, title, published_date, content, content_html, links, tags) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                sql_data = (domain, data['pageUrl'], author, data['title'], published_date, data['text'], html_content, links, tags)
                commit_to_db(sql_query, sql_data)
            
            #Checking for comments
            if 'discussion' in data:
                #Doing all non-nested comments first
                comment_data = sorted(data['discussion']['posts'], key=lambda k: ("parentId" in k, k.get("parentId", None)))
                for c in comment_data:
                    comment = {}
                    comment['domain'] = domain
                    comment['url'] = data['pageUrl']
                    comment['username'] = c['author'] if 'author' in c else None
                    comment['comment'] = c['text']
                    comment['comment_original'] = c['html'] 
                    comment['published_date'] = parse(c['date']) if 'date' in c else None
                    comment['links'] = get_links(c['html'])
                    comment['reply_count'] = len([x for x in comment_data if 'parentId' in x and c['id'] == x['parentId']])
                    parent_comment = [x for x in comment_data if 'parentId' in c and c['parentId'] == x['id']]
                    comment['reply_to'] = get_reply_to(parent_comment[0]) if parent_comment else None
                    insert_comment(comment)
    return 


def get_reply_to(parent_comment):
    username = parent_comment['author'] if 'author' in parent_comment else None 
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute('''Select comment_id from comments where
                         url=%s and username=%s and comment_original=%s ''', 
                         (parent_comment['pageUrl'], username, parent_comment['html']))
        record = cursor.fetchall()
    return record[0]['comment_id']


def insert_comment(comment):
    """Checks if the comment is already in database, then updates. 
        If not, generate unique key and update"""
    #Getitng id
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute('''Select comment_id from comments where
                         url=%s and username=%s and published_date=%s ''', 
                         (comment['url'], comment['username'], comment['published_date']))
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
    

def gen_comment_id():
    return ''.join(random.choices(string.ascii_letters.lower() + string.digits, k=16))
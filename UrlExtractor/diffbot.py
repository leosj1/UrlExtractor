from urllib.parse import urlparse
from dateutil.parser import parse
import urllib.parse
import requests
import datetime
import pymysql
from tqdm import tqdm
import string, random, json, re

from UrlExtractor.utils import links_to_json, tags_to_json, get_links
from UrlExtractor.sql import get_connection, commit_to_db

# token = "fc7ea3a02234f4589f5042bfcf9d637f"
token = "fc7ea3a02234f4589f5042bfcf9d637f"


def diff_get_article(url, paging=True):  
    diff_endpoint = "https://api.diffbot.com/v3/analyze?token={}&url={}&paging={}".format(token, urllib.parse.quote(url), paging)
    try:
        request = requests.get(diff_endpoint).json()
    except Exception as e:
        print(e)
        return []
    if 'error' in request: 
        if "Automatic page concatenation exceeded timeout" in request['error']:
            print(f"\nRetrying with paging off due to failed page concatenation: {url}")
            return diff_get_article(url, paging=False)
        elif '404' in request['error'] or '502' in request['error']:
            print(f"\nUnable to download due to 404/502 error: {url}")
        else: 
            print("\n{} url: {}".format(request['error'], url))
        return []
    diff_data = request['objects']

    return process_diff_data(diff_data)


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
            if 'text' in data and '<?xml' not in data['text']:
                sql_query = """INSERT INTO posts (domain, url, author, title, published_date, content, content_html, links, tags) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                sql_data = (domain, data['pageUrl'], author, data['title'], published_date, data['text'], html_content, links, tags)
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
                        comment['published_date'] = parse(c['date']) if 'date' in c else None
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
        cursor.execute('''Select comment_id from comments where
                         url=%s and username=%s and published_date=%s ''', 
                         (url, username, date))
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
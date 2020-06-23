# from BlogCrawler.pipelines import get_connection
from urllib.parse import urlparse
from json import JSONDecoder
import pycountry
import scrapy
from itertools import chain
import json
import os
import re
from dateutil.parser import parse
import ast
import urllib
import requests

def tags_to_json(tags):
    if tags:
        df = {'tags':tags}
        return json.dumps(df)
    else:
        return None

def links_to_json(links):
    if links: 
        df = {'links':links}
        return json.dumps(df)
    else:
        return None

def get_links(html):
    return links_to_json(re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+',html.replace('};', '')))

def get_matching_links(html, match_str):
    links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+',html.replace('};', ''))
    return [link for link in links if match_str in link]

def get_domain(url):
    return urlparse(url).netloc

def get_keywords():
    with open('search_strings.txt') as s:
        data = s.readlines()
        return list(map(lambda x: x.replace('\n',''), data))

def get_request(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text


# def get_start_urls(domain):
#     connection = get_connection()
#     with connection.cursor() as cursor: 
#         cursor.execute("SELECT url FROM posts where domain = %s;", domain)
#         records = [x['url'] for x in cursor.fetchall()]
#     connection.close()
#     return records

# def get_users(domain):
#     connection = get_connection()
#     with connection.cursor() as cursor: 
#         cursor.execute("SELECT username, user_id FROM comments where domain = %s;", domain)
#         user_dict = {}
#         for x in cursor.fetchall():
#             user_dict[x['username']] = x['user_id']      
#     connection.close()
#     return user_dict

def parse_datetime(date):
    if 'EDT' in date:
        result = parse(date, tzinfos={"EDT": "UTC-5"}) 
    elif 'EST' in date:
        result = parse(date, tzinfos={"EST": "UTC-5"}) 
    else:
        result = parse(date) 
    return result

def find_json(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data
    https://stackoverflow.com/questions/54235528/how-to-find-json-object-in-text-with-python
    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.
    """
    results = []
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            if result: results.append(result)
            pos = match + index
        except ValueError:
            pos = match + 1
    return results

def find_arry(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data
    https://stackoverflow.com/questions/54235528/how-to-find-json-object-in-text-with-python
    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.
    """
    results = []
    pos = 0
    while True:
        match_start = text.find('[', pos)
        match_end = text.find(']', pos)
        if match_start == -1 and match_end == -1:
            break
        try:
            result = ast.literal_eval(text[match_start:match_end +1])
            if result: results.append(result)
            pos = match_start + match_end
        except ValueError:
            pos = match_start + 1
    return results

def author_title(author):
    result = author
    if ' and ' in result or ' & ' in result:
        result_split = result.split('and')
        res = 'and'.join([x.title() for x in result_split])
    elif result.isupper():
        return result.title()
    else:
        res = result
    return res
    
def relevant(content, keywords=[], use=None):
    if type(keywords) != list:
        raise TypeError("Please insert keywords as a list")
    elif keywords and use:
        raise InterruptedError("You defined keywords and a built in check. Please use one or the other")
    elif not keywords and not use:
        raise InterruptedError("Please provide keywords or use some built in ones")

    #Using built in keywords
    if use:
        with open('keywords.json') as json_file:
            data = json.load(json_file)
            if use in data: keywords = data[use]
            else: raise KeyError(f"We don't have built in keywords for {use}. You can add it yourself in the keywords.json file\nHere are the ones available: {data.keys()}")

    for keyword in keywords:
        #+ Keywords
        required = [x.lower() for x in keyword.split("+") if "|" not in x]
        or_words = list(chain(*[x.lower().split("|") for x in keyword.split("+") if "|" in x]))
        search_terms = keyword.replace("+", "|").replace('(','').replace(')','')
        match = re.findall(search_terms, content.lower(), re.IGNORECASE)
        if match and set(required).issubset(set(match)) and any([x for x in or_words if x in match]):
            return True
    return False

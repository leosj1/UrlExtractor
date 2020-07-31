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
import pandas as pd
import io

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
    if type(html) == None: raise TypeError('''Passed a None object to get links. 
        This should be the html of the page, so look into your code why you aren't selecting the hmtl properly.''')
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

    #Cleaning content, return if empty after cleaning
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    content = content.translate(translator)
    if not content.strip(): return False

    #Using built in keywords
    if use:
        with open('keywords.json', encoding="utf-8") as json_file:
            data = json.load(json_file)
            if use in data: keywords = data[use]
            else: raise KeyError(f"We don't have built in keywords for {use}. You can add it yourself in the keywords.json file\nHere are the ones available: {data.keys()}")

    for groups in keywords:
        if "+( " in groups or " )" in groups: raise ValueError(f"Don't leave a space before or after '+( ', ' )' instead bump the word right next to it. \n{groups}")
        #Grouping
        if groups.startswith("("):
            grouped = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+',groups)
            grouped = [x.replace("(+","+") for x in grouped if x != ")"]
            for pos, i in enumerate(grouped):
                if i.endswith(")") and "(" not in i:
                    grouped[pos] = i.replace(")","")
        else: grouped = [groups]
        for keyword in grouped:
            #+ Keywords
            required = [x.lower().replace("+","") for x in keyword.split() if "+" in x and '(' not in x]
            or_words = [x.lower().replace("+(","").replace(")","") for x in keyword.split() if "+" not in x or "+(" in x]
            search_terms = "|".join(required + or_words)
            match = re.findall(search_terms, content.lower(), re.IGNORECASE)
            if match and set(required).issubset(set(match)) and any([x for x in or_words if x in match]):
                return True
    return False

def get_relevant_keywords(use = None):
    results = []
    if use:
        with open('keywords.json', encoding="utf-8") as json_file:
            data = json.load(json_file)
            if use in data: keywords = data[use]
            else: raise KeyError(f"We don't have built in keywords for {use}. You can add it yourself in the keywords.json file\nHere are the ones available: {data.keys()}")

    for groups in keywords:
        if "+( " in groups or " )" in groups: raise ValueError(f"Don't leave a space before or after '+( ', ' )' instead bump the word right next to it. \n{groups}")
        #Grouping
        if groups.startswith("("):
            grouped = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+',groups)
            grouped = [x.replace("(+","+") for x in grouped if x != ")"]
            for pos, i in enumerate(grouped):
                if i.endswith(")") and "(" not in i:
                    grouped[pos] = i.replace(")","")
        else: grouped = [groups]
        for keyword in grouped:
            #+ Keywords
            required = [x.lower().replace("+","") for x in keyword.split() if "+" in x and '(' not in x]
            or_words = [x.lower().replace("+(","").replace(")","") for x in keyword.split() if "+" not in x or "+(" in x]        
            required_words = "\"" + '\" \"'.join(required) + "\""
            or_words = "\"" + '\" \"'.join(or_words) + "\""
            results.append((required_words, or_words))
    return results


def get_txt_data(file_name):
    with open(f'{file_name}.txt') as f:
        data = f.readlines()
    f.close()
    return list(map(lambda x: x.replace('\n', ''), data))
    

def last_page(data):
    with open('last_pages.csv', 'a', encoding='utf-8') as f:
        f.write(data)
        f.close()

def get_start_page(domain, project, words):
    with open('last_pages.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        fo = io.StringIO()
        fo.writelines(u"" + line.replace(',',';', 4) for line in lines)
        fo.seek(0) 
        result = pd.read_csv(fo, sep=';')
    data = result[(result['domain'] == domain) & (result['project'] == project) & (result['keywords'] == str(words))]
    # Last page
    page_num = data['last_page'].max()
    status = 'NOT_FOUND' if str(page_num) == 'nan' else 'FOUND'
    page_num = 0 if str(page_num) == 'nan' else page_num

    return page_num, status

def open_keywords(use=None, fname='keywords.json',):
    with open(fname, encoding="utf-8") as json_file:
        data = json.load(json_file)
    if not use: return data
    else:
        try: return data[use]
        except KeyError: raise KeyError("You chose a project name that is not in {}: {}".format(fname, use))



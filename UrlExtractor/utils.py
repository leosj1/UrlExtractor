from itertools import chain
import json
import re

def links_to_json(links):
    if links: 
        df = {'links':links}
        return json.dumps(df)
    else:
        return None

def tags_to_json(tags):
    if tags:
        df = {'tags':tags}
        return json.dumps(df)
    else:
        return None

def get_links(html):
    return links_to_json(re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+',html.replace('};', '')))

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
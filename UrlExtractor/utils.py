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

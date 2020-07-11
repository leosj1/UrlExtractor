# -*- coding: utf-8 -*-
import scrapy
import requests
from tqdm import tqdm
import json
import datetime
import urllib
import pause


from UrlExtractor.items import Posts
from UrlExtractor.utils import get_api_keys, get_relevant_keywords, last_page, get_start_page

class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['google.com', 'wordpress.com']
    start_urls = ['http://google.com/']
    project = 'muri'

    # Standard google format 
    # "https://www.googleapis.com/customsearch/v1?q={searchTerms}&num={count?}&start={startIndex?}&lr={language?}&safe={safe?}&cx={cx?}&sort={sort?}&filter={filter?}&gl={gl?}&cr={cr?}&googlehost={googleHost?}&c2coff={disableCnTwTranslation?}&hq={hq?}&hl={hl?}&siteSearch={siteSearch?}&siteSearchFilter={siteSearchFilter?}&exactTerms={exactTerms?}&excludeTerms={excludeTerms?}&linkSite={linkSite?}&orTerms={orTerms?}&relatedSite={relatedSite?}&dateRestrict={dateRestrict?}&lowRange={lowRange?}&highRange={highRange?}&searchType={searchType}&fileType={fileType?}&rights={rights?}&imgSize={imgSize?}&imgType={imgType?}&imgColorType={imgColorType?}&imgDominantColor={imgDominantColor?}&alt=json"

    def parse(self, response):
        words = get_relevant_keywords(use=self.project)
        for word in words:
            response = get_google_request(word, self.project)
            for items in response:
                if not items['link'].endswith('.pdf'):
                    blog = Posts()
                    # blog['domain'] = domain
                    blog['url'] =  items['link']
                    yield blog            

def get_google_request(words, project):
    results = []
    api_keys = get_api_keys()
    api_keys = [x for x in api_keys if x != '']

    domain = "wordpress.com"
    start = get_start_page(domain, project)
    location = "Australia"
    siteSearchFilter = "i"
    cse_key = "008008521178205893081:w7ksepj1jro"
    pbar = tqdm(total=len(api_keys), desc="Google Web Requests")

    required_keywords , or_keywords = words
    required_keywords = urllib.parse.quote(required_keywords, safe='')
    or_keywords = urllib.parse.quote(or_keywords, safe='')
    
    while True: 
        page_url = f"https://www.googleapis.com/customsearch/v1?key={api_keys[0]}&start={start}&cx={cse_key}&cr={location}&siteSearch={domain}&siteSearchFilter={siteSearchFilter}&exactTerms={required_keywords}&orTerms={or_keywords}&as_occt=body"
        response = requests.get(page_url)
        if response.status_code == 200:
            response = json.loads(response.text)
            if 'items' in response:
                results += response['items']

                # today = datetime.datetime.now()
                # last_page_data = f'{domain},{today.strftime("%Y-%m-%d %H:%M")},{start},{project},{words}'
                # last_page(last_page_data)
                if 'nextPage' in response['queries']:
                    # Limiting to top 11 results
                    if response['queries']['nextPage'][0]['startIndex'] == 11:
                        break
                    else:
                        start+=10
            else:
                break
                        
        elif response.status_code == 429:
            # Quota is out
            if api_keys:
                api_keys.remove(api_keys[0])
                pbar.update(1)
                if not api_keys: 
                    today = datetime.datetime.now()
                    last_page_data = f'{domain},{today.strftime("%Y-%m-%d %H:%M")},{start},{project},{words}'
                    last_page(last_page_data)
                    
                    # Pause till the next day
                    next_day = today + datetime.timedelta(days=1)
                    year,month, day = next_day.strftime("%Y-%m-%d").split('-')
                    pause.until(datetime.datetime(int(year), int(month), int(day)))
                    api_keys = get_api_keys()
                    break
        elif 'error' in json.loads(response.text):
            break

    return results


           


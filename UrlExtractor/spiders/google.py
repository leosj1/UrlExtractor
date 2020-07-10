# -*- coding: utf-8 -*-
import scrapy
import requests
from tqdm import tqdm
import json
import datetime

from UrlExtractor.items import Posts
from UrlExtractor.utils import get_api_keys, get_relevant_keywords, last_page, get_start_page

class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['google.com', 'wordpress.com']
    start_urls = ['http://google.com/']

    # Standard google format 
    # "https://www.googleapis.com/customsearch/v1?q={searchTerms}&num={count?}&start={startIndex?}&lr={language?}&safe={safe?}&cx={cx?}&sort={sort?}&filter={filter?}&gl={gl?}&cr={cr?}&googlehost={googleHost?}&c2coff={disableCnTwTranslation?}&hq={hq?}&hl={hl?}&siteSearch={siteSearch?}&siteSearchFilter={siteSearchFilter?}&exactTerms={exactTerms?}&excludeTerms={excludeTerms?}&linkSite={linkSite?}&orTerms={orTerms?}&relatedSite={relatedSite?}&dateRestrict={dateRestrict?}&lowRange={lowRange?}&highRange={highRange?}&searchType={searchType}&fileType={fileType?}&rights={rights?}&imgSize={imgSize?}&imgType={imgType?}&imgColorType={imgColorType?}&imgDominantColor={imgDominantColor?}&alt=json"

    def parse(self, response):
        response = get_google_request()
        for items in response:
            blog = Posts()
            # blog['domain'] = domain
            blog['url'] =  items['link']
            yield blog            

def get_google_request():
    results = []
    api_keys = get_api_keys()
    api_keys = [x for x in api_keys if x != '']
    domain = "wordpress.com"
    start = get_start_page(domain)
    location = "Australia"
    siteSearchFilter = "i"
    cse_key = "008008521178205893081:w7ksepj1jro"
    project = 'ausi_dod'
    required_keywords, or_keywords = get_relevant_keywords(use=project)
    pbar = tqdm(total=len(api_keys), desc="Google Web Requests")
    
    while True: 
        page_url = f"https://www.googleapis.com/customsearch/v1?key={api_keys[0]}&start={start}&cx={cse_key}&cr={location}&siteSearch={domain}&siteSearchFilter={siteSearchFilter}&exactTerms={required_keywords}&orTerms={or_keywords}&as_occt=body"
        response = requests.get(page_url)
        if response.status_code == 200:
            response = json.loads(response.text)
            results += response['items']
            if 'nextPage' in response['queries']:
                start+=10
        elif response.status_code == 429:
            # Quota is out
            if api_keys:
                api_keys.remove(api_keys[0])
                pbar.update(1)
                if not api_keys: 
                    last_page_data = f'{domain},{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")},{start},{project}'
                    last_page(last_page_data)
                    break
    return results

         

           


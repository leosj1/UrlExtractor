# -*- coding: utf-8 -*-
import scrapy
import requests
from tqdm import tqdm
import json
import datetime
import urllib
import pause


from UrlExtractor.items import Posts
from UrlExtractor.utils import get_txt_data, get_relevant_keywords, last_page, get_start_page, get_domain, open_keywords

class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['google.com', 'wordpress.com']
    start_urls = ['http://google.com/']
    project = 'ausi_dod'
    today = datetime.datetime.now() #today's date

    def parse(self, response):
        words = get_relevant_keywords(use=self.project)
        domains = open_keywords(use = self.project, fname=r"C:\UrlExtractor\UrlExtractor\cosmos_diffbot\domains.json")

        for domain in domains:
            domain_name = get_domain(domain)
            domain = domain if not domain_name else domain_name

            for word in words:
                start_index, start_status = get_start_page(domain, self.project, word)
                start = -1 if start_index == -1 else start_index + 10

                response = get_google_request(word, self.project, domain, start_status, start_index, start)
                item_response = response[0]
                last_crawled_start = response[1]

                for items in item_response:
                    if not items['link'].endswith('.pdf')  and 'archive.html' not in items['link'] and '/author/' not in items['link'] and '/category/' not in items['link'] and '/tag/' not in items['link'] and 'http-redirect' not in items['link'] and '/articles/' not in items['link'] and 'search?updated-max' not in items['link'] and '&max-results=' not in items['link'] and 'index.php?' not in items['link'] :
                        blog = Posts()

                        if items['link']:
                            blog['url'] =  items['link']

                            # Keeping track of the extracted keywords and start index
                            # url_domain_name = get_domain(items['link'])
                            last_page_data = f'{domain},{self.today.strftime("%Y-%m-%d %H:%M")},{last_crawled_start},{self.project},{word}\n'
                            last_page(last_page_data)

                            # update_domains(domain, use=self.project)

                            yield blog
                        
                    
def update_domains(domain, use=None, fname=r"C:\UrlExtractor\UrlExtractor\cosmos_diffbot\domains.json"):
    with open(fname, encoding="utf-8") as json_file:
        data = json.load(json_file)
    if not use: return data
    else:
        try: 
            data[use].append(domain)
            with open(fname, 'w') as fp:
                json.dump(data, fp)

        except KeyError: raise KeyError("You chose a project name that is not in {}: {}".format(fname, use))

def get_google_request(words, project, domain, start_status, start_index, start):
    results = []
    api_keys = get_txt_data('api_keys')
    api_keys = [x for x in api_keys if x != '']

    # domains = get_txt_data('domains')
    # domains = [x for x in domains if x != '']
    # domain = "wordpress.com"
    # domain = domains[0]

    

    # location = "Ukraine"
    siteSearchFilter = "i"
    cse_key = "008008521178205893081:w7ksepj1jro"
    pbar = tqdm(total=len(api_keys), desc="Google Web Requests")

    required_keywords , or_keywords = words
    # required_keywords = urllib.parse.quote(required_keywords, safe='')
    # or_keywords = urllib.parse.quote(or_keywords, safe='')

    limit = 200
    today = datetime.datetime.now() #today's date
    
    while True:
        if start == -1:
            break

        # Standard google format 
        # "https://www.googleapis.com/customsearch/v1?q={searchTerms}&num={count?}&start={startIndex?}&lr={language?}&safe={safe?}&cx={cx?}&sort={sort?}&filter={filter?}&gl={gl?}&cr={cr?}&googlehost={googleHost?}&c2coff={disableCnTwTranslation?}&hq={hq?}&hl={hl?}&siteSearch={siteSearch?}&siteSearchFilter={siteSearchFilter?}&exactTerms={exactTerms?}&excludeTerms={excludeTerms?}&linkSite={linkSite?}&orTerms={orTerms?}&relatedSite={relatedSite?}&dateRestrict={dateRestrict?}&lowRange={lowRange?}&highRange={highRange?}&searchType={searchType}&fileType={fileType?}&rights={rights?}&imgSize={imgSize?}&imgType={imgType?}&imgColorType={imgColorType?}&imgDominantColor={imgDominantColor?}&alt=json"
        
        # Documentation can be found here - https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
        payload = {
                    'key': api_keys[0],
                    'q': None, 
                    'num': None, 
                    'start': start_index,
                    'lr': None,
                    'safe': None,
                    'cx': cse_key,
                    'sort': None,
                    'filter': None,
                    'gl': None,
                    'cr': "countryUA", #countryUA - Ukraine #countryAU - Australis
                    'googlehost': None,
                    'c2coff': None,
                    'hq': None,
                    'hl': None,
                    'siteSearch': domain,
                    'siteSearchFilter': siteSearchFilter,
                    'exactTerms': required_keywords,
                    'excludeTerms': None,
                    'linkSite': None,
                    'orTerms': or_keywords,
                    'relatedSite': None,
                    'dateRestrict': None, #'m[8]'
                    'lowRange': None,
                    'highRange': None,
                    'searchType': None,
                    'fileType': None,
                    'rights': None,
                    'imgSize': None,
                    'imgType': None,
                    'imgColorType': None,
                    'imgDominantColor': None,
                    'alt': None,
                    'occt': 'body' #ass occured in body and not anywhere else
                    }

        # page_url = f"https://www.googleapis.com/customsearch/v1?key={api_keys[0]}&start={start_index}&cx={cse_key}&siteSearch={domain}&siteSearchFilter={siteSearchFilter}&exactTerms={required_keywords}&orTerms={or_keywords}&as_occt=body&dateRestrict=m[8]"

        # Dont send request if start_status is "NOT_FOUND"
        if start_status == 'NOT_FOUND' or start <= limit - 1:
            response = requests.get('https://www.googleapis.com/customsearch/v1', params=payload)
            if response.status_code == 200:
                response = json.loads(response.text)
                if 'items' in response:
                    results += response['items']

                    if 'nextPage' in response['queries']:
                        # Limiting to top 'limit' results
                        next_index = response['queries']['nextPage'][0]['startIndex']
                        if  next_index == limit + 1 or next_index == limit:
                            break
                        else:
                            start_index+=10
                    else:
                        break
                else:
                    # Update csv with -1 because no data found for keyword
                    start_index = -1
                    last_page_data = f'{domain},{today.strftime("%Y-%m-%d %H:%M")},{start_index},{project},{words}\n'
                    last_page(last_page_data)
                    break
                            
            elif response.status_code == 429:
                # Quota is out
                if api_keys:
                    api_keys.remove(api_keys[0])
                    pbar.update(1)
                    if not api_keys: 
                        # last_page_data = f'{domain},{today.strftime("%Y-%m-%d %H:%M")},{start},{project},{words}\n'
                        # last_page(last_page_data)
                        
                        # Pause till the next day
                        next_day = today + datetime.timedelta(days=1)
                        year,month, day = next_day.strftime("%Y-%m-%d").split('-')
                        pause.until(datetime.datetime(int(year), int(month), int(day)))
                        api_keys = get_txt_data('api_keys')
                        # break
            elif 'error' in json.loads(response.text):
                break
        else:
            break

    # Keeping track of the extracted keywords and start index
    # if start_index != -1 or start != -1:
    #     last_page_data = f'{domain},{today.strftime("%Y-%m-%d %H:%M")},{start_index},{project},{words}\n'
    #     last_page(last_page_data)

    # domains.remove(domain)

    return results, start_index


           


# -*- coding: utf-8 -*-
import scrapy
import re
from UrlExtractor.items import AnyPosts

class AnyDomainSpider(scrapy.Spider):
    name = 'AnyDomain'
    
    def __init__(self, category='', **kwargs):
        super().__init__(**kwargs)
        self.domain = self.DOMAIN
        self.allowed_domains = [self.DOMAIN]
        self.start_urls = ['http://' + self.DOMAIN + '/']
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    
    
    def parse(self, response):
        #Some files don't have content 'like wp-content'
        try:
            response.text
        except AttributeError:
            return 
    
        #Getting all URL's on page
        for url in re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', response.text.replace('};', '')):
            if self.domain in url: #If domain in page
                if re.match(self.MATCH, url): #If ULR pattern matches
                    yield scrapy.Request(url, self.parse_blog)
                yield scrapy.Request(url, self.parse)
       

    def parse_blog(self, response):
        # Post
        blog = AnyPosts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['crawl_diffbot'] = self.CRAWL_DIFFBOT  
        blog['file_name'] = self.FILE_NAME
        #-Cleaning Post
        yield blog



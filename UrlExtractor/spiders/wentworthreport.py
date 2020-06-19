# -*- coding: utf-8 -*-
import scrapy
import re
from UrlExtractor.items import Posts

class WentworthreportSpider(scrapy.Spider):
    name = 'wentworthreport'
    domain = 'wentworthreport.com'
    allowed_domains = ['wentworthreport.com']
    start_urls = ['https://wentworthreport.com/?s=coronavirus']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.css('.entry-summary a').xpath('@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        next_page = response.css('.bd-paginationitem-6 a').xpath('@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, self.parse)


    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = None     
        #-Cleaning Post
        yield blog

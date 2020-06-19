# -*- coding: utf-8 -*-
import scrapy
import re
from UrlExtractor.items import Posts

class AustraliannationalreviewSpider(scrapy.Spider):
    name = 'australiannationalreview'
    domain = "australiannationalreview.com"
    allowed_domains = ['australiannationalreview.com']
    start_urls = ['https://australiannationalreview.com/?s=covid-19']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4

    def parse(self, response):
        #Getting links of required catagories
        for url in response.css('.entry-title a').xpath('@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        # Getting next page
        count = 1
        while count <= 13:
            count +=1
            next_page = f'https://australiannationalreview.com/page/{count}/?s=covid-19'
            yield scrapy.Request(next_page, self.parse)
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.css('.entry-title::text').extract_first()      
        yield blog
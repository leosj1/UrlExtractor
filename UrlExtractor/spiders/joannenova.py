# -*- coding: utf-8 -*-
import scrapy
import re
from UrlExtractor.items import Posts

class JoannenovaSpider(scrapy.Spider):
    name = 'joannenova'
    domain = 'joannenova.com.au'
    allowed_domains = ['joannenova.com.au']
    start_urls = ['http://joannenova.com.au/?s=covid-19']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.css('.post-headline a').xpath('@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        count = 1
        while count <= 6:
            count +=1
            next_page = f'http://joannenova.com.au/page/{count}/?s=covid-19'
            yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//div[@class="post-headline"]/h2/a/@title').get()     
        #-Cleaning Post
        yield blog

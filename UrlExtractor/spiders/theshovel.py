# -*- coding: utf-8 -*-
import scrapy
import re
from UrlExtractor.items import Posts

class TheshovelSpider(scrapy.Spider):
    name = 'theshovel'
    domain= 'theshovel.com.au'
    allowed_domains = ['www.theshovel.com.au    ']
    start_urls = ['https://www.theshovel.com.au/?s=covid-19']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//div[@id="archive_posts"]/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        #next_page = response.xpath('//*[@id="archive_posts"]/div[2]/a/@href').extract_first()
        #if next_page:
            #yield scrapy.Request(next_page, self.parse)

        # Getting next page
        count = 1
        while count <=3:
            count +=1
            next_page = f'https://www.theshovel.com.au/page/{count}/?s=covid-19'
            yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//div[@id="archive_posts"]/a[1]/div/div[2]/text()').get().strip()     
        #-Cleaning Post
        yield blog



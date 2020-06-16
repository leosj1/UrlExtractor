# -*- coding: utf-8 -*-
import scrapy
import re
from Australia.items import Posts

class EutimesSpider(scrapy.Spider):
    name = 'eutimes'
    domain = 'eutimes.net'
    allowed_domains = ['www.eutimes.net']
    start_urls = ['https://www.eutimes.net/?s=covid-19']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//div[@id="archive"]/h2/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        next_page = response.xpath('//div[@id="content"]/div[18]/div/a/@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, self.parse)

        #Getting next page
        #count = 1
        #while count <= 13:
            #count +=1
            #next_page = f'https://www.eutimes.net/page/{count}/?s=covid-19'
            #yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h1[@class="entry-title"]//text()').extract_first()     
        #-Cleaning Post
        yield blog




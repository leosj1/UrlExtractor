# -*- coding: utf-8 -*-
import scrapy
import scrapy
import re
from Australia.items import Posts

class BetootaadvocateSpider(scrapy.Spider):
    name = 'betootaadvocate'
    domain ='www.betootaadvocate.com'
    allowed_domains = ['www.betootaadvocate.com']
    start_urls = ['https://www.betootaadvocate.com/?s=covid-19']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//h3[@class="entry-title td-module-title"]/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        #next_page = response.xpath('//div[@class="page-nav td-pb-padding-side"]/a/@href').extract_first()
        #if next_page:
            #yield scrapy.Request(next_page, self.parse)
        
         # Getting next page
        count = 1
        while count <= 22:
            count +=1
            next_page = f'https://www.betootaadvocate.com/page/{count}/?s=covid-19'
            yield scrapy.Request(next_page, self.parse)
    
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h3[@class="entry-title td-module-title"]/a/text()').extract()     
        #-Cleaning Post
        yield blog


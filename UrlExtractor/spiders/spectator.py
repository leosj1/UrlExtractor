# -*- coding: utf-8 -*-
import scrapy
import re
from UrlExtractor.items import Posts


class SpectatorSpider(scrapy.Spider):
    name = 'spectator'
    domain = 'www.spectator.com.au'
    allowed_domains = ['www.spectator.com.au']
    start_urls = ['https://www.spectator.com.au/category/australia/']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//h2[@class="term-item__title"]/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
       # next_page = response.css('.bd-paginationitem-6 a').xpath('@href').extract_first()
       # if next_page:
          #  yield scrapy.Request(next_page, self.parse)

        # Getting next page
        count = 1
        while count <=179:
            count +=1
            next_page = f'https://www.spectator.com.au/category/australia/page/{count}/'
            yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h2[@class="term-item__title"]/a/text()').extract_first()     
        #-Cleaning Post
        yield blog

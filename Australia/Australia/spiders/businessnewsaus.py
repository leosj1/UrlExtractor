# -*- coding: utf-8 -*-
import scrapy
import re
from Australia.items import Posts

class BusinessnewsausSpider(scrapy.Spider):
    name = 'businessnewsaus'
    domain = 'businessnewsaus.com.au'
    allowed_domains = ['www.businessnewsaus.com.au']
    start_urls = ['https://www.businessnewsaus.com.au/article/article/index?search=covid-19&perPage=10']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//h2[@class="articleListHeading"]/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
       # next_page = response.css('.bd-paginationitem-6 a').xpath('@href').extract_first()
       # if next_page:
          #  yield scrapy.Request(next_page, self.parse)

        # Getting next page
        count = 1
        while count <= 49:
            count +=1
            next_page = f'https://www.businessnewsaus.com.au/article/article/index/page/{count}/perPage/10/search/covid-19'
            yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h2[@class="articleListHeading"]/a/@title').extract_first()     
        #-Cleaning Post
        yield blog



# -*- coding: utf-8 -*-
import scrapy
import re
from Australia.items import Posts

class A38southSpider(scrapy.Spider):
    name = '38south'
    domain ='38south.com'
    allowed_domains = ['38south.com']
    start_urls = ['http://www.38south.com/']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//h2[@class="entry-title taggedlink"]/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        #next_page = response.xpath('//div[@class="page-nav td-pb-padding-side"]/a/@href').extract_first()
        #if next_page:
            #yield scrapy.Request(next_page, self.parse)
        
         # Getting next page
        count = 1
        while count <=3:
            count +=1
            next_page = f'https://www.38south.com/?paged={count}'
            yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h2[@class="entry-title taggedlink"]/a/text()').extract_first()     
        #-Cleaning Post
        yield blog



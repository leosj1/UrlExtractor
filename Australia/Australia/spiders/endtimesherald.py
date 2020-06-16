# -*- coding: utf-8 -*-
import scrapy
import re
from Australia.items import Posts

class EndtimesheraldSpider(scrapy.Spider):
    name = 'endtimesherald'
    domain = 'endtimesherald.com'
    allowed_domains = ['endtimesherald.com']
    start_urls = ['https://endtimesherald.com/']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//h3[@class="article-title article-title-2"]/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        #next_page = response.xpath('//*[@id="main"]/div/div/div/nav/div/a/@href').extract_first()
        #if next_page:
            #yield scrapy.Request(next_page, self.parse)

        #Getting next page
        count = 1
        while count <= 23:
            count +=1
            next_page = f'https://endtimesherald.com/page/{count}/'
            yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h3[@class="article-title article-title-2"]/a/text()').extract_first()     
        #-Cleaning Post
        yield blog



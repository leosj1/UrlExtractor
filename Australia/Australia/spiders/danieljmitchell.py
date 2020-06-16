# -*- coding: utf-8 -*-
import scrapy
import re
from Australia.items import Posts

class DanieljmitchellSpider(scrapy.Spider):
    name = 'danieljmitchell'
    domain = 'danieljmitchell.wordpress.com'
    allowed_domains = ['danieljmitchell.wordpress.com']
    start_urls = ['https://danieljmitchell.wordpress.com/tag/coronavirus/','https://danieljmitchell.wordpress.com/tag/coronavirus/page/2/','https://danieljmitchell.wordpress.com/tag/coronavirus/page/3/','https://danieljmitchell.wordpress.com/tag/coronavirus/page/4/','https://danieljmitchell.wordpress.com/tag/coronavirus/page/5/','https://danieljmitchell.wordpress.com/tag/coronavirus/page/6/','https://danieljmitchell.wordpress.com/tag/coronavirus/page/7/']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.xpath('//div[@class="posttitle"]/h2/a/@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        #next_page = response.xpath('//div[@id="content-main"]/p/a/@href').extract_first()
        #if next_page:
            #yield scrapy.Request(next_page, self.parse)

        #Getting next page
        #count = 1
        #while count <=7:
            #count +=1
            #next_page = f'https://danieljmitchell.wordpress.com/tag/coronavirus/page/{count}/'
            #yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//div[@class="posttitle"]/h2/a/text()').extract_first()     
        #-Cleaning Post
        yield blog



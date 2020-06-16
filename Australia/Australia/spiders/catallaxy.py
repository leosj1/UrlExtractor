import scrapy
import re
from Australia.items import Posts
class catallaxySpider(scrapy.Spider):
    name = 'catallaxy'
    domain = 'catallaxyfiles.com'
    # current_page = 1
    start_urls = ['https://catallaxyfiles.com/?s=covid-19']
    allowed_domains = ['catallaxyfiles.com']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    # download_delay = 4
    
    
    def parse(self, response):
        #Getting links of required catagories
        for url in response.css('.entry-title a').xpath('@href').extract():
            yield scrapy.Request(url, self.parse_blog)
        
        # Getting next page
        next_page = response.css('.nav-previous a').xpath('@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, self.parse)
    
    
    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.css('.entry-title::text').extract_first()      
        #-Cleaning Post
        yield blog
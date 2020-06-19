# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts

class A21stcenturywireSpider(scrapy.Spider):
    name = '21stcenturywire'
    allowed_domains = ['21stcenturywire.com']
    domain = '21stcenturywire.com'
    start_urls = ['https://21stcenturywire.com/tag/covid-19/']

    def parse(self, response):
        all_urls = response.css('.entry-title-link').xpath('@href').extract()
        for url in all_urls:
            blog = Posts()
            blog['domain'] = self.domain
            blog['url'] = url
            # yield blog
        
        next_page = response.css('.pagination-next a').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)


    

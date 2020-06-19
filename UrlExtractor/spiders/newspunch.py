# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts

class NewspunchSpider(scrapy.Spider):
    name = 'newspunch'
    allowed_domains = ['newspunch.com']
    domain = 'newspunch.com'
    start_urls = ['https://newspunch.com/?s=covid']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

    def parse(self, response):
        all_urls = response.xpath('//*[@id="main-content"]/article/div/header/h3/a/@href').extract()
        for url in all_urls:
            blog = Posts()
            blog['domain'] = self.domain
            blog['url'] = url
            yield blog
        
        next_page = response.css('.next').xpath('@href').extract_first()
        # next_page_icon = response.xpath('//*[@id="main-content"]/div/nav/div/a[3]/text()').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)
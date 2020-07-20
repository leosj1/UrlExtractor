# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import relevant

class NewspunchSpider(scrapy.Spider):
    name = 'newspunch'
    allowed_domains = ['newspunch.com']
    domain = 'newspunch.com'
    start_urls = ['https://newspunch.com/']
    user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

    def parse(self, response):
        all_urls = response.xpath('//*[@id="main-content"]/article/div/header/h3/a/@href').extract()
        for url in all_urls:
            yield scrapy.Request(url, self.parse_blog)
        
        next_page = response.css('.next').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        content = " ".join(response.xpath('//*[contains(@id,"post-")]/div//*[not(self::script)]/text()').extract())
        if relevant(content, use='ausi_covid') or relevant(content, use='ausi_dod'):
            yield blog
            
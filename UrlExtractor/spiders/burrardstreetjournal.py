# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import *

class BurrardstreetjournalSpider(scrapy.Spider):
    name = 'burrardstreetjournal'
    allowed_domains = ['burrardstreetjournal.com']
    domain = 'burrardstreetjournal.com'
    start_urls = ['https://www.burrardstreetjournal.com/?s=corona']

    def parse(self, response):
        all_urls = response.css('.td_module_16 .td-module-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request( url, self.parse_blog)

        next_page = response.css('.last+ a').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        yield blog

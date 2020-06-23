# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import *

class GulagboundSpider(scrapy.Spider):
    name = 'gulagbound'
    allowed_domains = ['gulagbound.com']
    domain = 'gulagbound.com'
    # start_urls = ['http://gulagbound.com/?s=covid/']

    search_keywords = get_keywords()
    start_urls = [f'http://gulagbound.com/?s={search_string}' for search_string in search_keywords]

    def parse(self, response):
        all_urls = response.css('.entry-title-link').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request( url, self.parse_blog)

        next_page = response.css('.pagination-next a').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        # yield blog

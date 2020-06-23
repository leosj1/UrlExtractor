# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import *

class ConsciouslifenewsSpider(scrapy.Spider):
    name = 'consciouslifenews'
    allowed_domains = ['consciouslifenews.com']
    domain = 'consciouslifenews.com'

    search_keywords = get_keywords()
    start_urls = [f'http://consciouslifenews.com/?s={search_string}' for search_string in search_keywords]

    def parse(self, response):
        all_urls = response.css('.post-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request( url, self.parse_blog)

        next_page = response.css('.nextpostslink').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        # yield blog

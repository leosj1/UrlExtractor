# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import *
import urllib

class HangthebankersSpider(scrapy.Spider):
    name = 'hangthebankers'
    allowed_domains = ['hangthebankers.com']
    domain = 'hangthebankers.com'
    # start_urls = ['http://hangthebankers.com/?s=america/']

    search_keywords = get_keywords()
    start_urls = [f"http://hangthebankers.com/?s={urllib.parse.quote(search_string, safe='')}" for search_string in search_keywords]

    def parse(self, response):
        all_urls = response.css('.post-box-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request( url, self.parse_blog)

        next_page = response.css('#tie-next-page a').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        # yield blog

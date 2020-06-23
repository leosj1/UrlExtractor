# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import *
import urllib

class HumansarefreeSpider(scrapy.Spider):
    name = 'humansarefree'
    allowed_domains = ['humansarefree.com']
    domain = 'humansarefree.com'
    # start_urls = ['http://humansarefree.com/?s=america/']

    search_keywords = get_keywords()
    start_urls = [f"http://humansarefree.com/?s={urllib.parse.quote(search_string, safe='')}" for search_string in search_keywords]

    def parse(self, response):
        all_urls = response.css('.image-post-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request( url, self.parse_blog)

        next_page = response.css('.next').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        yield blog

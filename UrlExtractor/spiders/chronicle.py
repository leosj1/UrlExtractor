# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import *

class ChronicleSpider(scrapy.Spider):
    name = 'chronicle'
    allowed_domains = ['chronicle.su']
    domain = 'chronicle.su'
    # search_string = 'australia'
    search_keywords = get_keywords()
    start_urls = [f'https://chronicle.su/?s={search_string}' for search_string in search_keywords]
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

    def parse(self, response):
        all_urls = response.css('.entry-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request( url, self.parse_blog)

        next_page = response.css('.next').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        # yield blog

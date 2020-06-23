# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts

class AntiwarSpider(scrapy.Spider):
    name = 'antiwar'
    allowed_domains = ['antiwar.com']
    domain = 'antiwar.com'
    search_string = 'australia'
    start_urls = [f'https://www.antiwar.com/blog/?s={search_string}']

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
        # blog['title'] = None     
        # blog['author'] = None
        # blog['published_date'] = None
        # blog['content'] = "None"
        # blog['content_html'] = None
        # blog['links'] = None
        # blog['tags'] = None
        # yield blog

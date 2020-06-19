# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts

class Clipper28Spider(scrapy.Spider):
    name = 'clipper28'
    allowed_domains = ['www.clipper28.com']
    domain = 'www.clipper28.com'
    start_urls = ['http://www.clipper28.com/']

    def parse(self, response):
        all_urls = response.css('.entry-title-link').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request(url, self.parse_blog)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.xpath('//*[contains(@id,"post-body-")]/a/@href').extract()
        # blog['title'] = None     
        # blog['author'] = None
        # blog['published_date'] = None
        # blog['content'] = "None"
        # blog['content_html'] = None
        # blog['links'] = None
        # blog['tags'] = None
        yield blog

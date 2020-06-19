# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts


class UtopiayouarestandinginitSpider(scrapy.Spider):
    name = 'utopiayouarestandinginit'
    allowed_domains = ['utopiayouarestandinginit.com']
    domain = 'utopiayouarestandinginit.com'
    start_urls = ['https://utopiayouarestandinginit.com/?s=covid-19', 'https://utopiayouarestandinginit.com/?s=coronavirus']

    def parse(self, response):
        all_urls = response.css('.post-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request(url, self.parse_blog)

        next_page = response.xpath('//*[@id="content"]/p/span[1]/a/@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.css('.post-title a::text').extract_first()     
        # blog['author'] = None
        # blog['published_date'] = None
        # blog['content'] = "None"
        # blog['content_html'] = None
        # blog['links'] = None
        # blog['tags'] = None
        yield blog

# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts

class WorldhealthSpider(scrapy.Spider):
    name = 'worldhealth'
    allowed_domains = ['worldhealth.net']
    domain = 'worldhealth.net'
    search_string = 'covid-19'
    start_urls = [f'https://www.worldhealth.net/search/?q={search_string}/']
    page_number = 2

    def parse(self, response):
        all_urls = response.css('.titleItem a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request('https://www.worldhealth.net'+ url, self.parse_blog)

        next_page = f"https://www.worldhealth.net/search/?q={self.search_string}&page={str(self.page_number)}&count=4&order=popular"
        self.page_number+=1
        yield scrapy.Request(next_page, self.parse)

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
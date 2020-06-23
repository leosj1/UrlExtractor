# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import relevant

class BurrardstreetjournalSpider(scrapy.Spider):
    name = 'burrardstreetjournal'
    allowed_domains = ['burrardstreetjournal.com']
    domain = 'burrardstreetjournal.com'
    start_urls = ['https://www.burrardstreetjournal.com']

    def parse(self, response):
        all_categories = response.css('#menu-main-menu-1 a').xpath('@href').extract()
        if response.url == 'https://www.burrardstreetjournal.com':
            for link in all_categories:
                yield scrapy.Request(link)

        all_urls = response.css('.td-module-title a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request(url, self.parse_blog)

        next_page = response.css('.last+ a').xpath('@href').extract_first()
        if next_page: yield scrapy.Request(next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        content = " ".join(response.css('.td-post-content').xpath('//text()').extract()).replace('\n','').replace('\t','').replace('\r','')
        if relevant(content, use='ausi_covid') or relevant(content, use='ausi_dod'):
            yield blog

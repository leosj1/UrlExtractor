# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts


class UnzSpider(scrapy.Spider):
    name = 'unz'
    allowed_domains = ['unz.com']
    domain = 'unz.com'
    start_urls = ['https://www.unz.com/?s=covid-19&Action=Search&ptype=all&paged=1']
    # next_page = 2

    def parse(self, response):
        all_urls = response.xpath('//*[@id="wrap-content"]/div/div[1]/a/@href').extract()
        for url in all_urls:
            blog = Posts()
            blog['domain'] = self.domain
            blog['url'] = 'https://www.unz.com' + url
            yield blog
            # yield scrapy.Request(url, self.parse_blog)

        page_number = response.url.split('paged=')[-1]
        next_page = f"{''.join(response.url.split('paged=')[:-1])}paged={int(page_number) + 1}"
        if next_page: yield scrapy.Request(next_page, self.parse)


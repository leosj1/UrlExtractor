# -*- coding: utf-8 -*-
import scrapy
from UrlExtractor.items import Posts
from UrlExtractor.utils import relevant

class UnzSpider(scrapy.Spider):
    name = 'unz'
    allowed_domains = ['unz.com']
    domain = 'unz.com'
    
    # start_urls = ['https://www.unz.com/?s=covid-19&Action=Search&ptype=all&paged=1']
    start_urls = ['https://www.unz.com/']

    def parse(self, response):
        all_categories = response.xpath('//*[@id="topmenu-holder"]/div/ul[1]/div/li/a/@href').extract()
        if response.url == 'https://www.unz.com/':
            for link in all_categories:
                if link != '/' and link != '/masthead/':
                    if 'tcategory' in link:
                        link = link.replace('tcategory', 'category')
                        yield scrapy.Request('https://www.unz.com' + link)

        all_urls = response.css('#contents-holder .head a').xpath('@href').extract()
        for url in all_urls:
            yield scrapy.Request('https://www.unz.com' + url, self.parse_blog)
        
        next_page = response.css('.leftside a').xpath('@href').extract_first()
        if next_page: yield scrapy.Request('https://www.unz.com' + next_page, self.parse)

    def parse_blog(self, response):
        # Posts
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        content = " ".join(response.xpath('//*[@id="contents-holder"]//text()').extract()).replace('\n','').replace('\t','').replace('\r','')
        if relevant(content, use='ausi_covid') or relevant(content, use='ausi_dod'):
            yield blog

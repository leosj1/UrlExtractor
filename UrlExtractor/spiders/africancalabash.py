# -*- coding: utf-8 -*-
import scrapy

from UrlExtractor.items import Posts
from UrlExtractor.utils import relevant

class AfricancalabashSpider(scrapy.Spider):
    name = 'africancalabash'
    domain = 'africancalabash.wordpress.com'
    allowed_domains = ['africancalabash.wordpress.com']
    start_urls = ['https://africancalabash.wordpress.com/']

    def parse(self, response):
        #Parsing blogs
        posts = response.xpath('//h1[@class="entry-title"]/a/@href').getall()
        for post in posts:
            yield scrapy.Request(post, self.parse_blog)

        #Getting catagories
        cats = response.xpath('//aside[@class="widget widget_archive"]/ul/li/a/@href').getall()
        for cat in cats:
            yield scrapy.Request(cat)


    def parse_blog(self, response):
        # Post
        blog = Posts()
        blog['domain'] = self.domain
        blog['url'] = response.url
        blog['title'] = response.xpath('//h1[@class="entry-title"]/text()').get()  
        content = " ".join(response.xpath('//div[@class="entry-content"]//text()').getall())
        if relevant(content, use='ausi_covid') or relevant(content, use='ausi_dod'):
            yield blog

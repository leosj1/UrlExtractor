# -*- coding: utf-8 -*-
import scrapy
import json
import urllib
from UrlExtractor.items import Posts
from UrlExtractor.utils import *

class AustralianPoliticsSpider(scrapy.Spider):
    name = 'australianpolitics'
    allowed_domains = ['australian-politics.blogspot.com']
    domain = 'australian-politics.blogspot.com'
    start_urls = ['https://australian-politics.blogspot.com/']
    DOWNLOAD_DELAY = 30
    CONCURRENT_REQUESTS = 1
    ROBOTSTXT_OBEY = True
    # user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

    def parse(self, response):
        all_urls = response.xpath('//*[@id="BlogArchive1_ArchiveList"]/ul/li/a[2]/@href').extract()
        for url in all_urls:
            feed_url = urllib.parse.quote(url, safe='') 
            year_url = f'https://australian-politics.blogspot.com/?action=getTitles&widgetId=BlogArchive1&widgetType=BlogArchive&responseType=js&path={feed_url}&xssi_token=AOuZoY5j-tWUcaNFdab7rj29aMU8av5SZg%3A1592494684753'
            yield scrapy.Request(year_url, self.parse_blog)
        
        # next_page = response.xpath('//*[@id="Blog1_blog-pager-older-link"]/@href').extract_first()
        # if next_page: yield scrapy.Request(next_page, self.parse)
        
    def parse_blog(self, response):
        links = find_arry(response.xpath("//*[contains(., 'posts')]/text()").extract_first())
        for arr in links:
            for link in arr:
                blog = Posts()
                blog['domain'] = self.domain
                blog['url'] = link['url']
                
                yield scrapy.Request(link['url'], self.parse_blog_2)

    def parse_blog_2(self, response):
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

        

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from UrlExtractor.diffbot import diff_get_article
from sql import  get_connection

class UrlExtractorPipeline(object):

    def process_item(self, item, spider):
        force_diff = False
        if force_diff: diff_get_article(item['url'])
        else:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts where url = %s;", item['url'])
                record = cursor.fetchall()
            if not record:
                diff_get_article(item['url'])
            connection.close()
        return item





# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from UrlExtractor.diffbot import diff_get_article
from sql import  get_connection
import csv
import os

class UrlExtractorPipeline(object):

    def process_item(self, item, spider):
        #AnyPosts
        if 'crawl_diffbot' in item:
            if item['crawl_diffbot']:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM posts where url = %s;", item['url'])
                    record = cursor.fetchall()
                if not record:
                    diff_get_article(item['url'])
                connection.close()
            if item['file_name']:
                fpath = os.path.join(os.getcwd()[:-13], "Export\\" + item['file_name']) + '.csv'
                mode = 'a' if os.path.exists(fpath) else 'w'
                data = {"domain": item['domain'], 'url':item['url']}
                #Only append new rows...
                new = True
                if mode == 'a':
                    with open(fpath, 'r') as r:
                        csv_reader = csv.DictReader(r)
                        for row in csv_reader:
                            if row == data: new = False
                if new: 
                    with open(fpath, mode, newline='') as f: 
                        w = csv.DictWriter(f, fieldnames=['domain', 'url'])
                        if mode == 'w': w.writeheader()
                        w.writerow(data)

        #Posts
        else: 
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





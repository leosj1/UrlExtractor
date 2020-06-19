# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Posts(scrapy.Item):
    domain = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
   
    

    #modifying the print output
    def __repr__(self):
        """only print out attr1 after exiting the Pipeline"""
        return repr({"Blog URL": self._values['url']})
 

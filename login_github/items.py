# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import json
import codecs

class LoginGithubItem(scrapy.Item):

    # define the fields for your item here like:
    #先不考虑去重
    full_name = scrapy.Field()
    additional_name = scrapy.Field()


# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Chapter(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    chapter = scrapy.Field()
    text = scrapy.Field()
    index = scrapy.Field()
    last = scrapy.Field()


class NovelInfo(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    novel_dir = scrapy.Field()

    last_index = scrapy.Field()
    last_files = scrapy.Field()

# -*- coding: utf-8 -*-
import os
import json

import scrapy
import time
from crawler.common import get_status_file, get_url_id
from crawler.items import Chapter, NovelInfo


class CzbooksSpider(scrapy.Spider):
    name = 'czbooks'
    allowed_domains = ['czbooks.net']
    root = 'https://czbooks.net/'

    def start_requests(self):
        url = getattr(self, 'url', None)
        if url:
            yield scrapy.Request(url, self.parse_novel)
        else:
            yield scrapy.Request(self.root, self.parse_homepage)

    def parse_homepage(self, response):
        self.logger.info("Processing homepage {}".format(response.request.url))

        # selector = 'body > div.header > div > ul.nav.menu > li > a::attr("href")'
        # for category in response.css(selector):
        #     url = 'https:' + category.extract() + '/total'
        #     yield scrapy.Request(url, self.parse_category)

        selector = ('body > div.main > div > ul:nth-child(1) > li > '
                    'div.novel-item > div.novel-item-info-wrapper > '
                    'div.novel-item-title > a::attr("href")')
        for category in response.css(selector):
            url = 'https:' + category.extract()
            yield scrapy.Request(url, self.parse_novel)

    def parse_category(self, response):
        self.logger.info("Processing category {}".format(response.request.url))

        selector = ('body > div.main > div > ul.nav.novel-list.style-default '
                    '> li> div > div.novel-item-cover-wrapper > a::attr("href")')
        for novel in response.css(selector):
            url = 'https:' + novel.extract()
            yield scrapy.Request(url, self.parse_novel)

    def parse_novel(self, response):
        self.logger.info("Processing novel {}".format(response.request.url))

        last_status = self.load_status(response.request.url)
        if last_status:
            last = last_status.get('last_index')
        else:
            title = response.css('span.title::text').get()
            author = response.css('span.author::text').get()
            image = response.css("div.thumbnail > img::attr('src')").get()
            yield NovelInfo(
                url=response.request.url,
                title=title,
                author=author,
                image_urls=[image],
            )
            last = -1

        found = False
        index = 0
        for href in response.css('.nav.chapter-list').css("li a::attr('href')"):
            url = 'https:' + href.extract()
            if index > last:
                yield scrapy.Request(
                    url,
                    self.parse_page,
                    meta={'index': index, 'url': response.request.url},
                )

            index += 1

    def parse_page(self, response):
        self.logger.info("Processing chapter {}".format(response.request.url))

        text = [t.strip("'").strip() for t in response.css('div.content::text').getall()]
        chapter = response.css('div.name::text').getall()[0].strip()
        yield Chapter(
            url=response.meta['url'],
            chapter=chapter,
            text=text,
            index=response.meta['index'],
        )

    def load_status(self, url):
        status_file = get_status_file(url)

        if os.path.isfile(status_file):
            with open(status_file, 'r') as fd:
                status = json.load(fd)
            return NovelInfo(
                url=status.get('url', ""),
                last_index=status.get('last_index', -1),
            )

        return None

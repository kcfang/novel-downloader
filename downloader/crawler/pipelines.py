# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline

from crawler.common import get_novel_dir, get_status_file
from crawler import settings
from crawler.items import Chapter, NovelInfo


class ChapterPipeline(object):
    def process_item(self, item, spider):
        if not isinstance(item, Chapter):
            return item

        f = os.path.join(get_novel_dir(item['url']), '{}.json'.format(item['index']))
        with open(f, 'w') as fd:
            json.dump(dict(item), fd)
        return item



class NovelInfoUpdater(object):
    def process_item(self, item, spider):
        if not isinstance(item, NovelInfo):
            return item

        f = get_status_file(item['url'])
        orig = {}
        if os.path.isfile(f):
            with open(f, 'r') as fd:
                orig = json.load(fd)

        orig.update(dict(item))
        orig['novel_dir'] = get_novel_dir(item['url'])
        with open(f, 'w') as fd:
            json.dump(orig, fd)

        return item

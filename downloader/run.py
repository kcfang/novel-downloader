#!/usr/bin/env python

import sys
import os
import json
import glob
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


from crawler.spiders.czbooks import CzbooksSpider
from crawler.common import get_status_file, get_result_dir
from crawler import settings
from txt import TxtGenerator
from mobi import MobiGenerator


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=None, help="Parse given url.")
    parser.add_argument("--all", action='store_true', help="Parse popular novel.")
    return parser.parse_args()


def generate_book(url):
    status_file = get_status_file(url)
    with open(status_file, 'r') as fd:
        status = json.load(fd)

    novel_dir = status['novel_dir']
    files = sorted(os.listdir(novel_dir), key=lambda x: int(x.split('.')[0]))
    last_index = int(files[-1].split('.')[0])

    if last_index == int(status.get('last_index', 0)):
        print("No new chapter for novel {}".format(url))
        return

    for f in status.get('last_files', []):
        if os.path.isfile(f):
            print("New chapter updated, remove last file {}".format(f))
            os.remove(f)

    gs = [
        TxtGenerator(status),
        MobiGenerator(status)
    ]
    last_files = [g.process(files) for g in gs]

    status['last_files'] = last_files
    status['last_index'] = last_index
    status['result_dir'] = get_result_dir(status['title'], status['author'])
    with open(status_file, 'w') as fd:
        json.dump(status, fd)

    return status


def run_crawler(url):
    process = CrawlerProcess(get_project_settings())
    process.crawl(CzbooksSpider, url=url)
    process.start()


def main():
    args = parse_args()

    run_crawler(args.url)

    if args.url:
        generate_book(args.url)
        return

    if args.all:
        for info in glob.glob(os.path.join(settings.NOVEL_STATUS, '*.json')):
            with open(info, 'r') as fd:
                url = json.load(fd)['url']
            generate_book(url)
        return


if __name__ == "__main__":
    main()

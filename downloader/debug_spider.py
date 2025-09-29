#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug script for testing Scrapy spiders with Cloudflare bypass
"""

import sys
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.czbooks import CzbooksSpider

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def run_spider(url=None):
    """Run the spider with the given URL"""
    settings = get_project_settings()
    
    # Create a crawler process
    process = CrawlerProcess(settings)
    
    # Start the spider
    if url:
        process.crawl(CzbooksSpider, url=url)
    else:
        process.crawl(CzbooksSpider)
    
    # Run the spider
    process.start()

if __name__ == "__main__":
    # Get the URL from command line arguments
    url = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the spider
    run_spider(url)

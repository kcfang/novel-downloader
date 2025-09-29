# -*- coding: utf-8 -*-
import logging
import cloudscraper
from scrapy.http import HtmlResponse

class CloudflareMiddleware:
    """Middleware to bypass Cloudflare protection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Create a cloudscraper session
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            },
            delay=10  # Add a delay to avoid detection
        )
    
    def process_request(self, request, spider):
        """Process the request using cloudscraper if needed"""
        # Only use cloudscraper for czbooks domain
        if 'czbooks' in request.url:
            self.logger.debug(f"Using cloudscraper for: {request.url}")
            try:
                # Get the URL using cloudscraper
                response = self.scraper.get(
                    request.url,
                    headers=dict(request.headers),
                    cookies=request.cookies,
                    allow_redirects=True
                )
                
                # Log the response status
                self.logger.debug(f"Cloudscraper response status: {response.status_code}")
                
                # Create a HtmlResponse from the cloudscraper response
                return HtmlResponse(
                    url=request.url,
                    status=response.status_code,
                    headers=response.headers,
                    body=response.content,
                    encoding='utf-8',
                    request=request
                )
            except Exception as e:
                self.logger.error(f"Cloudscraper error: {str(e)}")
                
        # For other domains, use the default Scrapy downloader
        return None

# -*- coding: utf-8 -*-
import logging
import json
from scrapy.http import HtmlResponse

class DebugMiddleware:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        self.logger.debug(f"Outgoing request to: {request.url}")
        self.logger.debug(f"Request headers: {request.headers}")
        return None

    def process_response(self, request, response, spider):
        self.logger.debug(f"Response from {response.url}: Status {response.status}")
        
        # Log first 500 characters of the response body for debugging
        body_preview = response.body.decode('utf-8', errors='replace')[:500]
        self.logger.debug(f"Response body preview: {body_preview}")
        
        # Check for Cloudflare protection
        if response.status == 403 or "Just a moment" in body_preview:
            self.logger.warning(f"Detected Cloudflare protection at {response.url}")
            
        return response

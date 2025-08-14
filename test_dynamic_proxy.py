#!/usr/bin/env python3
"""
Test dynamic scraper with Webshare proxies
"""
from scraper import scrape_dynamic_content
from proxy_manager import ProxyManager
import os

# Load environment
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('WEBSHARE_API_KEY='):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("Testing dynamic scraper with Webshare proxies...")
print("-" * 50)

# Initialize proxy manager
manager = ProxyManager()
manager.fetch_proxies_from_webshare()

# Get a proxy
proxy = manager.get_next_proxy()
print(f"Using proxy session: {proxy['session_id']}")

# Test dynamic scraping with proxy
url = "http://httpbin.org/ip"
print(f"\nScraping {url} with dynamic method + proxy...")

result = scrape_dynamic_content(url, proxy=proxy)

if "Error" in result:
    print(f"❌ Failed: {result}")
else:
    print(f"✅ Success! Got {len(result)} characters")
    print(f"Content: {result}")
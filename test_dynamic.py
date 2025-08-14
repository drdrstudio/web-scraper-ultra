#!/usr/bin/env python3
"""
Test dynamic scraper with Chrome
"""
from scraper import scrape_dynamic_content

print("Testing dynamic scraper...")
print("-" * 40)

# Test without proxy first
url = "https://example.com"
print(f"Scraping {url} with dynamic method...")

result = scrape_dynamic_content(url, proxy=None)

if "Error" in result:
    print(f"❌ Failed: {result}")
else:
    print(f"✅ Success! Got {len(result)} characters")
    print(f"Preview: {result[:200]}...")
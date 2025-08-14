#!/usr/bin/env python3
"""
Test scraper WITHOUT proxies to verify basic functionality
"""
from scraper import scrape_static_content, scrape_dynamic_content

# Test URLs
test_urls = [
    "https://httpbin.org/html",  # Simple HTML page
    "https://example.com",        # Basic website
]

print("=" * 60)
print("TESTING SCRAPER WITHOUT PROXIES")
print("=" * 60)

for url in test_urls:
    print(f"\n📍 Testing: {url}")
    print("-" * 40)
    
    # Test static scraping
    print("Static scraping...")
    try:
        content = scrape_static_content(url, proxy=None)
        if content:
            print(f"✅ Success! Got {len(content)} characters")
            print(f"Preview: {content[:200]}...")
        else:
            print("❌ No content returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

# Test dynamic scraping on a simple page
print("\n📍 Testing dynamic scraping on example.com")
print("-" * 40)
try:
    content = scrape_dynamic_content("https://example.com", proxy=None)
    if content:
        print(f"✅ Success! Got {len(content)} characters")
        print(f"Preview: {content[:200]}...")
    else:
        print("❌ No content returned")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
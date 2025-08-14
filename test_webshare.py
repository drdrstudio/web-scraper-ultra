#!/usr/bin/env python3
"""
Test Webshare.io connection and fetch proxies
"""
import os
from proxy_manager import ProxyManager
import json

# Load .env file
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('WEBSHARE_API_KEY='):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                print(f"✓ Loaded API key from .env: {value[:10]}...")

# Create proxy manager
manager = ProxyManager()

print("\n🔄 Fetching proxies from Webshare.io...")
proxies = manager.fetch_proxies_from_webshare()

if proxies:
    print(f"\n✅ Successfully fetched {len(proxies)} proxies!")
    
    # Show proxy details
    print("\n📍 Proxy Locations:")
    countries = {}
    for proxy in proxies[:10]:  # Show first 10
        country = proxy.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
        print(f"  • {proxy['address']}:{proxy['port']} ({country})")
    
    # Save to file
    with open('proxies.json', 'w') as f:
        json.dump(proxies, f, indent=2)
    print(f"\n💾 Saved {len(proxies)} proxies to proxies.json")
    
    # Test a proxy
    print("\n🧪 Testing first proxy...")
    if manager.test_proxy(proxies[0]):
        print("✅ Proxy test successful!")
    else:
        print("⚠️ Proxy test failed (might be temporary)")
        
else:
    print("\n❌ Failed to fetch proxies")
    print("Please check your API key or network connection")
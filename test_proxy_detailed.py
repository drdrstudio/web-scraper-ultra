#!/usr/bin/env python3
"""
Detailed proxy testing to diagnose connection issues
"""
import requests
import json
from proxy_manager import ProxyManager

# Load proxies
manager = ProxyManager()
manager.load_proxies_from_file('proxies.json')

print(f"Loaded {len(manager.proxies)} proxies")
print("\n" + "=" * 60)

# Test first 5 proxies with different methods
test_sites = [
    "http://httpbin.org/ip",
    "http://icanhazip.com",
    "http://checkip.amazonaws.com",
]

tested = 0
working = 0

for i, proxy in enumerate(manager.proxies[:10]):
    print(f"\n🔍 Testing proxy {i+1}: {proxy['address']}:{proxy['port']} ({proxy['country']})")
    print(f"   Username: {proxy['username']}")
    print(f"   Valid status: {proxy.get('valid', 'Unknown')}")
    
    # Build proxy dict
    proxy_dict = {
        'http': proxy['url'],
        'https': proxy['url']
    }
    
    # Test against different sites
    for site in test_sites:
        try:
            print(f"   Testing {site}...", end="")
            response = requests.get(
                site,
                proxies=proxy_dict,
                timeout=5,  # Shorter timeout
                verify=False  # Skip SSL verification
            )
            if response.status_code == 200:
                print(f" ✅ Success! Response: {response.text.strip()[:50]}")
                working += 1
                break
            else:
                print(f" ❌ Status: {response.status_code}")
        except requests.exceptions.ProxyError as e:
            print(f" ❌ ProxyError: Unable to connect")
        except requests.exceptions.ConnectTimeout:
            print(f" ❌ Timeout after 5 seconds")
        except requests.exceptions.ConnectionError as e:
            print(f" ❌ ConnectionError")
        except Exception as e:
            print(f" ❌ {type(e).__name__}")
    
    tested += 1

print("\n" + "=" * 60)
print(f"Results: {working}/{tested} proxies working")
print("=" * 60)

# Try a direct request without proxy to confirm network is OK
print("\n🌐 Testing direct connection (no proxy)...")
try:
    response = requests.get("http://httpbin.org/ip", timeout=5)
    print(f"✅ Direct connection works! Your IP: {response.json()['origin']}")
except Exception as e:
    print(f"❌ Direct connection failed: {e}")
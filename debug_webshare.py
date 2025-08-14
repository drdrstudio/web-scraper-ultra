#!/usr/bin/env python3
"""
Debug Webshare.io API connection
"""
import requests
import os

# Load API key
api_key = "hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms"

print(f"API Key: {api_key[:10]}...")
print("\nTrying different Webshare endpoints:\n")

# Test different endpoints
endpoints = [
    "https://proxy.webshare.io/api/v2/proxy/list/",
    "https://proxy.webshare.io/api/proxy/list/",
    "https://proxy.webshare.io/api/v2/proxy/list/download/",
]

headers = {
    "Authorization": f"Token {api_key}"
}

for endpoint in endpoints:
    print(f"Testing: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                print(f"  ✓ Found {len(data['results'])} proxies")
            elif isinstance(data, list):
                print(f"  ✓ Found {len(data)} proxies")
            else:
                print(f"  Response: {str(data)[:100]}...")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")
    print()

# Also try with Bearer instead of Token
print("\nTrying with Bearer auth:")
headers_bearer = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get("https://proxy.webshare.io/api/v2/proxy/list/", headers=headers_bearer, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Response: {response.text[:200]}")
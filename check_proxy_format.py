#!/usr/bin/env python3
"""
Check the exact proxy format from Webshare
"""
import json

# Load saved proxies
with open('proxies.json', 'r') as f:
    proxies = json.load(f)

print(f"Total proxies: {len(proxies)}")
print("\nFirst proxy details:")
print(json.dumps(proxies[0], indent=2))

# Check the URL format
proxy = proxies[0]
print(f"\nProxy URL format: {proxy['url']}")
print(f"Does it have username? {'username' in proxy}")
print(f"Does it have password? {'password' in proxy}")

# Check if credentials are empty
if proxy.get('username'):
    print(f"Username length: {len(proxy['username'])}")
if proxy.get('password'):
    print(f"Password length: {len(proxy['password'])}")
#!/usr/bin/env python3
"""
Check Webshare configuration and get proxy details
"""
import requests

api_key = "hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms"
headers = {"Authorization": f"Token {api_key}"}

# Get account info
print("📊 Getting account info...")
response = requests.get(
    "https://proxy.webshare.io/api/subscription/",
    headers=headers
)
if response.status_code == 200:
    data = response.json()
    print(f"Subscription: {data.get('type', 'Unknown')}")
    print(f"Active: {data.get('is_active', False)}")
    print(f"Bandwidth: {data.get('bandwidth_limit', 'Unknown')}")
else:
    print(f"Error: {response.status_code}")

# Get proxy config
print("\n🔧 Getting proxy configuration...")
response = requests.get(
    "https://proxy.webshare.io/api/proxy/config/",
    headers=headers
)
if response.status_code == 200:
    config = response.json()
    print(f"Config: {config}")
else:
    print(f"Error: {response.status_code}")

# Get backbone/server info
print("\n🌐 Getting backbone servers...")
response = requests.get(
    "https://proxy.webshare.io/api/proxy/backbone/",
    headers=headers
)
if response.status_code == 200:
    servers = response.json()
    if servers.get('results'):
        print(f"Found {len(servers['results'])} backbone servers")
        for server in servers['results'][:3]:
            print(f"  - {server}")
else:
    print(f"Error: {response.status_code}")

# Check if we should use different proxy format
print("\n📝 Checking proxy list with auth included...")
response = requests.get(
    "https://proxy.webshare.io/api/proxy/list/",
    headers=headers,
    params={"page_size": 1}
)
if response.status_code == 200:
    data = response.json()
    if data.get('results'):
        proxy = data['results'][0]
        print(f"\nProxy details from API:")
        print(f"  Address: {proxy.get('proxy_address')}")
        print(f"  Username: {proxy.get('username')}")
        print(f"  Ports: {proxy.get('ports')}")
        print(f"  Valid: {proxy.get('valid')}")
        print(f"  Country: {proxy.get('country_code')}")
        
        # Check for backbone connection
        if proxy.get('backbone_address'):
            print(f"  ⚠️ Backbone address: {proxy['backbone_address']}")
            print("  Note: Should connect via backbone!")
else:
    print(f"Error: {response.status_code}")
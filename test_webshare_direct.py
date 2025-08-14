#!/usr/bin/env python3
"""
Test Webshare proxies directly with their recommended approach
"""
import requests
from requests.auth import HTTPProxyAuth

# Get first proxy from our list
import json
with open('proxies.json', 'r') as f:
    proxies = json.load(f)

proxy = proxies[0]
print(f"Testing proxy: {proxy['address']}:{proxy['port']}")
print(f"Username: {proxy['username']}")
print(f"Country: {proxy['country']}")

# Method 1: URL with embedded auth (what we've been trying)
proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['address']}:{proxy['port']}"
proxies_dict = {
    'http': proxy_url,
    'https': proxy_url
}

print("\n1️⃣ Testing with embedded auth in URL...")
try:
    response = requests.get(
        'http://httpbin.org/ip',
        proxies=proxies_dict,
        timeout=10
    )
    print(f"✅ Success! IP: {response.json()['origin']}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Method 2: Using HTTPProxyAuth (alternative approach)
print("\n2️⃣ Testing with HTTPProxyAuth...")
proxy_without_auth = f"http://{proxy['address']}:{proxy['port']}"
proxies_dict2 = {
    'http': proxy_without_auth,
    'https': proxy_without_auth
}
auth = HTTPProxyAuth(proxy['username'], proxy['password'])

try:
    response = requests.get(
        'http://httpbin.org/ip',
        proxies=proxies_dict2,
        auth=auth,
        timeout=10
    )
    print(f"✅ Success! IP: {response.json()['origin']}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Method 3: Test without auth to see error
print("\n3️⃣ Testing without auth (should fail with 407)...")
try:
    response = requests.get(
        'http://httpbin.org/ip',
        proxies={'http': f"http://{proxy['address']}:{proxy['port']}"},
        timeout=10
    )
    print(f"Unexpected success! Status: {response.status_code}")
except requests.exceptions.ProxyError as e:
    if "407" in str(e):
        print("✅ Got expected 407 auth required - proxy is responding!")
    else:
        print(f"❌ ProxyError: {e}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Method 4: Direct connection test
print("\n4️⃣ Testing direct connection to proxy...")
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((proxy['address'], proxy['port']))
    sock.close()
    if result == 0:
        print(f"✅ Port {proxy['port']} is open on {proxy['address']}")
    else:
        print(f"❌ Cannot connect to {proxy['address']}:{proxy['port']}")
except Exception as e:
    print(f"❌ Socket error: {e}")
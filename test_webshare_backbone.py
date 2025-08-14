#!/usr/bin/env python3
"""
Test Webshare.io backbone proxy connection
According to Webshare docs, residential proxies use:
- Backbone server: p.webshare.io
- Port: specific port per proxy
- Auth: username and password
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_backbone_proxy():
    """Test Webshare backbone proxy"""
    
    # Get API key
    api_key = os.getenv('WEBSHARE_API_KEY')
    headers = {'Authorization': f'Token {api_key}'}
    
    print("Fetching proxy list...")
    proxy_url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=backbone&page=1&page_size=1'
    response = requests.get(proxy_url, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"Failed to fetch proxies: {response.status_code}")
        return False
    
    data = response.json()
    proxy_data = data['results'][0]
    
    print(f"\nProxy details:")
    print(f"  Username: {proxy_data['username']}")
    print(f"  Password: {proxy_data['password'][:10]}...")
    print(f"  Port: {proxy_data['port']}")
    print(f"  Country: {proxy_data['country_code']}")
    
    # Backbone server is p.webshare.io for residential proxies
    backbone_server = "p.webshare.io"
    
    # Build proxy URL for backbone mode
    proxy_url = f"http://{proxy_data['username']}:{proxy_data['password']}@{backbone_server}:{proxy_data['port']}"
    
    print(f"\nTesting connection through backbone server: {backbone_server}:{proxy_data['port']}")
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    # Test 1: Check IP
    print("\nTest 1: Checking IP through proxy...")
    try:
        response = requests.get(
            'http://ipinfo.io/json',
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ SUCCESS! Connected through proxy")
            print(f"   Proxy IP: {ip_info.get('ip')}")
            print(f"   Location: {ip_info.get('city')}, {ip_info.get('country')}")
            print(f"   ISP: {ip_info.get('org', 'Unknown')}")
            
            # Compare with expected country
            if ip_info.get('country') == proxy_data['country_code']:
                print(f"   ✅ Country matches: {proxy_data['country_code']}")
            else:
                print(f"   ⚠️ Country mismatch: Expected {proxy_data['country_code']}, got {ip_info.get('country')}")
            
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ProxyError as e:
        print(f"❌ Proxy connection failed:")
        print(f"   {str(e)[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)[:200]}")
        return False

def test_multiple_requests():
    """Test multiple requests through same proxy"""
    
    api_key = os.getenv('WEBSHARE_API_KEY')
    headers = {'Authorization': f'Token {api_key}'}
    
    # Get a proxy
    response = requests.get(
        'https://proxy.webshare.io/api/v2/proxy/list/?mode=backbone&page=1&page_size=1',
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        return False
    
    proxy_data = response.json()['results'][0]
    backbone_server = "p.webshare.io"
    proxy_url = f"http://{proxy_data['username']}:{proxy_data['password']}@{backbone_server}:{proxy_data['port']}"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print("\nTest 2: Multiple requests through same proxy...")
    
    test_urls = [
        'http://httpbin.org/ip',
        'http://httpbin.org/headers',
        'https://api.ipify.org?format=json'
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n   Request {i}: {url}")
        try:
            response = requests.get(url, proxies=proxies, timeout=15)
            if response.status_code == 200:
                print(f"   ✅ Success")
                if 'json' in response.headers.get('content-type', ''):
                    print(f"   Response: {response.json()}")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    return True

def main():
    print("="*60)
    print("WEBSHARE BACKBONE PROXY TEST")
    print("="*60)
    
    # Test 1: Basic connection
    connection_ok = test_backbone_proxy()
    
    if connection_ok:
        # Test 2: Multiple requests
        test_multiple_requests()
    
    print("\n" + "="*60)
    if connection_ok:
        print("✅ Webshare backbone proxy WORKING!")
        print("\nProxy configuration:")
        print("  Server: p.webshare.io")
        print("  Port: [unique per proxy]")
        print("  Auth: username:password")
    else:
        print("❌ Proxy connection failed")
    print("="*60)
    
    return 0 if connection_ok else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
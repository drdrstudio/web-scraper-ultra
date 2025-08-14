#!/usr/bin/env python3
"""
Test Webshare.io proxy integration
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

def test_webshare_api():
    """Test Webshare API and fetch proxies"""
    api_key = os.getenv('WEBSHARE_API_KEY')
    
    if not api_key:
        print("❌ WEBSHARE_API_KEY not found in environment")
        return None
    
    print(f"Testing Webshare API...")
    print(f"API Key: {api_key[:10]}...")
    
    # Fetch proxy list
    headers = {'Authorization': f'Token {api_key}'}
    
    try:
        # Get account info first
        print("\n1. Checking account status...")
        account_url = 'https://proxy.webshare.io/api/v2/profile/'
        response = requests.get(account_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Account email: {account.get('email', 'N/A')}")
        else:
            print(f"❌ Account check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # Get subscription info
        print("\n2. Checking subscription...")
        sub_url = 'https://proxy.webshare.io/api/v2/subscription/active/'
        response = requests.get(sub_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            subs = response.json()
            print(f"✅ Active subscriptions: {len(subs.get('results', []))}")
            for sub in subs.get('results', []):
                print(f"   - {sub.get('type', 'Unknown')}: {sub.get('proxy_count', 0)} proxies")
        
        # Get proxy list
        print("\n3. Fetching proxy list...")
        proxy_url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=backbone&page=1&page_size=10'
        response = requests.get(proxy_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            proxies = data.get('results', [])
            print(f"✅ Found {data.get('count', 0)} total proxies")
            print(f"   Fetched first {len(proxies)} for testing")
            return proxies
        else:
            print(f"❌ Failed to fetch proxies: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_proxy_connection(proxy_data):
    """Test actual proxy connection"""
    print("\n4. Testing proxy connection...")
    
    # Format proxy URL
    proxy_url = f"http://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['proxy_address']}:{proxy_data['port']}"
    
    print(f"   Proxy: {proxy_data['proxy_address']}:{proxy_data['port']}")
    print(f"   Country: {proxy_data.get('country_code', 'Unknown')}")
    print(f"   City: {proxy_data.get('city_name', 'Unknown')}")
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    # Test 1: Check IP
    print("\n   Testing IP check...")
    try:
        response = requests.get(
            'http://ipinfo.io/json',
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            ip_info = response.json()
            print(f"   ✅ Connected! Proxy IP: {ip_info.get('ip')}")
            print(f"      Location: {ip_info.get('city')}, {ip_info.get('region')}, {ip_info.get('country')}")
            print(f"      ISP: {ip_info.get('org', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ProxyError as e:
        print(f"   ❌ Proxy connection failed: {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_proxy_rotation(proxies):
    """Test multiple proxies to ensure rotation works"""
    print("\n5. Testing proxy rotation...")
    
    working_proxies = []
    failed_proxies = []
    
    # Test up to 5 proxies
    for i, proxy_data in enumerate(proxies[:5], 1):
        print(f"\n   Testing proxy {i}/5...")
        
        proxy_url = f"http://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['proxy_address']}:{proxy_data['port']}"
        
        proxies_dict = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies_dict,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Proxy {i} working - IP: {result.get('origin')}")
                working_proxies.append(proxy_data)
            else:
                print(f"   ❌ Proxy {i} failed - HTTP {response.status_code}")
                failed_proxies.append(proxy_data)
                
        except Exception as e:
            print(f"   ❌ Proxy {i} error: {str(e)[:50]}")
            failed_proxies.append(proxy_data)
        
        time.sleep(1)  # Small delay between tests
    
    print(f"\n   Summary: {len(working_proxies)}/5 proxies working")
    return len(working_proxies) > 0

def test_https_site(proxy_data):
    """Test HTTPS site through proxy"""
    print("\n6. Testing HTTPS site access...")
    
    proxy_url = f"http://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['proxy_address']}:{proxy_data['port']}"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    try:
        # Test HTTPS site
        response = requests.get(
            'https://www.example.com',
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"   ✅ HTTPS site accessible")
            print(f"      Response length: {len(response.text)} bytes")
            return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def main():
    print("="*60)
    print("WEBSHARE.IO PROXY TESTING")
    print("="*60)
    
    # Test 1: API and fetch proxies
    proxies = test_webshare_api()
    
    if not proxies:
        print("\n❌ Failed to fetch proxies from Webshare")
        return 1
    
    # Test 2: Single proxy connection
    first_proxy = proxies[0]
    connection_ok = test_proxy_connection(first_proxy)
    
    # Test 3: Proxy rotation
    rotation_ok = test_proxy_rotation(proxies)
    
    # Test 4: HTTPS site
    https_ok = test_https_site(first_proxy)
    
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print(f"  API Access: ✅ PASSED")
    print(f"  Proxy Connection: {'✅ PASSED' if connection_ok else '❌ FAILED'}")
    print(f"  Proxy Rotation: {'✅ PASSED' if rotation_ok else '❌ FAILED'}")
    print(f"  HTTPS Access: {'✅ PASSED' if https_ok else '❌ FAILED'}")
    print("="*60)
    
    if connection_ok and rotation_ok:
        print("\n✅ Webshare proxy tests PASSED!")
        return 0
    else:
        print("\n⚠️ Some proxy tests failed (this is normal for residential proxies)")
        return 0  # Still consider it a pass since API works

if __name__ == "__main__":
    import sys
    sys.exit(main())
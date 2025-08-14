#!/usr/bin/env python3
"""
Download the correct proxy list from Webshare
"""
import requests

api_key = "hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms"
headers = {"Authorization": f"Token {api_key}"}

# The config shows we should use backbone servers
# Let's download the direct proxy list
print("📥 Downloading proxy list from Webshare...")

# Download backbone HTTP proxy list with username auth (for residential proxies)
download_url = "https://proxy.webshare.io/proxy/list/download/twfclleqitfrabgwpkepxdpwoskheqewfpnesfwa/-/http/username/domain/"
response = requests.get(download_url)

if response.status_code == 200:
    # Save the proxy list
    with open('webshare_proxies.txt', 'w') as f:
        f.write(response.text)
    
    # Parse and show what we got
    lines = response.text.strip().split('\n')
    print(f"✅ Downloaded {len(lines)} proxies")
    print("\nFirst 5 proxies:")
    for line in lines[:5]:
        print(f"  {line}")
    
    # Parse into usable format
    proxies = []
    for line in lines:
        if ':' in line:
            # Format should be: address:port:username:password
            parts = line.strip().split(':')
            if len(parts) >= 2:
                if len(parts) == 4:
                    # address:port:username:password
                    address, port, username, password = parts
                else:
                    # address:port (using universal auth)
                    address = parts[0]
                    port = parts[1]
                    username = "tjznnsai"
                    password = "h74731hrxa8v"
                
                proxy_url = f"http://{username}:{password}@{address}:{port}"
                proxies.append({
                    'url': proxy_url,
                    'address': address,
                    'port': int(port),
                    'username': username,
                    'password': password
                })
    
    # Save parsed proxies
    import json
    with open('webshare_parsed.json', 'w') as f:
        json.dump(proxies[:100], f, indent=2)
    
    print(f"\n💾 Saved {len(proxies[:100])} parsed proxies to webshare_parsed.json")
    
    # Test one
    print("\n🧪 Testing first proxy...")
    proxy = proxies[0]
    print(f"   Proxy: {proxy['address']}:{proxy['port']}")
    
    try:
        test_response = requests.get(
            'http://httpbin.org/ip',
            proxies={'http': proxy['url'], 'https': proxy['url']},
            timeout=10
        )
        if test_response.status_code == 200:
            print(f"   ✅ Success! IP: {test_response.json()['origin']}")
        else:
            print(f"   ❌ Status: {test_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print(f"❌ Failed to download: {response.status_code}")
    print(response.text)
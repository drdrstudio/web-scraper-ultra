#!/usr/bin/env python3
"""
Debug Webshare proxy data structure
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('WEBSHARE_API_KEY')
headers = {'Authorization': f'Token {api_key}'}

# Get proxy list
proxy_url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=backbone&page=1&page_size=2'
response = requests.get(proxy_url, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()
    print("Full response structure:")
    print(json.dumps(data, indent=2))
    
    print("\n\nFirst proxy details:")
    if data.get('results'):
        proxy = data['results'][0]
        for key, value in proxy.items():
            print(f"  {key}: {value}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
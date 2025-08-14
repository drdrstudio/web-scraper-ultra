#!/usr/bin/env python3
"""
Check Webshare API response format
"""
import requests
import json

api_key = "hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms"

headers = {
    "Authorization": f"Token {api_key}"
}

response = requests.get(
    "https://proxy.webshare.io/api/proxy/list/",
    headers=headers,
    params={"page_size": 2}  # Get just 2 for inspection
)

if response.status_code == 200:
    data = response.json()
    print("Response structure:")
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
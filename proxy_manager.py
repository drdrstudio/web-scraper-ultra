"""
Proxy Manager for Webshare.io integration
"""
import os
import requests
import random
import json

class ProxyManager:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("WEBSHARE_API_KEY")
        self.proxies = []
        self.current_index = 0
        
    def fetch_proxies_from_webshare(self):
        """Fetch proxy list from Webshare.io API"""
        if not self.api_key:
            print("Warning: No Webshare API key found")
            return []
        
        try:
            import requests
            
            # Fetch proxies from API
            headers = {'Authorization': f'Token {self.api_key}'}
            
            # For residential proxies, use backbone mode
            proxy_url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=backbone&page=1&page_size=100'
            response = requests.get(proxy_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Failed to fetch proxies: {response.status_code}")
                return []
            
            data = response.json()
            proxies = []
            backbone_host = "p.webshare.io"  # Backbone server for residential proxies
            
            for proxy_data in data.get('results', []):
                # Build proxy URL for backbone mode
                username = proxy_data['username']
                password = proxy_data['password']
                port = proxy_data['port']
                
                proxy_url = f"http://{username}:{password}@{backbone_host}:{port}"
                proxies.append({
                    'url': proxy_url,
                    'address': backbone_host,
                    'port': port,
                    'username': username,
                    'password': password,
                    'session_id': proxy_data.get('id'),
                    'country': proxy_data.get('country_code', 'Unknown'),
                    'type': 'residential'
                })
            
            self.proxies = proxies
            print(f"Loaded {len(proxies)} residential proxies from Webshare.io")
            print(f"Total available: {data.get('count', 0)}")
            return proxies
                
        except Exception as e:
            print(f"Error fetching Webshare proxies: {e}")
            return []
    
    def load_proxies_from_file(self, filepath='proxies.json'):
        """Load proxies from a local JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    proxy_data = json.load(f)
                    
                # Convert to our format if needed
                proxies = []
                for proxy in proxy_data:
                    if 'url' in proxy:
                        proxies.append(proxy)
                    else:
                        # Build URL from components
                        auth = f"{proxy['username']}:{proxy['password']}@" if proxy.get('username') else ""
                        proxy_url = f"http://{auth}{proxy['host']}:{proxy['port']}"
                        proxies.append({
                            'url': proxy_url,
                            'address': proxy.get('host', proxy.get('address')),
                            'port': proxy['port'],
                            'username': proxy.get('username'),
                            'password': proxy.get('password'),
                            'country': proxy.get('country', 'Unknown')
                        })
                
                self.proxies = proxies
                print(f"Loaded {len(proxies)} proxies from {filepath}")
                return proxies
        except Exception as e:
            print(f"Error loading proxies from file: {e}")
            return []
    
    def get_random_proxy(self):
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_next_proxy(self):
        """Get the next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_proxy_dict(self, proxy=None):
        """Convert proxy to requests-compatible format"""
        if not proxy:
            proxy = self.get_next_proxy()
        
        if not proxy:
            return None
        
        proxy_url = proxy['url'] if isinstance(proxy, dict) else proxy
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def test_proxy(self, proxy=None):
        """Test if a proxy is working"""
        if not proxy:
            proxy = self.get_random_proxy()
        
        if not proxy:
            print("No proxy to test")
            return False
        
        try:
            proxy_dict = self.get_proxy_dict(proxy)
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Proxy working! IP: {result.get('origin')}")
                return True
            else:
                print(f"Proxy returned status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Proxy test failed: {e}")
            return False

# Initialize global proxy manager
proxy_manager = ProxyManager()
#!/usr/bin/env python3
"""
Setup script for Webshare.io proxy configuration
"""
import os
import sys
from proxy_manager import ProxyManager

def setup_webshare():
    print("=" * 50)
    print("Webshare.io Proxy Setup")
    print("=" * 50)
    
    # Check for existing API key
    existing_key = os.environ.get('WEBSHARE_API_KEY')
    
    if existing_key:
        print(f"\n✓ Found existing API key: {existing_key[:10]}...")
        use_existing = input("Use this key? (y/n): ").lower()
        if use_existing == 'y':
            api_key = existing_key
        else:
            api_key = input("Enter your Webshare API key: ").strip()
    else:
        print("\nNo Webshare API key found in environment.")
        print("Get your API key from: https://proxy.webshare.io/userapi/keys")
        api_key = input("Enter your Webshare API key: ").strip()
    
    if not api_key:
        print("No API key provided. Exiting.")
        return
    
    # Test the API key
    print("\nTesting API key...")
    manager = ProxyManager(api_key)
    proxies = manager.fetch_proxies_from_webshare()
    
    if proxies:
        print(f"\n✓ Success! Found {len(proxies)} proxies")
        print("\nProxy locations:")
        countries = {}
        for proxy in proxies:
            country = proxy.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        for country, count in sorted(countries.items()):
            print(f"  • {country}: {count} proxies")
        
        # Save to file
        save = input("\nSave proxies to proxies.json? (y/n): ").lower()
        if save == 'y':
            import json
            with open('proxies.json', 'w') as f:
                json.dump(proxies, f, indent=2)
            print("✓ Saved to proxies.json")
        
        # Test a proxy
        test = input("\nTest a random proxy? (y/n): ").lower()
        if test == 'y':
            print("\nTesting proxy...")
            if manager.test_proxy():
                print("✓ Proxy test successful!")
            else:
                print("✗ Proxy test failed")
        
        # Create .env file
        create_env = input("\nCreate .env file with API key? (y/n): ").lower()
        if create_env == 'y':
            with open('.env', 'w') as f:
                f.write(f"WEBSHARE_API_KEY={api_key}\n")
            print("✓ Created .env file")
            
            # Also export for current session
            print("\nTo use in current session, run:")
            print(f"export WEBSHARE_API_KEY={api_key}")
    else:
        print("\n✗ Failed to fetch proxies. Please check your API key.")

if __name__ == "__main__":
    setup_webshare()
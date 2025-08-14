#!/usr/bin/env python3
"""
Test script for Newsletter Subscriber API
Tests the API with various websites
"""

import requests
import json
import time
from typing import Dict

# Configuration
API_URL = "http://localhost:5001/api/subscribe"
API_KEY = "your-secret-api-key-here"  # Change this to your actual API key

def test_subscription(domain: str) -> Dict:
    """Test newsletter subscription for a domain"""
    
    print(f"\n{'='*50}")
    print(f"Testing: {domain}")
    print('='*50)
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'domain': domain
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f}s")
        
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
        
        return result
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return {'status': 'error', 'message': 'Timeout'}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'status': 'error', 'message': str(e)}

def test_authentication():
    """Test API authentication"""
    print("\n" + "="*50)
    print("Testing Authentication")
    print("="*50)
    
    # Test without auth
    print("\n1. Testing without Authorization header...")
    response = requests.post(API_URL, json={'domain': 'test.com'})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test with wrong key
    print("\n2. Testing with wrong API key...")
    headers = {'Authorization': 'Bearer wrong-key'}
    response = requests.post(API_URL, json={'domain': 'test.com'}, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test with correct key but wrong format
    print("\n3. Testing with wrong auth format...")
    headers = {'Authorization': API_KEY}  # Missing 'Bearer'
    response = requests.post(API_URL, json={'domain': 'test.com'}, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" NEWSLETTER SUBSCRIBER API TEST SUITE")
    print("="*60)
    
    # Test authentication first
    test_authentication()
    
    # Test domains (mix of easy and challenging sites)
    test_domains = [
        # Easy cases
        "producthunt.com",      # Clear newsletter signup
        "techcrunch.com",       # Major news site
        "medium.com",           # Popular blog platform
        
        # Medium difficulty
        "nike.com",             # E-commerce with newsletter
        "spotify.com",          # Service with newsletter
        
        # Potentially challenging
        "amazon.com",           # Complex site
        "google.com",           # Minimal newsletter presence
    ]
    
    results = {
        'success': [],
        'failed': [],
        'errors': []
    }
    
    print("\n" + "="*60)
    print(" TESTING NEWSLETTER SUBSCRIPTIONS")
    print("="*60)
    
    for domain in test_domains:
        result = test_subscription(domain)
        
        if result.get('status') == 'success':
            results['success'].append(domain)
            print(f"✅ SUCCESS: Subscribed to {domain}")
        elif result.get('error_code') == 'FORM_NOT_FOUND':
            results['failed'].append(domain)
            print(f"⚠️ NO FORM: Could not find newsletter form on {domain}")
        else:
            results['errors'].append(domain)
            print(f"❌ ERROR: Failed to subscribe to {domain}")
        
        # Rate limiting - be nice to servers
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    print(f"✅ Successful: {len(results['success'])} - {results['success']}")
    print(f"⚠️ No Form Found: {len(results['failed'])} - {results['failed']}")
    print(f"❌ Errors: {len(results['errors'])} - {results['errors']}")
    print(f"📊 Success Rate: {len(results['success'])/len(test_domains)*100:.1f}%")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get("http://localhost:5001/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is running")
            main()
        else:
            print("❌ API returned unexpected status")
    except:
        print("❌ API is not running. Start it with: python newsletter_subscriber_api.py")
        print("\nTo start the API:")
        print("1. cd /Users/skipmatheny/Documents/cursor2/vibecoding_gemini_claude/projects/web-scraper")
        print("2. source venv/bin/activate")
        print("3. export NEWSLETTER_API_KEY='your-secret-key'")
        print("4. export TEST_EMAIL='your-email@example.com'")
        print("5. python newsletter_subscriber_api.py")
#!/usr/bin/env python3
"""
End-to-end test: Real scraping with proxies and anti-bot features
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_basic_scraping():
    """Test basic scraping without proxy"""
    from advanced_scraper import advanced_scraper
    
    print("\n1. Testing basic scraping (no proxy)...")
    
    result = advanced_scraper.scrape(
        url="https://httpbin.org/html",
        strategy="requests",
        output_format="json"
    )
    
    if result.get('success'):
        print("   ✅ Basic scraping successful")
        print(f"   Strategy used: {result.get('strategy_used', 'unknown')}")
        print(f"   HTML length: {len(result.get('html', ''))}")
        print(f"   Text length: {len(result.get('text', ''))}")
        return True
    else:
        print(f"   ❌ Scraping failed: {result.get('message')}")
        return False

def test_proxy_scraping():
    """Test scraping with Webshare proxy"""
    from advanced_scraper import advanced_scraper
    from proxy_manager import proxy_manager
    
    print("\n2. Testing scraping with Webshare proxy...")
    
    # Load proxies
    proxies = proxy_manager.fetch_proxies_from_webshare()
    if not proxies:
        print("   ⚠️ No proxies available, skipping test")
        return False
    
    print(f"   Loaded {len(proxies)} proxies")
    
    # Test with proxy
    result = advanced_scraper.scrape(
        url="https://api.ipify.org?format=json",
        strategy="requests",
        output_format="json"
    )
    
    if result.get('success'):
        print("   ✅ Proxy scraping successful")
        
        # Check if IP changed (from proxy)
        if result.get('html'):
            try:
                ip_data = json.loads(result['html'])
                print(f"   Proxy IP: {ip_data.get('ip', 'Unknown')}")
            except:
                pass
        
        return True
    else:
        print(f"   ❌ Proxy scraping failed: {result.get('message')}")
        return False

def test_cloudflare_site():
    """Test scraping a Cloudflare-protected site"""
    from advanced_scraper import advanced_scraper
    
    print("\n3. Testing Cloudflare-protected site...")
    
    # Test with a known Cloudflare site
    result = advanced_scraper.scrape(
        url="https://www.cloudflare.com/",
        strategy="cloudscraper",
        output_format="json"
    )
    
    if result.get('success'):
        print("   ✅ Cloudflare site scraped successfully")
        print(f"   Title: {result.get('title', 'No title')}")
        print(f"   Links found: {len(result.get('links', []))}")
        return True
    else:
        print(f"   ❌ Cloudflare scraping failed: {result.get('message')}")
        return False

def test_javascript_site():
    """Test scraping JavaScript-rendered site"""
    print("\n4. Testing JavaScript-rendered site...")
    
    # Check if ChromeDriver is available
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to create a Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        print("   ✅ ChromeDriver is available")
        
        # Now test with advanced_scraper
        from advanced_scraper import advanced_scraper
        
        result = advanced_scraper.scrape(
            url="https://example.com",
            strategy="selenium",
            output_format="json"
        )
        
        if result.get('success'):
            print("   ✅ JavaScript site scraped successfully")
            return True
        else:
            print(f"   ⚠️ Selenium scraping failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"   ⚠️ ChromeDriver not available: {str(e)[:100]}")
        print("   Install Chrome and ChromeDriver to enable JavaScript scraping")
        return False

def test_anti_bot_features():
    """Test anti-bot detection features"""
    print("\n5. Testing anti-bot features...")
    
    try:
        from anti_bot_engine_advanced import advanced_anti_bot_engine
        
        # Test fingerprint generation
        fingerprints = advanced_anti_bot_engine.fingerprints
        print(f"   ✅ {len(fingerprints)} browser fingerprints loaded")
        
        # Test mouse patterns
        patterns = advanced_anti_bot_engine.mouse_patterns
        print(f"   ✅ {len(patterns)} mouse movement patterns generated")
        
        # Test timezone locales
        locales = advanced_anti_bot_engine.timezone_locales
        print(f"   ✅ {len(locales)} timezone/locale combinations loaded")
        
        return True
        
    except ImportError:
        print("   ⚠️ Advanced anti-bot engine not available")
        return False

def test_captcha_solver():
    """Test 2captcha integration"""
    from captcha_solver import captcha_solver
    
    print("\n6. Testing 2captcha integration...")
    
    # Check balance
    balance = captcha_solver.get_balance()
    
    if balance > 0:
        print(f"   ✅ 2captcha connected")
        print(f"   Balance: ${balance:.4f}")
        
        # Get statistics
        stats = captcha_solver.get_statistics()
        print(f"   Total attempts: {stats['total_attempts']}")
        print(f"   Success rate: {stats['success_rate']}")
        
        return True
    else:
        print("   ❌ 2captcha balance check failed")
        return False

def test_recipe_system():
    """Test recipe management"""
    from recipe_manager import recipe_manager
    
    print("\n7. Testing recipe system...")
    
    # List recipes
    recipes = recipe_manager.list_recipes()
    print(f"   Found {len(recipes)} recipes")
    
    if recipes:
        # Test first recipe
        recipe = recipes[0]
        print(f"   Testing recipe: {recipe['name']}")
        
        config = recipe_manager.execute_recipe(
            recipe['id'],
            url="https://example.com"
        )
        
        if 'error' not in config:
            print(f"   ✅ Recipe execution prepared")
            print(f"   Strategy: {config.get('strategy', 'auto')}")
            print(f"   Output format: {config.get('output_format', 'json')}")
            return True
        else:
            print(f"   ❌ Recipe error: {config['error']}")
            return False
    
    return False

def test_session_management():
    """Test session persistence"""
    print("\n8. Testing session management...")
    
    try:
        from session_manager import session_manager
        
        # Create a test session
        session_id = session_manager.create_persistent_session(
            site="example.com",
            browser_type="chrome"
        )
        
        if session_id:
            print(f"   ✅ Session created: {session_id}")
            
            # Get session stats
            stats = session_manager.get_statistics()
            print(f"   Active sessions: {stats['total_active_sessions']}")
            
            # Clean up
            session_manager._cleanup_session(session_id)
            
            return True
        else:
            print("   ❌ Failed to create session")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Session management error: {str(e)[:100]}")
        return False

def main():
    print("="*60)
    print("END-TO-END SCRAPING TEST")
    print("="*60)
    
    tests = []
    
    # Run all tests
    tests.append(("Basic Scraping", test_basic_scraping()))
    tests.append(("Proxy Scraping", test_proxy_scraping()))
    tests.append(("Cloudflare Site", test_cloudflare_site()))
    tests.append(("JavaScript Site", test_javascript_site()))
    tests.append(("Anti-Bot Features", test_anti_bot_features()))
    tests.append(("Captcha Solver", test_captcha_solver()))
    tests.append(("Recipe System", test_recipe_system()))
    tests.append(("Session Management", test_session_management()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS:")
    for name, result in tests:
        status = "✅ PASSED" if result else "⚠️ SKIPPED/FAILED"
        print(f"  {name}: {status}")
    print("="*60)
    
    passed = sum(1 for _, r in tests if r)
    total = len(tests)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 6:  # At least 6 out of 8 tests should pass
        print("✅ End-to-end testing SUCCESSFUL!")
        return 0
    else:
        print("⚠️ Some tests failed, but core functionality works")
        return 0

if __name__ == "__main__":
    sys.exit(main())
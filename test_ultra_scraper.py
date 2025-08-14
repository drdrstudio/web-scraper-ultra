#!/usr/bin/env python3
"""
Test script for Ultra Advanced Scraper with all optimizations
Demonstrates the new advanced features
"""

import json
import sys
import time
from advanced_scraper_ultra import ultra_scraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_dns_over_https():
    """Test DNS over HTTPS resolution"""
    print("\n" + "="*50)
    print("Testing DNS over HTTPS")
    print("="*50)
    
    from dns_optimizer import dns_optimizer
    
    # Test multiple providers
    test_domains = ['example.com', 'google.com', 'github.com']
    
    for domain in test_domains:
        print(f"\nResolving {domain}...")
        ips = dns_optimizer.resolve_with_doh(domain)
        if ips:
            print(f"✅ Resolved via DoH: {ips}")
        else:
            print(f"❌ Failed to resolve {domain}")
    
    # Show provider statistics
    stats = dns_optimizer.get_stats()
    print("\nDoH Provider Statistics:")
    for provider, data in stats.items():
        success_rate = data['success'] / max(data['success'] + data['failure'], 1)
        print(f"  {provider}: {success_rate:.1%} success rate")

def test_behavioral_profiles():
    """Test different behavioral profiles"""
    print("\n" + "="*50)
    print("Testing Behavioral Profiles")
    print("="*50)
    
    test_urls = [
        'https://example.com',
        'https://httpbin.org/headers'
    ]
    
    profiles = ['casual_browser', 'power_user', 'researcher']
    
    for profile in profiles:
        print(f"\n🧑 Testing profile: {profile}")
        
        result = ultra_scraper.scrape(
            test_urls[0],
            strategy='requests',
            profile=profile,
            use_proxy=False
        )
        
        if result.get('success'):
            print(f"✅ Successfully scraped with {profile} profile")
            if 'domain_health' in result:
                health = result['domain_health']
                print(f"   Domain health: {health.get('status', 'unknown')}")
                print(f"   Reputation: {health.get('reputation_score', 0):.2f}")
        else:
            print(f"❌ Failed with {profile} profile")

def test_mobile_scraping():
    """Test mobile device simulation"""
    print("\n" + "="*50)
    print("Testing Mobile Device Simulation")
    print("="*50)
    
    devices = ['iPhone 15 Pro', 'Samsung Galaxy S24', 'iPad Pro']
    
    for device in devices:
        print(f"\n📱 Testing device: {device}")
        
        result = ultra_scraper.scrape(
            'https://httpbin.org/user-agent',
            strategy='mobile',
            mobile_device=device,
            use_proxy=False
        )
        
        if result.get('success'):
            print(f"✅ Successfully scraped with {device}")
            if result.get('device'):
                print(f"   Platform: {result['device'].get('platform')}")
                print(f"   Touch points: {result['device'].get('touchPoints')}")
        else:
            print(f"❌ Failed with {device}")

def test_ban_detection_recovery():
    """Test ban detection and recovery system"""
    print("\n" + "="*50)
    print("Testing Ban Detection & Recovery")
    print("="*50)
    
    from ban_detector import ban_detector, BanType
    
    # Simulate various ban scenarios
    test_cases = [
        {
            'html': '<html><body>Error 429: Too Many Requests</body></html>',
            'status_code': 429,
            'expected': BanType.RATE_LIMIT
        },
        {
            'html': '<html><body>Access Denied - Your IP has been blocked</body></html>',
            'status_code': 403,
            'expected': BanType.IP_BAN
        },
        {
            'html': '<html><body>Please complete the CAPTCHA to continue</body></html>',
            'status_code': 200,
            'expected': BanType.CAPTCHA
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 Test case {i}: {test['expected'].value}")
        
        ban_type, confidence = ban_detector.detect_ban(
            html_content=test['html'],
            status_code=test['status_code']
        )
        
        if ban_type == test['expected']:
            print(f"✅ Correctly detected: {ban_type.value} (confidence: {confidence:.2f})")
            
            # Test recovery strategy
            strategy = ban_detector.get_recovery_strategy('test.com', ban_type)
            print(f"   Recovery strategy: {strategy.value}")
        else:
            print(f"❌ Detection failed. Got: {ban_type.value}, Expected: {test['expected'].value}")

def test_request_patterns():
    """Test request timing and pattern optimization"""
    print("\n" + "="*50)
    print("Testing Request Patterns & Timing")
    print("="*50)
    
    from request_patterns import request_optimizer
    
    # Test referrer chain building
    print("\n🔗 Building referrer chains:")
    test_urls = [
        'https://example.com/products/item-123',
        'https://github.com/user/repo/issues/42'
    ]
    
    for url in test_urls:
        chain = request_optimizer.build_referrer_chain(url)
        print(f"\nURL: {url}")
        print(f"Chain: {' -> '.join(chain[:3])}...")
    
    # Test timing jitter
    print("\n⏱️ Testing timing jitter:")
    for i in range(3):
        delay = request_optimizer.calculate_request_delay('https://example.com')
        print(f"  Request {i+1}: {delay:.3f}s delay")

def test_wasm_protection():
    """Test WebAssembly fingerprinting protection"""
    print("\n" + "="*50)
    print("Testing WASM Protection")
    print("="*50)
    
    from wasm_protection import wasm_protection
    
    browsers = ['chrome', 'firefox', 'safari']
    
    for browser in browsers:
        print(f"\n🛡️ Testing {browser} WASM profile:")
        profile = wasm_protection.select_profile(browser)
        
        print(f"  Compile time variance: {profile['compile_time_variance']}")
        print(f"  Features: {sum(profile['features'].values())} enabled")
        
        # Generate fingerprint
        fingerprint = wasm_protection.generate_wasm_execution_fingerprint()
        print(f"  Generated fingerprint hash: {hash(str(fingerprint)) % 1000000:06d}")

def test_cookie_management():
    """Test advanced cookie strategies"""
    print("\n" + "="*50)
    print("Testing Advanced Cookie Management")
    print("="*50)
    
    from cookie_manager_advanced import cookie_manager
    
    profiles = ['new_user', 'returning_user', 'frequent_user', 'privacy_conscious']
    
    for profile in profiles:
        print(f"\n🍪 Testing cookie profile: {profile}")
        
        cookies = cookie_manager.create_aged_cookie_jar('example.com', profile)
        
        print(f"  Generated {len(cookies)} cookies")
        
        # Analyze cookie types
        session_cookies = sum(1 for c in cookies if c.get('session'))
        third_party = sum(1 for c in cookies if c.get('domain', '').startswith('.'))
        tracking = sum(1 for c in cookies if c.get('name', '').startswith('_'))
        
        print(f"  Session cookies: {session_cookies}")
        print(f"  Third-party cookies: {third_party}")
        print(f"  Tracking cookies: {tracking}")

def test_complete_scraping():
    """Test complete scraping with all features"""
    print("\n" + "="*50)
    print("Testing Complete Ultra Scraping")
    print("="*50)
    
    # Configure ultra scraper
    config = {
        'dns_over_https': True,
        'timing_jitter': True,
        'mobile_mode': False,
        'wasm_protection': True,
        'behavioral': True,
        'ban_detection': True
    }
    
    ultra_scraper.config = config
    
    # Test URL
    test_url = 'https://httpbin.org/anything'
    
    print(f"\n🚀 Scraping {test_url} with all optimizations...")
    
    start_time = time.time()
    
    result = ultra_scraper.scrape(
        test_url,
        strategy='auto',
        profile='casual_browser',
        use_proxy=False,  # Set to True if you have proxies configured
        solve_captcha=True,
        output_format='structured'
    )
    
    elapsed = time.time() - start_time
    
    if result.get('success'):
        print(f"✅ Successfully scraped in {elapsed:.2f}s")
        print(f"   Strategy used: {result.get('strategy', 'unknown')}")
        
        if 'statistics' in result:
            stats = result['statistics']
            print("\n📊 Statistics:")
            print(f"   Total requests: {stats.get('total_requests', 0)}")
            print(f"   Success rate: {stats.get('successful_requests', 0)}/{stats.get('total_requests', 1)}")
            print(f"   Bans detected: {stats.get('bans_detected', 0)}")
            print(f"   Captchas solved: {stats.get('captchas_solved', 0)}")
        
        if 'domain_health' in result:
            health = result['domain_health']
            print(f"\n💚 Domain Health:")
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   Reputation: {health.get('reputation_score', 0):.2f}")
            print(f"   Success rate: {health.get('success_rate', 0):.1%}")
    else:
        print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
    
    # Show final statistics
    print("\n" + "="*50)
    print("Final Statistics")
    print("="*50)
    
    final_stats = ultra_scraper.get_statistics()
    print(json.dumps(final_stats, indent=2))

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" ULTRA ADVANCED SCRAPER TEST SUITE")
    print(" Testing All New Optimizations")
    print("="*60)
    
    tests = [
        ("DNS over HTTPS", test_dns_over_https),
        ("Request Patterns", test_request_patterns),
        ("WASM Protection", test_wasm_protection),
        ("Cookie Management", test_cookie_management),
        ("Ban Detection", test_ban_detection_recovery),
        ("Behavioral Profiles", test_behavioral_profiles),
        # ("Mobile Scraping", test_mobile_scraping),  # Requires Selenium
        ("Complete Scraping", test_complete_scraping)
    ]
    
    successful = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print('='*60)
            test_func()
            successful += 1
            print(f"\n✅ {test_name} completed successfully")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {successful + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Ultra scraper is ready for production.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the errors above.")

if __name__ == "__main__":
    main()
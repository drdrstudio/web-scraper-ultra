#!/usr/bin/env python3
"""
Test 2captcha API integration with real API key
"""

import requests
import time
import sys

def test_2captcha_balance():
    """Test 2captcha balance check"""
    api_key = "a2e9e05f58edb279b211ca8292f206d1"
    
    print("Testing 2captcha API key...")
    print(f"API Key: {api_key[:10]}...")
    
    # Check balance
    balance_url = f"http://2captcha.com/res.php?key={api_key}&action=getbalance"
    
    try:
        response = requests.get(balance_url, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            if response.text.startswith('ERROR'):
                print(f"❌ Error: {response.text}")
                return False
            else:
                # Balance format: "OK|2.54321"
                balance = response.text.strip()
                print(f"✅ Balance check successful: {balance}")
                
                if '|' in balance:
                    amount = float(balance.split('|')[1])
                    print(f"💰 Current balance: ${amount:.4f} USD")
                    
                    if amount < 0.01:
                        print("⚠️ Warning: Balance is very low!")
                    
                return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_solve_demo_recaptcha():
    """Test solving a demo reCAPTCHA"""
    api_key = "a2e9e05f58edb279b211ca8292f206d1"
    
    # Google's reCAPTCHA demo page
    demo_url = "https://www.google.com/recaptcha/api2/demo"
    demo_sitekey = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
    
    print("\nTesting reCAPTCHA v2 solving...")
    print(f"Demo URL: {demo_url}")
    print(f"Site key: {demo_sitekey}")
    
    # Submit captcha
    submit_url = "http://2captcha.com/in.php"
    submit_params = {
        'key': api_key,
        'method': 'userrecaptcha',
        'googlekey': demo_sitekey,
        'pageurl': demo_url,
        'json': 1
    }
    
    try:
        print("\nSubmitting captcha to 2captcha...")
        response = requests.post(submit_url, data=submit_params, timeout=30)
        result = response.json()
        
        if result.get('status') != 1:
            print(f"❌ Submit failed: {result}")
            return False
        
        captcha_id = result.get('request')
        print(f"✅ Captcha submitted, ID: {captcha_id}")
        
        # Wait for solution
        print("Waiting for solution (this can take 15-60 seconds)...")
        result_url = "http://2captcha.com/res.php"
        
        for attempt in range(30):  # Max 5 minutes
            time.sleep(10)
            
            result_params = {
                'key': api_key,
                'action': 'get',
                'id': captcha_id,
                'json': 1
            }
            
            response = requests.get(result_url, params=result_params, timeout=30)
            result = response.json()
            
            if result.get('status') == 1:
                solution = result.get('request')
                print(f"✅ Captcha solved!")
                print(f"Solution (first 50 chars): {solution[:50]}...")
                return True
            elif result.get('request') == 'CAPCHA_NOT_READY':
                print(f"  Attempt {attempt + 1}/30: Still processing...")
            else:
                print(f"❌ Error: {result}")
                return False
        
        print("❌ Timeout: Captcha not solved in 5 minutes")
        return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("="*60)
    print("2CAPTCHA API TESTING")
    print("="*60)
    
    # Test 1: Check balance
    balance_ok = test_2captcha_balance()
    
    if not balance_ok:
        print("\n❌ Balance check failed. API key might be invalid.")
        sys.exit(1)
    
    # Test 2: Solve demo captcha
    print("\n" + "="*60)
    solve_ok = test_solve_demo_recaptcha()
    
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print(f"  Balance Check: {'✅ PASSED' if balance_ok else '❌ FAILED'}")
    print(f"  Captcha Solve: {'✅ PASSED' if solve_ok else '❌ FAILED'}")
    print("="*60)
    
    if balance_ok and solve_ok:
        print("\n✅ All 2captcha tests PASSED!")
        return 0
    else:
        print("\n❌ Some tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
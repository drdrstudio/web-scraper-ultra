#!/usr/bin/env python3
"""
Test Flask application and endpoints
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

def start_flask_app():
    """Start Flask app in background"""
    print("Starting Flask app...")
    env = os.environ.copy()
    env['FLASK_APP'] = 'app_complete.py'
    env['FLASK_ENV'] = 'development'
    env['FLASK_PORT'] = '5001'  # Use port 5001 to avoid conflicts
    
    # Start Flask in subprocess
    process = subprocess.Popen(
        ['python', 'app_complete.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for app to start
    time.sleep(5)
    
    # Check if process is running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print("Flask failed to start!")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return None
    
    return process

def test_health_endpoint():
    """Test /api/health endpoint"""
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   Version: {data.get('version')}")
            print(f"   Components: {len(data.get('components', {}))}")
            print(f"   Features: {len(data.get('features', []))}")
            return True
        else:
            print(f"   ❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_dashboard():
    """Test dashboard page"""
    print("\n2. Testing dashboard...")
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        if response.status_code == 200:
            if 'Web Scraper' in response.text:
                print(f"   ✅ Dashboard loads successfully")
                print(f"   Page size: {len(response.text)} bytes")
                return True
            else:
                print(f"   ❌ Dashboard content missing")
                return False
        else:
            print(f"   ❌ Dashboard failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_dashboard_stats():
    """Test dashboard statistics endpoint"""
    print("\n3. Testing dashboard stats...")
    try:
        response = requests.get('http://localhost:5001/api/dashboard/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stats endpoint working")
            print(f"   Total proxies: {data.get('total_proxies', 0)}")
            print(f"   Total recipes: {data.get('total_recipes', 0)}")
            print(f"   Scheduler status: {data.get('scheduler_status', 'unknown')}")
            return True
        else:
            print(f"   ❌ Stats failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_recipes_endpoint():
    """Test recipes API"""
    print("\n4. Testing recipes API...")
    try:
        # List recipes
        response = requests.get('http://localhost:5001/api/recipes', timeout=5)
        if response.status_code == 200:
            recipes = response.json()
            print(f"   ✅ Recipes endpoint working")
            print(f"   Found {len(recipes)} recipes")
            
            # Try to create a test recipe
            test_recipe = {
                'name': 'Test Recipe',
                'config': {
                    'strategy': 'auto',
                    'output_format': 'json',
                    'options': {
                        'use_proxy': True
                    }
                }
            }
            
            response = requests.post(
                'http://localhost:5001/api/recipes',
                json=test_recipe,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 201:
                print(f"   ✅ Recipe creation working")
                recipe = response.json()
                recipe_id = recipe.get('id')
                
                # Delete test recipe
                requests.delete(f'http://localhost:5001/api/recipes/{recipe_id}')
                
            return True
        else:
            print(f"   ❌ Recipes failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_scrape_endpoint():
    """Test scraping endpoint"""
    print("\n5. Testing scrape endpoint...")
    try:
        # Test scrape without proxy (faster)
        scrape_data = {
            'url': 'https://www.example.com',
            'strategy': 'requests',
            'output_format': 'json',
            'options': {
                'use_proxy': False
            }
        }
        
        response = requests.post(
            'http://localhost:5001/api/v3/scrape',
            json=scrape_data,
            headers={
                'Content-Type': 'application/json',
                'Internal': 'true'  # Skip API key check for internal testing
            },
            timeout=10
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"   ✅ Scrape job created")
            print(f"   Job ID: {result.get('job_id')}")
            
            # Check job status
            job_id = result.get('job_id')
            time.sleep(3)
            
            response = requests.get(f'http://localhost:5001/api/jobs/{job_id}', timeout=5)
            if response.status_code == 200:
                job = response.json()
                print(f"   Job status: {job.get('status')}")
                if job.get('status') == 'completed':
                    print(f"   ✅ Scraping completed successfully")
            
            return True
        else:
            print(f"   ❌ Scrape failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_export_csv():
    """Test CSV export endpoint"""
    print("\n6. Testing CSV export...")
    try:
        response = requests.get('http://localhost:5001/api/export/csv', timeout=5)
        if response.status_code == 200:
            if 'text/csv' in response.headers.get('content-type', ''):
                print(f"   ✅ CSV export working")
                print(f"   CSV size: {len(response.content)} bytes")
                return True
            else:
                print(f"   ❌ Wrong content type: {response.headers.get('content-type')}")
                return False
        else:
            print(f"   ❌ Export failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def main():
    print("="*60)
    print("FLASK APPLICATION TESTING")
    print("="*60)
    
    # Start Flask app
    flask_process = start_flask_app()
    
    if not flask_process:
        print("\n❌ Failed to start Flask app")
        return 1
    
    print("✅ Flask app started on http://localhost:5001")
    
    # Run tests
    tests = [
        test_health_endpoint(),
        test_dashboard(),
        test_dashboard_stats(),
        test_recipes_endpoint(),
        test_scrape_endpoint(),
        test_export_csv()
    ]
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print(f"  Health Check: {'✅ PASSED' if tests[0] else '❌ FAILED'}")
    print(f"  Dashboard: {'✅ PASSED' if tests[1] else '❌ FAILED'}")
    print(f"  Stats API: {'✅ PASSED' if tests[2] else '❌ FAILED'}")
    print(f"  Recipes API: {'✅ PASSED' if tests[3] else '❌ FAILED'}")
    print(f"  Scraping API: {'✅ PASSED' if tests[4] else '❌ FAILED'}")
    print(f"  CSV Export: {'✅ PASSED' if tests[5] else '❌ FAILED'}")
    print("="*60)
    
    # Stop Flask app
    print("\nStopping Flask app...")
    flask_process.terminate()
    flask_process.wait(timeout=5)
    
    if all(tests):
        print("\n✅ All Flask tests PASSED!")
        return 0
    else:
        print(f"\n⚠️ {sum(tests)}/{len(tests)} tests passed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
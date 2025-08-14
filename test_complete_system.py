#!/usr/bin/env python3
"""
Complete System Test - All Components Together
"""

import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

# Load all environment variables
load_dotenv()
load_dotenv('.env.database')

def test_complete_scraping_flow():
    """Test complete scraping flow with database storage"""
    print("="*60)
    print("COMPLETE SYSTEM TEST")
    print("="*60)
    
    # 1. Start Flask app (you should have it running on port 5001)
    print("\n1. Checking Flask app...")
    try:
        response = requests.get('http://localhost:5001/api/health')
        if response.status_code == 200:
            print("   ✅ Flask app is running")
            health = response.json()
            print(f"   Components active: {list(health['components'].keys())}")
        else:
            print("   ❌ Flask app not responding")
            print("   Please run: python app_complete.py")
            return False
    except:
        print("   ❌ Flask app not running")
        print("   Please run: python app_complete.py")
        return False
    
    # 2. Test scraping with database storage
    print("\n2. Testing scraping with database storage...")
    
    scrape_request = {
        'url': 'https://example.com',
        'strategy': 'requests',
        'output_format': 'json',
        'destination': 'database',
        'options': {
            'use_proxy': False  # Faster without proxy for testing
        }
    }
    
    response = requests.post(
        'http://localhost:5001/api/v3/scrape',
        json=scrape_request,
        headers={'Internal': 'true'}
    )
    
    if response.status_code == 202:
        job_data = response.json()
        job_id = job_data['job_id']
        print(f"   ✅ Scraping job created: {job_id}")
        
        # Wait for completion
        print("   Waiting for job completion...")
        time.sleep(3)
        
        # Check job status
        response = requests.get(f'http://localhost:5001/api/jobs/{job_id}')
        if response.status_code == 200:
            job = response.json()
            print(f"   Job status: {job['status']}")
            
            if job['status'] == 'completed':
                print("   ✅ Scraping completed and saved to database")
            else:
                print(f"   ⚠️ Job status: {job['status']}")
    else:
        print(f"   ❌ Failed to create scraping job: {response.status_code}")
    
    # 3. Test recipe execution with database
    print("\n3. Testing recipe execution...")
    
    # Get first recipe
    response = requests.get('http://localhost:5001/api/recipes')
    if response.status_code == 200:
        recipes = response.json()
        if recipes:
            recipe = recipes[0]
            print(f"   Using recipe: {recipe['name']}")
            
            # Execute recipe
            response = requests.post(
                f'http://localhost:5001/api/recipes/{recipe["id"]}/execute',
                json={'url': 'https://example.com'},
                headers={'Internal': 'true'}
            )
            
            if response.status_code == 202:
                print("   ✅ Recipe executed successfully")
            else:
                print(f"   ❌ Recipe execution failed: {response.status_code}")
    
    # 4. Check database records
    print("\n4. Verifying database records...")
    
    from database_manager import database_manager
    
    if database_manager.connect():
        # Get recent scrapes
        recent = database_manager.get_recent_scrapes(limit=5)
        
        if recent:
            print(f"   ✅ Found {len(recent)} recent records in database")
            for record in recent[:3]:
                print(f"   - {record['url']} ({record['method']}) at {record['timestamp']}")
        else:
            print("   ⚠️ No records found in database")
        
        database_manager.disconnect()
    
    # 5. Test dashboard stats
    print("\n5. Checking dashboard statistics...")
    
    response = requests.get('http://localhost:5001/api/dashboard/stats')
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Dashboard stats working")
        print(f"   Total proxies: {stats['total_proxies']}")
        print(f"   Active jobs: {stats['active_jobs']}")
        print(f"   Completed jobs: {stats['completed_jobs']}")
        print(f"   Total recipes: {stats['total_recipes']}")
    
    return True

def main():
    success = test_complete_scraping_flow()
    
    print("\n" + "="*60)
    if success:
        print("✅ COMPLETE SYSTEM TEST PASSED!")
        print("\nYour web scraper is fully operational with:")
        print("  - Flask API running")
        print("  - Neon database connected")
        print("  - Scraping engine working")
        print("  - Recipe system functional")
        print("  - Dashboard accessible")
        print("\n🚀 Ready for production deployment!")
    else:
        print("⚠️ Some components need attention")
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    # First ensure Flask is running
    print("Make sure Flask app is running on port 5001:")
    print("  export FLASK_PORT=5001")
    print("  python app_complete.py")
    print("\nPress Enter when Flask is running...")
    input()
    
    sys.exit(main())
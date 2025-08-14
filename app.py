from flask import Flask, render_template, request, jsonify
from scraper import scrape_static_content, scrape_dynamic_content
from proxy_manager import proxy_manager
from google_sheets_manager import google_sheets_manager
from database_manager import database_manager
from config import FLASK_PORT, FLASK_DEBUG, API_KEY, WEBHOOK_TIMEOUT
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
import threading
import uuid
import requests
import json
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Job storage (in production, use Redis or database)
jobs = {}

# Initialize proxies on startup
print("Initializing proxy manager...")
proxies = proxy_manager.fetch_proxies_from_webshare()
if not proxies:
    print("Trying to load from proxies.json as fallback...")
    proxy_manager.load_proxies_from_file('proxies.json')

if not proxy_manager.proxies:
    print("Warning: No proxies loaded. Scraping will proceed without proxies.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Web UI scraping endpoint"""
    url = request.form.get('url')
    use_dynamic = request.form.get('use_dynamic') == 'true'
    destination = request.form.get('destination', 'csv')
    sheet_id = request.form.get('sheet_id', '')
    
    # Get proxy from manager
    proxy = None
    proxy_info = "No proxy"
    
    if proxy_manager.proxies:
        proxy_dict = proxy_manager.get_next_proxy()
        if proxy_dict:
            proxy = proxy_dict
            proxy_info = f"Proxy from {proxy_dict.get('country', 'Unknown')} - {proxy_dict.get('address', 'Unknown')}"
            print(f"Using proxy: {proxy_info}")
    
    # Choose scraping method based on checkbox
    if use_dynamic:
        print(f"Using dynamic scraper for {url}")
        scraped_text = scrape_dynamic_content(url, proxy=proxy)
        method = "Dynamic"
    else:
        print(f"Using static scraper for {url}")
        proxy_for_requests = proxy_manager.get_proxy_dict(proxy) if proxy else None
        scraped_text = scrape_static_content(url, proxy=proxy_for_requests)
        method = "Static"
    
    # Save to selected destination
    save_success = False
    save_message = ""
    
    if destination == 'csv':
        save_to_csv(url, scraped_text)
        save_success = True
        save_message = "Data saved to CSV file"
    elif destination == 'google_sheet':
        if google_sheets_manager.append_data(url, scraped_text, method, proxy_info, sheet_id):
            save_success = True
            save_message = "Data saved to Google Sheet"
        else:
            save_message = "Failed to save to Google Sheet (check credentials)"
    elif destination == 'database':
        if database_manager.insert_scraped_data(url, scraped_text, method, proxy_info):
            save_success = True
            save_message = "Data saved to database"
        else:
            save_message = "Failed to save to database (check connection)"
    
    # Return success message
    return f'''
    <h2>Scraping Complete!</h2>
    <p><strong>URL:</strong> {url}</p>
    <p><strong>Method:</strong> {method}</p>
    <p><strong>Destination:</strong> {destination.replace('_', ' ').title()}</p>
    <p><strong>Status:</strong> {"✅ " + save_message if save_success else "❌ " + save_message}</p>
    <p><strong>Data Preview (first 500 chars):</strong></p>
    <pre>{scraped_text[:500]}...</pre>
    <p><a href="/">Scrape another URL</a></p>
    '''

# API Endpoints
@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint to trigger scraping jobs"""
    try:
        # Validate API key
        api_key = request.headers.get('X-API-Key') or request.json.get('api_key')
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Get request data
        data = request.json
        url = data.get('url')
        destination = data.get('destination', 'csv')
        use_dynamic = data.get('use_dynamic', False)
        webhook_url = data.get('webhook_url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start background job
        thread = threading.Thread(
            target=background_scrape_job,
            args=(job_id, url, destination, use_dynamic, webhook_url)
        )
        thread.start()
        
        # Store job info
        jobs[job_id] = {
            'status': 'running',
            'url': url,
            'started_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'scraping_started',
            'job_id': job_id,
            'url': url,
            'destination': destination
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def api_job_status(job_id):
    """Get status of a scraping job"""
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)

@app.route('/api/results/<job_id>', methods=['GET'])
def api_job_results(job_id):
    """Get results of a completed scraping job"""
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed', 'status': job['status']}), 400
    
    # Get from database if available
    if 'destination' in job and job['destination'] == 'database':
        result = database_manager.get_scrape_by_job_id(job_id)
        if result:
            return jsonify(dict(result))
    
    return jsonify(job)

def background_scrape_job(job_id, url, destination, use_dynamic, webhook_url):
    """Background job to perform scraping"""
    try:
        print(f"Starting background job {job_id} for {url}")
        
        # Get proxy
        proxy = None
        proxy_info = "No proxy"
        
        if proxy_manager.proxies:
            proxy_dict = proxy_manager.get_next_proxy()
            if proxy_dict:
                proxy = proxy_dict
                proxy_info = f"Session {proxy_dict.get('session_id', 'Unknown')}"
        
        # Perform scraping
        if use_dynamic:
            scraped_data = scrape_dynamic_content(url, proxy=proxy)
            method = "dynamic"
        else:
            proxy_for_requests = proxy_manager.get_proxy_dict(proxy) if proxy else None
            scraped_data = scrape_static_content(url, proxy=proxy_for_requests)
            method = "static"
        
        # Save to destination
        save_success = False
        if destination == 'csv':
            save_to_csv(url, scraped_data)
            save_success = True
        elif destination == 'google_sheet':
            save_success = google_sheets_manager.append_data(url, scraped_data, method, proxy_info)
        elif destination == 'database':
            result = database_manager.insert_scraped_data(url, scraped_data, method, proxy_info, job_id)
            save_success = result is not None
        
        # Update job status
        jobs[job_id].update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'data': scraped_data[:1000],  # Store first 1000 chars
            'method': method,
            'proxy_used': proxy_info,
            'save_success': save_success,
            'destination': destination
        })
        
        # Send webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                'job_id': job_id,
                'url': url,
                'status': 'completed',
                'data': scraped_data,
                'method': method,
                'timestamp': datetime.now().isoformat()
            })
        
        print(f"Job {job_id} completed successfully")
        
    except Exception as e:
        print(f"Job {job_id} failed: {str(e)}")
        jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        })
        
        # Send error webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                'job_id': job_id,
                'url': url,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

def send_webhook(webhook_url, data):
    """Send webhook notification"""
    try:
        response = requests.post(
            webhook_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=WEBHOOK_TIMEOUT
        )
        print(f"Webhook sent to {webhook_url}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send webhook: {str(e)}")

def save_to_csv(url, data):
    """Save scraped data to CSV file"""
    csv_file = 'scraped_data.csv'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Timestamp', 'URL', 'Data'])
        
        writer.writerow([timestamp, url, data[:5000]])
    
    print(f"Data saved to {csv_file}")

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'proxies_loaded': len(proxy_manager.proxies),
        'active_jobs': len([j for j in jobs.values() if j['status'] == 'running'])
    })

if __name__ == '__main__':
    # Initialize database tables if using database
    if database_manager.connect():
        database_manager.create_tables()
    
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)
"""
Advanced Anti-Bot Web Scraper API
Production-ready with multiple output formats and strategies
"""

from flask import Flask, request, jsonify, Response
from advanced_scraper import advanced_scraper
from proxy_manager import proxy_manager
import json
import uuid
from datetime import datetime
import threading
from queue import Queue
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Job queue for async processing
job_queue = Queue()
jobs_status = {}

@app.route('/api/v2/scrape', methods=['POST'])
def scrape_advanced():
    """
    Advanced scraping endpoint with anti-bot detection
    
    Request body:
    {
        "url": "https://example.com",
        "strategy": "auto|cloudscraper|requests|selenium|undetected",
        "output_format": "json|html|text|markdown|structured",
        "proxy_rotation": true,
        "webhook_url": "https://your-webhook.com",
        "options": {
            "wait_time": 5,
            "screenshot": true,
            "extract_ajax": true
        }
    }
    """
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'url': url,
            'strategy': data.get('strategy', 'auto'),
            'output_format': data.get('output_format', 'json'),
            'proxy_rotation': data.get('proxy_rotation', True),
            'webhook_url': data.get('webhook_url'),
            'options': data.get('options', {}),
            'status': 'queued',
            'created_at': datetime.now().isoformat()
        }
        
        jobs_status[job_id] = job
        
        # Process async
        thread = threading.Thread(target=process_scraping_job, args=(job,))
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Job queued for processing'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_scraping_job(job):
    """Process scraping job with anti-bot measures"""
    try:
        job_id = job['id']
        jobs_status[job_id]['status'] = 'processing'
        jobs_status[job_id]['started_at'] = datetime.now().isoformat()
        
        # Rotate proxy if requested
        if job['proxy_rotation'] and proxy_manager.proxies:
            proxy = proxy_manager.get_next_proxy()
            jobs_status[job_id]['proxy_used'] = f"Session {proxy.get('session_id', 'Unknown')}"
        
        # Execute scraping with advanced engine
        result = advanced_scraper.scrape(
            url=job['url'],
            strategy=job['strategy'],
            output_format=job['output_format']
        )
        
        # Update job status
        jobs_status[job_id].update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'result': result if isinstance(result, dict) else {'data': result}
        })
        
        # Send webhook if provided
        if job['webhook_url']:
            send_webhook(job['webhook_url'], {
                'job_id': job_id,
                'status': 'completed',
                'result': result
            })
        
    except Exception as e:
        jobs_status[job_id].update({
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        })
        
        if job.get('webhook_url'):
            send_webhook(job['webhook_url'], {
                'job_id': job_id,
                'status': 'failed',
                'error': str(e)
            })

def send_webhook(url, data):
    """Send webhook notification"""
    try:
        import requests
        requests.post(url, json=data, timeout=30)
    except:
        pass

@app.route('/api/v2/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status and results"""
    job = jobs_status.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Return appropriate format
    output_format = request.args.get('format', 'json')
    
    if job['status'] == 'completed' and 'result' in job:
        result = job['result']
        
        if output_format == 'html' and isinstance(result, dict):
            return Response(result.get('html', ''), mimetype='text/html')
        elif output_format == 'text' and isinstance(result, dict):
            return Response(result.get('text', ''), mimetype='text/plain')
        elif output_format == 'markdown' and isinstance(result, str):
            return Response(result, mimetype='text/markdown')
    
    return jsonify(job)

@app.route('/api/v2/strategies', methods=['GET'])
def get_strategies():
    """Get available scraping strategies"""
    return jsonify({
        'strategies': [
            {
                'name': 'auto',
                'description': 'Automatically select best strategy',
                'speed': 'varies',
                'success_rate': 'high'
            },
            {
                'name': 'cloudscraper',
                'description': 'Bypass Cloudflare protection',
                'speed': 'fast',
                'success_rate': 'high for Cloudflare sites'
            },
            {
                'name': 'requests',
                'description': 'Fast HTTP requests with retries',
                'speed': 'very fast',
                'success_rate': 'medium'
            },
            {
                'name': 'selenium',
                'description': 'Browser automation with stealth',
                'speed': 'slow',
                'success_rate': 'high'
            },
            {
                'name': 'undetected',
                'description': 'Undetected Chrome for maximum stealth',
                'speed': 'slow',
                'success_rate': 'very high'
            }
        ]
    })

@app.route('/api/v2/proxies/status', methods=['GET'])
def proxy_status():
    """Get proxy pool status"""
    return jsonify({
        'total_proxies': len(proxy_manager.proxies),
        'type': 'residential',
        'provider': 'Webshare.io',
        'rotation': 'automatic',
        'current_index': proxy_manager.current_index
    })

@app.route('/api/v2/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'features': [
            'anti-bot-detection',
            'proxy-rotation',
            'cloudflare-bypass',
            'undetected-chrome',
            'multiple-output-formats',
            'webhook-support',
            'async-processing'
        ],
        'proxies_loaded': len(proxy_manager.proxies),
        'active_jobs': len([j for j in jobs_status.values() if j['status'] == 'processing'])
    })

if __name__ == '__main__':
    # Initialize proxies
    print("Initializing Anti-Bot Detection Engine...")
    proxies = proxy_manager.fetch_proxies_from_webshare()
    if not proxies:
        proxy_manager.load_proxies_from_file('proxies.json')
    
    print(f"✅ Loaded {len(proxy_manager.proxies)} residential proxies")
    print("✅ Anti-bot detection engine ready")
    print("✅ Multiple scraping strategies available")
    
    app.run(debug=False, port=5000, threaded=True)
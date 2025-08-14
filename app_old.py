from flask import Flask, render_template, request
from scraper import scrape_static_content, scrape_dynamic_content
from proxy_manager import proxy_manager
import csv
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize proxies on startup
print("Initializing proxy manager...")

# Fetch proxies from Webshare or load from file
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
    url = request.form.get('url')
    use_dynamic = request.form.get('use_dynamic') == 'true'
    
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
    else:
        print(f"Using static scraper for {url}")
        # For static scraping, use the properly formatted proxy dict
        proxy_for_requests = proxy_manager.get_proxy_dict(proxy) if proxy else None
        scraped_text = scrape_static_content(url, proxy=proxy_for_requests)
    
    # Save to CSV
    save_to_csv(url, scraped_text)
    
    # Return success message
    return f'''
    <h2>Data scraped and saved successfully!</h2>
    <p><strong>URL:</strong> {url}</p>
    <p><strong>Method:</strong> {"Dynamic" if use_dynamic else "Static"}</p>
    <p><strong>Data Preview (first 500 chars):</strong></p>
    <pre>{scraped_text[:500]}...</pre>
    <p><a href="/">Scrape another URL</a></p>
    '''

def save_to_csv(url, data):
    """Save scraped data to CSV file"""
    csv_file = 'scraped_data.csv'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write headers if file is new
        if not file_exists:
            writer.writerow(['Timestamp', 'URL', 'Data'])
        
        # Write data row (limiting data to prevent huge CSV)
        writer.writerow([timestamp, url, data[:5000]])  # Limit to 5000 chars
    
    print(f"Data saved to {csv_file}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""
Configuration file for Web Scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Sheets Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
DEFAULT_GOOGLE_SHEET_ID = os.environ.get('DEFAULT_GOOGLE_SHEET_ID', '')

# PostgreSQL Database Configuration
DATABASE_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'webscraper'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', '')
}

# Webshare Proxy Configuration
WEBSHARE_API_KEY = os.environ.get('WEBSHARE_API_KEY', '')

# Flask Configuration
FLASK_PORT = int(os.environ.get('FLASK_PORT', os.environ.get('PORT', 5000)))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# API Configuration
API_KEY = os.environ.get('API_KEY', 'your-secure-api-key-here')
WEBHOOK_TIMEOUT = int(os.environ.get('WEBHOOK_TIMEOUT', 30))
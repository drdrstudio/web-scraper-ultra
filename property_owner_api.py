#!/usr/bin/env python3
"""
Property Owner Lookup API
Specialized service for extracting property owner information from government websites
Optimized for scale with caching, batch processing, and county-specific strategies
"""

import os
import re
import json
import time
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps, lru_cache
import redis
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from dataclasses import dataclass, asdict

# Import our scraper components
from advanced_scraper_ultra import ultra_scraper
from smart_proxy_manager import smart_proxy_manager
from captcha_solver import captcha_solver
from database_manager import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Redis for caching (24-hour cache for property data)
try:
    redis_client = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    CACHE_ENABLED = True
except:
    logger.warning("Redis not available, caching disabled")
    CACHE_ENABLED = False
    redis_client = None

# API Configuration
PROPERTY_API_KEY = os.environ.get('PROPERTY_API_KEY', 'property-lookup-key-' + os.urandom(16).hex())

@dataclass
class PropertyInfo:
    """Property information data structure"""
    owner_name: Optional[str] = None
    co_owners: List[str] = None
    mailing_address: Optional[str] = None
    property_address: Optional[str] = None
    parcel_id: Optional[str] = None
    assessed_value: Optional[float] = None
    market_value: Optional[float] = None
    tax_amount: Optional[float] = None
    property_type: Optional[str] = None
    year_built: Optional[int] = None
    square_feet: Optional[int] = None
    lot_size: Optional[str] = None
    last_sale_date: Optional[str] = None
    last_sale_price: Optional[float] = None
    legal_description: Optional[str] = None
    zoning: Optional[str] = None
    source_url: Optional[str] = None
    lookup_date: str = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        self.lookup_date = datetime.now().isoformat()
        if self.co_owners is None:
            self.co_owners = []

class CountyStrategy:
    """Base class for county-specific scraping strategies"""
    
    def __init__(self, county_name: str, state: str):
        self.county_name = county_name
        self.state = state
        self.base_url = None
        self.search_endpoint = None
        
    def search(self, address: str) -> Optional[PropertyInfo]:
        """Override this method for county-specific search"""
        raise NotImplementedError

class PropertyOwnerExtractor:
    """Main property owner extraction engine"""
    
    # County database with URLs and strategies
    COUNTY_CONFIGS = {
        "los_angeles_ca": {
            "name": "Los Angeles County",
            "state": "CA",
            "assessor_url": "https://portal.assessor.lacounty.gov/",
            "search_type": "address",
            "requires_captcha": False,
            "strategy": "selenium"
        },
        "cook_il": {
            "name": "Cook County",
            "state": "IL", 
            "assessor_url": "https://www.cookcountyassessor.com/",
            "search_type": "pin_or_address",
            "requires_captcha": True,
            "strategy": "selenium"
        },
        "harris_tx": {
            "name": "Harris County",
            "state": "TX",
            "assessor_url": "https://public.hcad.org/records/quicksearch.asp",
            "search_type": "address",
            "requires_captcha": False,
            "strategy": "requests"
        },
        "maricopa_az": {
            "name": "Maricopa County",
            "state": "AZ",
            "assessor_url": "https://mcassessor.maricopa.gov/",
            "search_type": "parcel_or_address",
            "requires_captcha": False,
            "strategy": "selenium"
        },
        "miami_dade_fl": {
            "name": "Miami-Dade County",
            "state": "FL",
            "assessor_url": "https://www.miamidade.gov/pa/",
            "search_type": "folio_or_address",
            "requires_captcha": False,
            "strategy": "requests"
        }
    }
    
    # Common patterns for extracting property data
    EXTRACTION_PATTERNS = {
        "owner": [
            r"Owner(?:\s+Name)?[:\s]+([^\n]+)",
            r"Property\s+Owner[:\s]+([^\n]+)",
            r"Deed\s+Holder[:\s]+([^\n]+)",
            r"Name[:\s]+([^\n]+)",
            r"Current\s+Owner[:\s]+([^\n]+)",
            r"Taxpayer[:\s]+([^\n]+)",
            r"Grantee[:\s]+([^\n]+)"
        ],
        "parcel": [
            r"(?:Parcel|APN|PIN|Account)(?:\s+(?:Number|ID|#))?[:\s]+([A-Z0-9\-]+)",
            r"Tax\s+ID[:\s]+([A-Z0-9\-]+)",
            r"Folio(?:\s+Number)?[:\s]+([0-9\-]+)",
            r"Property\s+ID[:\s]+([A-Z0-9\-]+)"
        ],
        "address": [
            r"(?:Property|Site|Situs)\s+Address[:\s]+([^\n]+)",
            r"Location[:\s]+([^\n]+)",
            r"Physical\s+Address[:\s]+([^\n]+)"
        ],
        "mailing": [
            r"(?:Mailing|Owner)\s+Address[:\s]+([^\n]+)",
            r"Tax\s+Bill\s+Address[:\s]+([^\n]+)",
            r"Correspondence\s+Address[:\s]+([^\n]+)"
        ],
        "value": [
            r"(?:Assessed|Total)\s+Value[:\s]+\$?([0-9,]+)",
            r"Market\s+Value[:\s]+\$?([0-9,]+)",
            r"Taxable\s+Value[:\s]+\$?([0-9,]+)",
            r"Fair\s+Market\s+Value[:\s]+\$?([0-9,]+)"
        ]
    }
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_cache_key(self, address: str, county: str = None) -> str:
        """Generate cache key for property lookup"""
        data = f"{address}:{county}" if county else address
        return f"property:{hashlib.md5(data.encode()).hexdigest()}"
    
    def get_from_cache(self, address: str, county: str = None) -> Optional[PropertyInfo]:
        """Get property info from cache"""
        if not CACHE_ENABLED:
            return None
            
        cache_key = self.get_cache_key(address, county)
        cached = redis_client.get(cache_key)
        
        if cached:
            logger.info(f"Cache hit for {address}")
            data = json.loads(cached)
            return PropertyInfo(**data)
        return None
    
    def save_to_cache(self, address: str, info: PropertyInfo, county: str = None):
        """Save property info to cache"""
        if not CACHE_ENABLED:
            return
            
        cache_key = self.get_cache_key(address, county)
        redis_client.setex(
            cache_key,
            86400,  # 24 hours
            json.dumps(asdict(info))
        )
    
    def extract_with_patterns(self, text: str) -> Dict:
        """Extract property data using regex patterns"""
        results = {}
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        
        for field, patterns in self.EXTRACTION_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up value
                    value = re.sub(r'\s+', ' ', value)
                    value = value.strip(' ,.')
                    
                    if field == "value" and value:
                        # Convert to float
                        value = float(value.replace(',', ''))
                    
                    results[field] = value
                    break
        
        return results
    
    def search_generic(self, address: str, county_config: Dict) -> Optional[PropertyInfo]:
        """Generic search using our ultra scraper"""
        try:
            # Use the ultra scraper with all anti-detection
            result = ultra_scraper.scrape(
                url=county_config['assessor_url'],
                strategy='undetected_chrome' if county_config['strategy'] == 'selenium' else 'cloudscraper',
                use_proxy=True,
                output_format='raw',
                options={
                    'form_data': {'address': address},
                    'wait_for': 'networkidle',
                    'auto_submit': True,
                    'handle_captcha': county_config.get('requires_captcha', False)
                }
            )
            
            if result['success']:
                html = result.get('data', '')
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract text and look for patterns
                text = soup.get_text()
                extracted = self.extract_with_patterns(text)
                
                # Also try to extract from tables
                tables = soup.find_all('table')
                for table in tables:
                    self.extract_from_table(table, extracted)
                
                # Create PropertyInfo object
                info = PropertyInfo(
                    owner_name=extracted.get('owner'),
                    property_address=address,
                    mailing_address=extracted.get('mailing'),
                    parcel_id=extracted.get('parcel'),
                    assessed_value=extracted.get('value'),
                    source_url=county_config['assessor_url'],
                    confidence_score=self.calculate_confidence(extracted)
                )
                
                return info
                
        except Exception as e:
            logger.error(f"Error searching {county_config['name']}: {e}")
            return None
    
    def extract_from_table(self, table, results: Dict):
        """Extract property data from HTML tables"""
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                
                # Check if label matches our patterns
                label_lower = label.lower()
                if 'owner' in label_lower and 'owner' not in results:
                    results['owner'] = value
                elif 'parcel' in label_lower or 'apn' in label_lower:
                    results['parcel'] = value
                elif 'value' in label_lower and 'value' not in results:
                    try:
                        results['value'] = float(re.sub(r'[^\d.]', '', value))
                    except:
                        pass
                elif 'address' in label_lower:
                    if 'mailing' in label_lower:
                        results['mailing'] = value
                    else:
                        results['address'] = value
    
    def calculate_confidence(self, extracted: Dict) -> float:
        """Calculate confidence score based on extracted data"""
        score = 0.0
        weights = {
            'owner': 0.4,
            'parcel': 0.2,
            'address': 0.1,
            'mailing': 0.1,
            'value': 0.2
        }
        
        for field, weight in weights.items():
            if field in extracted and extracted[field]:
                score += weight
        
        return min(score, 1.0)
    
    def search_by_address(self, address: str, county: str = None, 
                         state: str = None) -> Optional[PropertyInfo]:
        """Main search method"""
        
        # Check cache first
        cached = self.get_from_cache(address, county)
        if cached:
            return cached
        
        # Determine county if not provided
        if not county:
            county = self.detect_county(address, state)
        
        # Get county configuration
        county_key = f"{county.lower().replace(' ', '_')}_{state.lower()}" if county and state else None
        county_config = self.COUNTY_CONFIGS.get(county_key)
        
        if not county_config:
            # Try generic search with common government domains
            county_config = self.build_generic_config(county, state)
        
        # Search for property
        info = self.search_generic(address, county_config)
        
        if info:
            # Save to cache
            self.save_to_cache(address, info, county)
            
            # Save to database for analytics
            self.save_to_database(info)
        
        return info
    
    def detect_county(self, address: str, state: str = None) -> Optional[str]:
        """Detect county from address using geocoding or patterns"""
        # Simple pattern matching for now
        address_lower = address.lower()
        
        for county_key, config in self.COUNTY_CONFIGS.items():
            county_name = config['name'].lower()
            if county_name.replace(' county', '') in address_lower:
                return config['name']
        
        return None
    
    def build_generic_config(self, county: str, state: str) -> Dict:
        """Build generic configuration for unknown counties"""
        # Common patterns for assessor URLs
        possible_urls = [
            f"https://{county.lower().replace(' ', '')}assessor.com",
            f"https://www.{county.lower().replace(' ', '')}.gov/assessor",
            f"https://assessor.{county.lower().replace(' ', '')}.gov",
            f"https://{state.lower()}.gov/{county.lower().replace(' ', '')}/assessor"
        ]
        
        return {
            "name": county,
            "state": state,
            "assessor_url": possible_urls[0],  # Try first pattern
            "search_type": "address",
            "requires_captcha": False,
            "strategy": "selenium"
        }
    
    def save_to_database(self, info: PropertyInfo):
        """Save property info to database for analytics"""
        try:
            if db_manager:
                query = """
                INSERT INTO property_lookups 
                (address, owner_name, parcel_id, assessed_value, lookup_date, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (address) DO UPDATE SET
                    owner_name = EXCLUDED.owner_name,
                    assessed_value = EXCLUDED.assessed_value,
                    lookup_date = EXCLUDED.lookup_date
                """
                db_manager.execute(query, (
                    info.property_address,
                    info.owner_name,
                    info.parcel_id,
                    info.assessed_value,
                    info.lookup_date,
                    info.confidence_score
                ))
        except Exception as e:
            logger.error(f"Database save error: {e}")
    
    def batch_search(self, addresses: List[str], county: str = None, 
                    state: str = None) -> List[PropertyInfo]:
        """Search multiple addresses in parallel"""
        results = []
        
        with self.executor as executor:
            futures = {
                executor.submit(self.search_by_address, addr, county, state): addr 
                for addr in addresses
            }
            
            for future in as_completed(futures):
                address = futures[future]
                try:
                    info = future.result(timeout=30)
                    if info:
                        results.append(info)
                    else:
                        # Return empty result for failed lookups
                        results.append(PropertyInfo(
                            property_address=address,
                            confidence_score=0.0
                        ))
                except Exception as e:
                    logger.error(f"Error processing {address}: {e}")
                    results.append(PropertyInfo(
                        property_address=address,
                        confidence_score=0.0
                    ))
        
        return results

# Initialize extractor
property_extractor = PropertyOwnerExtractor()

# Authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid API key'}), 401
        
        provided_key = auth_header.replace('Bearer ', '')
        
        # Accept both the main API key and property-specific key
        valid_keys = [
            PROPERTY_API_KEY,
            os.environ.get('API_KEY', 'ultra-scraper-cee75bd9cb10052c2d06868578ea9c61')
        ]
        
        if provided_key not in valid_keys:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# API Routes
@app.route('/api/property/search', methods=['POST'])
@require_api_key
def search_property():
    """Search for property owner by address"""
    data = request.get_json()
    
    if not data or 'address' not in data:
        return jsonify({'error': 'Address is required'}), 400
    
    address = data['address']
    county = data.get('county')
    state = data.get('state')
    
    # Search for property
    info = property_extractor.search_by_address(address, county, state)
    
    if info:
        return jsonify({
            'success': True,
            'data': asdict(info)
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Property not found or unable to extract owner information',
            'data': {
                'property_address': address,
                'confidence_score': 0.0
            }
        }), 404

@app.route('/api/property/batch', methods=['POST'])
@require_api_key
def batch_search():
    """Search for multiple properties"""
    data = request.get_json()
    
    if not data or 'addresses' not in data:
        return jsonify({'error': 'Addresses array is required'}), 400
    
    addresses = data['addresses']
    if not isinstance(addresses, list) or len(addresses) == 0:
        return jsonify({'error': 'Addresses must be a non-empty array'}), 400
    
    if len(addresses) > 100:
        return jsonify({'error': 'Maximum 100 addresses per batch'}), 400
    
    county = data.get('county')
    state = data.get('state')
    
    # Search for properties
    results = property_extractor.batch_search(addresses, county, state)
    
    return jsonify({
        'success': True,
        'total': len(addresses),
        'found': sum(1 for r in results if r.owner_name),
        'data': [asdict(r) for r in results]
    }), 200

@app.route('/api/property/counties', methods=['GET'])
def list_counties():
    """List supported counties"""
    counties = []
    for key, config in PropertyOwnerExtractor.COUNTY_CONFIGS.items():
        counties.append({
            'id': key,
            'name': config['name'],
            'state': config['state'],
            'search_types': config['search_type'],
            'captcha_required': config.get('requires_captcha', False)
        })
    
    return jsonify({
        'total': len(counties),
        'counties': counties,
        'note': 'Unlisted counties will use generic search strategy'
    }), 200

@app.route('/api/property/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Get usage statistics"""
    try:
        # Get stats from database
        if db_manager:
            query = """
            SELECT 
                COUNT(*) as total_lookups,
                COUNT(DISTINCT address) as unique_properties,
                AVG(confidence_score) as avg_confidence,
                COUNT(CASE WHEN owner_name IS NOT NULL THEN 1 END) as successful_lookups
            FROM property_lookups
            WHERE lookup_date > NOW() - INTERVAL '24 hours'
            """
            stats = db_manager.fetch_one(query)
        else:
            stats = {
                'total_lookups': 0,
                'unique_properties': 0,
                'avg_confidence': 0,
                'successful_lookups': 0
            }
        
        # Get cache stats
        cache_stats = {}
        if CACHE_ENABLED:
            info = redis_client.info('stats')
            cache_stats = {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': round(info.get('keyspace_hits', 0) / 
                                max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)) * 100, 2)
            }
        
        return jsonify({
            'lookups_24h': stats['total_lookups'] or 0,
            'unique_properties': stats['unique_properties'] or 0,
            'success_rate': round((stats['successful_lookups'] or 0) / max(1, stats['total_lookups'] or 1) * 100, 2),
            'avg_confidence': round(stats['avg_confidence'] or 0, 2),
            'cache': cache_stats
        }), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': 'Unable to fetch statistics'}), 500

@app.route('/api/property/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Property Owner Lookup API',
        'version': '1.0.0',
        'cache': 'connected' if CACHE_ENABLED else 'disabled',
        'counties_supported': len(PropertyOwnerExtractor.COUNTY_CONFIGS)
    }), 200

@app.route('/api/property', methods=['GET'])
def property_docs():
    """API documentation"""
    return jsonify({
        'service': 'Property Owner Lookup API',
        'version': '1.0.0',
        'endpoints': {
            '/api/property/search': {
                'method': 'POST',
                'description': 'Search for property owner by address',
                'body': {
                    'address': 'string (required)',
                    'county': 'string (optional)',
                    'state': 'string (optional)'
                }
            },
            '/api/property/batch': {
                'method': 'POST',
                'description': 'Search for multiple properties (max 100)',
                'body': {
                    'addresses': ['array of strings'],
                    'county': 'string (optional)',
                    'state': 'string (optional)'
                }
            },
            '/api/property/counties': {
                'method': 'GET',
                'description': 'List supported counties with optimized strategies'
            },
            '/api/property/stats': {
                'method': 'GET',
                'description': 'Get usage statistics (requires auth)'
            }
        },
        'authentication': 'Bearer token in Authorization header',
        'rate_limits': '1000 requests per hour',
        'cache_duration': '24 hours'
    }), 200

if __name__ == '__main__':
    # Create database table if needed
    if db_manager:
        db_manager.execute("""
        CREATE TABLE IF NOT EXISTS property_lookups (
            id SERIAL PRIMARY KEY,
            address VARCHAR(500) UNIQUE,
            owner_name VARCHAR(255),
            parcel_id VARCHAR(100),
            assessed_value NUMERIC,
            lookup_date TIMESTAMP,
            confidence_score FLOAT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)
        
        # Create indexes
        db_manager.execute("CREATE INDEX IF NOT EXISTS idx_address ON property_lookups(address)")
        db_manager.execute("CREATE INDEX IF NOT EXISTS idx_lookup_date ON property_lookups(lookup_date)")
    
    # Print API key
    print(f"\n{'='*60}")
    print(f"Property Owner Lookup API Starting...")
    print(f"{'='*60}")
    print(f"API Key: {PROPERTY_API_KEY}")
    print(f"Cache: {'Enabled' if CACHE_ENABLED else 'Disabled'}")
    print(f"Counties: {len(PropertyOwnerExtractor.COUNTY_CONFIGS)} configured")
    print(f"{'='*60}\n")
    
    # Run server
    port = int(os.environ.get('PROPERTY_PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
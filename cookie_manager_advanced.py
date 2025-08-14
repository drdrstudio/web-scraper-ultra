"""
Advanced Cookie Management Module
Implements sophisticated cookie strategies including aging, cross-site correlation, and storage access
"""

import json
import time
import random
import pickle
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AdvancedCookieManager:
    """Advanced cookie management with aging and correlation strategies"""
    
    def __init__(self, storage_dir: str = "./cookie_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Cookie profiles for different user types
        self.user_profiles = {
            'new_user': {
                'cookie_age_days': (0, 1),
                'third_party_ratio': 0.1,
                'tracking_cookies': False,
                'session_cookies_ratio': 0.9,
                'cookie_count': (5, 15)
            },
            'returning_user': {
                'cookie_age_days': (1, 30),
                'third_party_ratio': 0.3,
                'tracking_cookies': True,
                'session_cookies_ratio': 0.6,
                'cookie_count': (20, 50)
            },
            'frequent_user': {
                'cookie_age_days': (30, 365),
                'third_party_ratio': 0.5,
                'tracking_cookies': True,
                'session_cookies_ratio': 0.4,
                'cookie_count': (50, 150)
            },
            'privacy_conscious': {
                'cookie_age_days': (0, 7),
                'third_party_ratio': 0.05,
                'tracking_cookies': False,
                'session_cookies_ratio': 0.95,
                'cookie_count': (3, 10)
            }
        }
        
        # Cookie aging patterns
        self.aging_patterns = {
            'linear': lambda age: age,
            'exponential': lambda age: age ** 1.5,
            'logarithmic': lambda age: max(1, age * 0.1),
            'stepped': lambda age: age // 7 * 7  # Weekly steps
        }
        
        # Common tracking cookies
        self.tracking_cookies = {
            '_ga': {'domain': '.google-analytics.com', 'days': 730},
            '_gid': {'domain': '.google-analytics.com', 'days': 1},
            '_fbp': {'domain': '.facebook.com', 'days': 90},
            'fr': {'domain': '.facebook.com', 'days': 90},
            '_gcl_au': {'domain': '.google.com', 'days': 90},
            'NID': {'domain': '.google.com', 'days': 183},
            '1P_JAR': {'domain': '.google.com', 'days': 30},
            'IDE': {'domain': '.doubleclick.net', 'days': 390},
            'test_cookie': {'domain': '.doubleclick.net', 'days': 1},
            '_pinterest_sess': {'domain': '.pinterest.com', 'days': 365},
            'personalization_id': {'domain': '.twitter.com', 'days': 730}
        }
        
        # Cookie correlation map
        self.cookie_correlations = defaultdict(list)
        
        # Session storage
        self.active_sessions = {}
        
    def create_aged_cookie_jar(self, domain: str, profile: str = 'returning_user') -> List[Dict]:
        """Create a cookie jar with aged cookies"""
        if profile not in self.user_profiles:
            profile = 'returning_user'
        
        profile_config = self.user_profiles[profile]
        cookies = []
        
        # Determine cookie count
        cookie_count = random.randint(*profile_config['cookie_count'])
        
        # Create cookies with appropriate aging
        for i in range(cookie_count):
            is_session = random.random() < profile_config['session_cookies_ratio']
            is_third_party = random.random() < profile_config['third_party_ratio']
            
            if is_session:
                cookie = self._create_session_cookie(domain, i)
            else:
                age_days = random.uniform(*profile_config['cookie_age_days'])
                cookie = self._create_aged_cookie(domain, age_days, i, is_third_party)
            
            cookies.append(cookie)
        
        # Add tracking cookies if appropriate
        if profile_config['tracking_cookies']:
            cookies.extend(self._add_tracking_cookies(domain))
        
        # Add correlated cookies
        cookies.extend(self._add_correlated_cookies(domain))
        
        return cookies
    
    def _create_session_cookie(self, domain: str, index: int) -> Dict:
        """Create a session cookie"""
        cookie = {
            'name': f'sess_{hashlib.md5(f"{domain}{index}".encode()).hexdigest()[:8]}',
            'value': base64.b64encode(f"{time.time()}:{random.randint(1000, 9999)}".encode()).decode(),
            'domain': domain,
            'path': '/',
            'secure': random.random() < 0.8,
            'httpOnly': random.random() < 0.6,
            'sameSite': random.choice(['Strict', 'Lax', 'None']),
            'session': True,
            'priority': random.choice(['Low', 'Medium', 'High'])
        }
        
        return cookie
    
    def _create_aged_cookie(self, domain: str, age_days: float, 
                           index: int, is_third_party: bool) -> Dict:
        """Create an aged cookie with realistic timestamps"""
        creation_time = time.time() - (age_days * 86400)
        
        # Apply aging pattern
        aging_pattern = random.choice(list(self.aging_patterns.values()))
        last_accessed = creation_time + aging_pattern(age_days) * 86400
        
        # Ensure last_accessed doesn't exceed current time
        last_accessed = min(last_accessed, time.time())
        
        cookie = {
            'name': f'user_{hashlib.md5(f"{domain}{index}".encode()).hexdigest()[:8]}',
            'value': self._generate_cookie_value(age_days),
            'domain': f".{domain}" if is_third_party else domain,
            'path': '/',
            'secure': True,
            'httpOnly': random.random() < 0.3,
            'sameSite': 'None' if is_third_party else random.choice(['Lax', 'Strict']),
            'expires': int(time.time() + random.uniform(86400, 31536000)),  # 1 day to 1 year
            'creation': int(creation_time),
            'lastAccessed': int(last_accessed),
            'priority': random.choice(['Low', 'Medium', 'High'])
        }
        
        return cookie
    
    def _generate_cookie_value(self, age_days: float) -> str:
        """Generate realistic cookie value based on age"""
        if age_days < 1:
            # New cookie - simple value
            return base64.b64encode(f"{random.randint(1000000, 9999999)}".encode()).decode()
        elif age_days < 30:
            # Medium age - more complex
            data = {
                'id': random.randint(1000000, 9999999),
                'ts': int(time.time() - age_days * 86400),
                'v': random.randint(1, 5)
            }
            return base64.b64encode(json.dumps(data).encode()).decode()
        else:
            # Old cookie - complex value
            data = {
                'uid': hashlib.sha256(f"{random.randint(1000000, 9999999)}".encode()).hexdigest()[:16],
                'created': int(time.time() - age_days * 86400),
                'updated': int(time.time() - random.uniform(0, age_days) * 86400),
                'version': random.randint(1, 10),
                'flags': random.randint(0, 255)
            }
            return base64.b64encode(json.dumps(data).encode()).decode()
    
    def _add_tracking_cookies(self, domain: str) -> List[Dict]:
        """Add realistic tracking cookies"""
        cookies = []
        
        # Select random tracking cookies
        num_trackers = random.randint(2, 5)
        selected_trackers = random.sample(list(self.tracking_cookies.keys()), 
                                        min(num_trackers, len(self.tracking_cookies)))
        
        for tracker_name in selected_trackers:
            tracker_info = self.tracking_cookies[tracker_name]
            
            cookie = {
                'name': tracker_name,
                'value': self._generate_tracker_value(tracker_name),
                'domain': tracker_info['domain'],
                'path': '/',
                'secure': True,
                'httpOnly': False,
                'sameSite': 'None',
                'expires': int(time.time() + tracker_info['days'] * 86400),
                'priority': 'Low'
            }
            
            cookies.append(cookie)
        
        return cookies
    
    def _generate_tracker_value(self, tracker_name: str) -> str:
        """Generate realistic tracking cookie values"""
        if tracker_name.startswith('_ga'):
            # Google Analytics format
            return f"GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}"
        elif tracker_name == '_fbp':
            # Facebook pixel format
            return f"fb.1.{int(time.time() * 1000)}.{random.randint(100000000, 999999999)}"
        elif tracker_name == 'NID':
            # Google NID format
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            return ''.join(random.choices(chars, k=128))
        else:
            # Generic tracker value
            return base64.b64encode(f"{random.randint(1000000000, 9999999999)}".encode()).decode()
    
    def _add_correlated_cookies(self, domain: str) -> List[Dict]:
        """Add cookies that are correlated with the domain"""
        cookies = []
        
        # Check if we have correlation data for this domain
        if domain in self.cookie_correlations:
            correlated_domains = self.cookie_correlations[domain]
            
            for corr_domain in correlated_domains[:3]:  # Max 3 correlated cookies
                cookie = {
                    'name': f'cross_{hashlib.md5(corr_domain.encode()).hexdigest()[:8]}',
                    'value': base64.b64encode(f"{domain}:{corr_domain}:{time.time()}".encode()).decode(),
                    'domain': corr_domain,
                    'path': '/',
                    'secure': True,
                    'httpOnly': False,
                    'sameSite': 'None',
                    'expires': int(time.time() + 86400 * 30),  # 30 days
                    'priority': 'Low'
                }
                cookies.append(cookie)
        
        return cookies
    
    def save_cookies(self, driver, session_id: str):
        """Save cookies from a browser session"""
        try:
            cookies = driver.get_cookies()
            
            # Process and store cookies
            processed_cookies = []
            for cookie in cookies:
                # Add metadata
                cookie['saved_at'] = time.time()
                cookie['session_id'] = session_id
                processed_cookies.append(cookie)
                
                # Update correlations
                domain = cookie.get('domain', '')
                if domain:
                    self._update_correlations(domain, cookies)
            
            # Save to file
            filename = self.storage_dir / f"cookies_{session_id}.json"
            with open(filename, 'w') as f:
                json.dump(processed_cookies, f, indent=2)
            
            logger.info(f"Saved {len(processed_cookies)} cookies for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False
    
    def load_cookies(self, driver, session_id: str = None, age_cookies: bool = True):
        """Load cookies into a browser session"""
        try:
            if session_id:
                filename = self.storage_dir / f"cookies_{session_id}.json"
                if not filename.exists():
                    logger.warning(f"No cookies found for session {session_id}")
                    return False
                
                with open(filename, 'r') as f:
                    cookies = json.load(f)
            else:
                # Create new aged cookies
                domain = urlparse(driver.current_url).netloc
                cookies = self.create_aged_cookie_jar(domain)
            
            # Age cookies if requested
            if age_cookies and session_id:
                cookies = self._age_existing_cookies(cookies)
            
            # Add cookies to browser
            for cookie in cookies:
                # Remove non-standard fields
                cookie_to_add = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain'),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                }
                
                if 'expires' in cookie:
                    cookie_to_add['expiry'] = cookie['expires']
                
                try:
                    driver.add_cookie(cookie_to_add)
                except Exception as e:
                    logger.warning(f"Could not add cookie {cookie['name']}: {e}")
            
            logger.info(f"Loaded {len(cookies)} cookies")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False
    
    def _age_existing_cookies(self, cookies: List[Dict]) -> List[Dict]:
        """Age existing cookies to make them look more realistic"""
        aged_cookies = []
        
        for cookie in cookies:
            # Calculate age since saved
            if 'saved_at' in cookie:
                age_seconds = time.time() - cookie['saved_at']
                age_days = age_seconds / 86400
                
                # Update lastAccessed time
                if 'lastAccessed' in cookie:
                    cookie['lastAccessed'] = int(time.time() - random.uniform(0, min(86400, age_seconds)))
                
                # Randomly expire some old cookies
                if age_days > 30 and random.random() < 0.1:  # 10% chance to expire old cookies
                    continue
                
                # Update cookie value for some cookies
                if age_days > 7 and random.random() < 0.2:  # 20% chance to update value
                    cookie['value'] = self._generate_cookie_value(age_days)
            
            aged_cookies.append(cookie)
        
        return aged_cookies
    
    def _update_correlations(self, domain: str, all_cookies: List[Dict]):
        """Update cookie correlation map"""
        domains = set()
        for cookie in all_cookies:
            cookie_domain = cookie.get('domain', '')
            if cookie_domain and cookie_domain != domain:
                domains.add(cookie_domain)
        
        if domains:
            self.cookie_correlations[domain] = list(domains)
    
    def implement_storage_access_api(self, driver):
        """Implement Storage Access API handling"""
        script = """
        (function() {
            // Check if Storage Access API is available
            if (document.hasStorageAccess && document.requestStorageAccess) {
                // Override hasStorageAccess
                const originalHasStorageAccess = document.hasStorageAccess;
                document.hasStorageAccess = async function() {
                    // Simulate checking storage access
                    await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
                    
                    // Return based on cookie settings
                    const hasCookies = document.cookie.length > 0;
                    return hasCookies ? true : Math.random() < 0.3; // 30% chance if no cookies
                };
                
                // Override requestStorageAccess
                const originalRequestStorageAccess = document.requestStorageAccess;
                document.requestStorageAccess = async function() {
                    // Simulate user interaction delay
                    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200));
                    
                    // Simulate user approval (80% chance)
                    if (Math.random() < 0.8) {
                        // Grant access
                        return Promise.resolve();
                    } else {
                        // Deny access
                        return Promise.reject(new DOMException('User denied storage access', 'NotAllowedError'));
                    }
                };
                
                console.log('Storage Access API handling injected');
            }
        })();
        """
        
        try:
            driver.execute_script(script)
        except Exception as e:
            logger.warning(f"Could not inject Storage Access API handling: {e}")
    
    def create_first_party_sets(self, domains: List[str]) -> Dict:
        """Create First-Party Sets configuration"""
        primary_domain = domains[0] if domains else 'example.com'
        
        first_party_set = {
            'primary': primary_domain,
            'associatedSites': domains[1:] if len(domains) > 1 else [],
            'serviceSites': [f"cdn.{primary_domain}", f"api.{primary_domain}"],
            'created': int(time.time()),
            'version': 1
        }
        
        return first_party_set
    
    def get_cookie_statistics(self, session_id: str = None) -> Dict:
        """Get statistics about stored cookies"""
        stats = {
            'total_cookies': 0,
            'session_cookies': 0,
            'persistent_cookies': 0,
            'third_party_cookies': 0,
            'tracking_cookies': 0,
            'average_age_days': 0,
            'domains': set()
        }
        
        # Get all cookie files
        if session_id:
            files = [self.storage_dir / f"cookies_{session_id}.json"]
        else:
            files = list(self.storage_dir.glob("cookies_*.json"))
        
        all_cookies = []
        for file in files:
            if file.exists():
                with open(file, 'r') as f:
                    cookies = json.load(f)
                    all_cookies.extend(cookies)
        
        if not all_cookies:
            return stats
        
        # Calculate statistics
        stats['total_cookies'] = len(all_cookies)
        ages = []
        
        for cookie in all_cookies:
            # Session vs persistent
            if cookie.get('session') or 'expires' not in cookie:
                stats['session_cookies'] += 1
            else:
                stats['persistent_cookies'] += 1
            
            # Third-party detection
            domain = cookie.get('domain', '')
            if domain.startswith('.'):
                stats['third_party_cookies'] += 1
            
            # Tracking cookies
            if cookie.get('name') in self.tracking_cookies:
                stats['tracking_cookies'] += 1
            
            # Domain collection
            if domain:
                stats['domains'].add(domain)
            
            # Age calculation
            if 'creation' in cookie:
                age_days = (time.time() - cookie['creation']) / 86400
                ages.append(age_days)
        
        if ages:
            stats['average_age_days'] = sum(ages) / len(ages)
        
        stats['domains'] = list(stats['domains'])
        
        return stats

# Singleton instance
cookie_manager = AdvancedCookieManager()
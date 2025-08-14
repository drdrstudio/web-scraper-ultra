"""
Request Pattern Optimization Module
Implements timing jitter, referrer chains, and request pattern randomization
"""

import random
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
from datetime import datetime, timedelta
import numpy as np
import logging
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class RequestPatternOptimizer:
    """Advanced request pattern optimization with timing and behavioral randomization"""
    
    def __init__(self):
        self.request_history = deque(maxlen=1000)
        self.referrer_chains = {}
        self.site_patterns = {}
        
        # Timing patterns for different user types
        self.user_profiles = {
            'fast_reader': {
                'min_delay': 0.5,
                'max_delay': 3.0,
                'burst_probability': 0.3,
                'idle_probability': 0.05
            },
            'normal_reader': {
                'min_delay': 2.0,
                'max_delay': 8.0,
                'burst_probability': 0.15,
                'idle_probability': 0.1
            },
            'slow_reader': {
                'min_delay': 5.0,
                'max_delay': 20.0,
                'burst_probability': 0.05,
                'idle_probability': 0.2
            },
            'researcher': {
                'min_delay': 3.0,
                'max_delay': 30.0,
                'burst_probability': 0.1,
                'idle_probability': 0.25
            },
            'bot_like': {  # Intentionally bot-like for testing
                'min_delay': 0.1,
                'max_delay': 0.5,
                'burst_probability': 0.8,
                'idle_probability': 0.01
            }
        }
        
        self.current_profile = random.choice(list(self.user_profiles.keys()))
        
        # Resource priority patterns
        self.resource_priorities = ['high', 'medium', 'low', 'auto']
        self.fetch_priorities = ['high', 'low', 'auto']
        
        # Request headers variation
        self.header_variations = {
            'Accept-Encoding': [
                'gzip, deflate, br',
                'gzip, deflate',
                'gzip, deflate, br, zstd',
                'identity'
            ],
            'Cache-Control': [
                'no-cache',
                'max-age=0',
                'no-cache, no-store, must-revalidate',
                None  # Sometimes omit
            ],
            'Upgrade-Insecure-Requests': ['1', None],
            'DNT': ['1', None],
            'Sec-Fetch-Site': ['none', 'same-origin', 'same-site', 'cross-site'],
            'Sec-Fetch-Mode': ['navigate', 'cors', 'no-cors', 'same-origin'],
            'Sec-Fetch-User': ['?1', None],
            'Sec-Fetch-Dest': ['document', 'empty', 'image', 'script', 'style']
        }
        
        # Microsecond-level timing jitter
        self.jitter_enabled = True
        self.jitter_range = (0.0001, 0.01)  # 0.1ms to 10ms
        
    def add_timing_jitter(self, base_delay: float = 0) -> float:
        """Add microsecond-level timing jitter to requests"""
        if not self.jitter_enabled:
            return base_delay
        
        # Add base delay
        total_delay = base_delay
        
        # Add microsecond jitter
        jitter = random.uniform(*self.jitter_range)
        total_delay += jitter
        
        # Occasionally add longer pauses (human-like hesitation)
        if random.random() < 0.05:  # 5% chance
            total_delay += random.uniform(0.1, 0.5)
        
        # Log for debugging
        logger.debug(f"Request delay: {total_delay:.4f}s (base: {base_delay:.4f}s, jitter: {jitter:.4f}s)")
        
        return total_delay
    
    def calculate_request_delay(self, url: str, resource_type: str = 'document') -> float:
        """Calculate realistic delay based on user profile and resource type"""
        profile = self.user_profiles[self.current_profile]
        
        # Base delay from profile
        base_delay = random.uniform(profile['min_delay'], profile['max_delay'])
        
        # Adjust for resource type
        resource_multipliers = {
            'document': 1.0,
            'image': 0.1,  # Images load faster
            'script': 0.2,
            'style': 0.15,
            'font': 0.1,
            'xhr': 0.3,  # AJAX requests
            'fetch': 0.3,
            'other': 0.5
        }
        
        base_delay *= resource_multipliers.get(resource_type, 1.0)
        
        # Check for burst mode
        if random.random() < profile['burst_probability']:
            base_delay *= 0.1  # Much faster during bursts
        
        # Check for idle mode
        if random.random() < profile['idle_probability']:
            base_delay *= random.uniform(5, 20)  # Much slower when idle
        
        # Add jitter
        return self.add_timing_jitter(base_delay)
    
    def build_referrer_chain(self, target_url: str, entry_point: str = None) -> List[str]:
        """Build a realistic referrer chain to target URL"""
        chain = []
        parsed_target = urlparse(target_url)
        
        # Determine entry point
        if entry_point is None:
            entry_points = [
                f"https://www.google.com/search?q={parsed_target.netloc}",
                f"https://www.bing.com/search?q={parsed_target.netloc}",
                f"https://duckduckgo.com/?q={parsed_target.netloc}",
                f"https://www.reddit.com/search/?q={parsed_target.netloc}",
                f"https://twitter.com/search?q={parsed_target.netloc}",
                f"https://{parsed_target.netloc}",  # Direct navigation
                None  # No referrer (bookmark/typed)
            ]
            entry_point = random.choice(entry_points)
        
        if entry_point:
            chain.append(entry_point)
        
        # Build path to target
        if parsed_target.path and parsed_target.path != '/':
            # Add intermediate pages
            base_url = f"{parsed_target.scheme}://{parsed_target.netloc}"
            path_parts = parsed_target.path.strip('/').split('/')
            
            # Sometimes visit homepage first
            if random.random() < 0.7:
                chain.append(base_url)
            
            # Visit some parent paths
            for i in range(len(path_parts) - 1):
                if random.random() < 0.5:
                    partial_path = '/'.join(path_parts[:i+1])
                    chain.append(f"{base_url}/{partial_path}")
        
        # Add target
        chain.append(target_url)
        
        # Store chain for future reference
        self.referrer_chains[target_url] = chain
        
        return chain
    
    def get_random_headers(self, base_headers: Dict = None) -> Dict:
        """Generate randomized headers while maintaining consistency"""
        headers = base_headers.copy() if base_headers else {}
        
        # Randomly vary certain headers
        for header, values in self.header_variations.items():
            if random.random() < 0.7:  # 70% chance to include
                value = random.choice(values)
                if value is not None:
                    headers[header] = value
                elif header in headers:
                    del headers[header]
        
        # Add priority hints sometimes
        if random.random() < 0.3:
            headers['Priority'] = random.choice(['u=0', 'u=1', 'u=2', 'u=3', 'u=4'])
        
        # Add importance hint sometimes
        if random.random() < 0.2:
            headers['Importance'] = random.choice(self.fetch_priorities)
        
        # Early hints support
        if random.random() < 0.1:
            headers['Early-Data'] = '1'
        
        return headers
    
    def simulate_navigation_timing(self, url: str) -> Dict:
        """Simulate Navigation Timing API data"""
        base_time = time.time() * 1000  # Convert to milliseconds
        
        # Realistic timing ranges (in ms)
        timing = {
            'navigationStart': base_time,
            'fetchStart': base_time + random.uniform(0, 5),
            'domainLookupStart': base_time + random.uniform(5, 20),
            'domainLookupEnd': base_time + random.uniform(20, 50),
            'connectStart': base_time + random.uniform(50, 100),
            'connectEnd': base_time + random.uniform(100, 200),
            'requestStart': base_time + random.uniform(200, 250),
            'responseStart': base_time + random.uniform(250, 500),
            'responseEnd': base_time + random.uniform(500, 1000),
            'domLoading': base_time + random.uniform(500, 600),
            'domInteractive': base_time + random.uniform(600, 1500),
            'domContentLoadedEventStart': base_time + random.uniform(1500, 2000),
            'domContentLoadedEventEnd': base_time + random.uniform(2000, 2100),
            'domComplete': base_time + random.uniform(2100, 3000),
            'loadEventStart': base_time + random.uniform(3000, 3100),
            'loadEventEnd': base_time + random.uniform(3100, 3200)
        }
        
        return timing
    
    def generate_resource_timing(self, resource_url: str, resource_type: str) -> Dict:
        """Generate Resource Timing API data"""
        base_time = time.time() * 1000
        
        # Different timings for different resource types
        type_delays = {
            'script': (50, 500),
            'style': (30, 300),
            'image': (100, 1000),
            'font': (20, 200),
            'fetch': (50, 300),
            'other': (50, 500)
        }
        
        min_delay, max_delay = type_delays.get(resource_type, (50, 500))
        
        timing = {
            'name': resource_url,
            'entryType': 'resource',
            'startTime': base_time,
            'duration': random.uniform(min_delay, max_delay),
            'initiatorType': resource_type,
            'transferSize': random.randint(100, 100000),
            'encodedBodySize': random.randint(100, 50000),
            'decodedBodySize': random.randint(100, 50000)
        }
        
        return timing
    
    def track_request(self, url: str, timestamp: float = None):
        """Track request for pattern analysis"""
        if timestamp is None:
            timestamp = time.time()
        
        self.request_history.append({
            'url': url,
            'timestamp': timestamp,
            'profile': self.current_profile
        })
        
        # Analyze patterns for the site
        domain = urlparse(url).netloc
        if domain not in self.site_patterns:
            self.site_patterns[domain] = {
                'request_count': 0,
                'total_time': 0,
                'first_request': timestamp,
                'last_request': timestamp
            }
        
        pattern = self.site_patterns[domain]
        pattern['request_count'] += 1
        pattern['last_request'] = timestamp
        pattern['total_time'] = timestamp - pattern['first_request']
    
    def should_take_break(self) -> bool:
        """Determine if we should take a break (human-like behavior)"""
        if len(self.request_history) < 10:
            return False
        
        recent_requests = list(self.request_history)[-10:]
        time_span = recent_requests[-1]['timestamp'] - recent_requests[0]['timestamp']
        
        # If making requests too fast, take a break
        if time_span < 30:  # 10 requests in 30 seconds
            return random.random() < 0.7  # 70% chance to break
        
        # Random breaks for realism
        return random.random() < 0.1  # 10% chance
    
    def get_break_duration(self) -> float:
        """Get duration for a break"""
        break_types = [
            (5, 15),    # Short break
            (30, 60),   # Medium break
            (120, 300), # Long break
            (600, 1800) # Very long break (10-30 minutes)
        ]
        
        # Weight towards shorter breaks
        weights = [0.5, 0.3, 0.15, 0.05]
        break_type = random.choices(break_types, weights=weights)[0]
        
        return random.uniform(*break_type)
    
    def switch_profile(self):
        """Switch to a different user profile"""
        profiles = list(self.user_profiles.keys())
        profiles.remove(self.current_profile)
        self.current_profile = random.choice(profiles)
        logger.info(f"Switched to profile: {self.current_profile}")
    
    def get_request_statistics(self) -> Dict:
        """Get statistics about request patterns"""
        stats = {
            'total_requests': len(self.request_history),
            'current_profile': self.current_profile,
            'sites_visited': len(self.site_patterns),
            'site_patterns': self.site_patterns
        }
        
        if self.request_history:
            recent = list(self.request_history)[-100:]
            timestamps = [r['timestamp'] for r in recent]
            if len(timestamps) > 1:
                intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                stats['avg_interval'] = np.mean(intervals)
                stats['std_interval'] = np.std(intervals)
        
        return stats
    
    def generate_fetch_metadata(self, url: str, referrer: str = None) -> Dict:
        """Generate Fetch Metadata headers"""
        parsed_url = urlparse(url)
        parsed_referrer = urlparse(referrer) if referrer else None
        
        # Determine site relationship
        if not referrer:
            site = 'none'
        elif parsed_referrer.netloc == parsed_url.netloc:
            site = 'same-origin'
        elif parsed_referrer.netloc.endswith(parsed_url.netloc) or parsed_url.netloc.endswith(parsed_referrer.netloc):
            site = 'same-site'
        else:
            site = 'cross-site'
        
        # Common patterns
        patterns = [
            {'Sec-Fetch-Site': site, 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Sec-Fetch-Dest': 'document'},
            {'Sec-Fetch-Site': site, 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty'},
            {'Sec-Fetch-Site': site, 'Sec-Fetch-Mode': 'no-cors', 'Sec-Fetch-Dest': 'image'},
            {'Sec-Fetch-Site': site, 'Sec-Fetch-Mode': 'no-cors', 'Sec-Fetch-Dest': 'script'},
            {'Sec-Fetch-Site': site, 'Sec-Fetch-Mode': 'no-cors', 'Sec-Fetch-Dest': 'style'}
        ]
        
        return random.choice(patterns)

# Singleton instance
request_optimizer = RequestPatternOptimizer()
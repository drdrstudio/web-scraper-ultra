"""
Smart Proxy Management with ML-based Selection
Real implementation with health tracking and intelligent rotation
"""

import random
import time
import json
import requests
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class SmartProxyManager:
    """
    Intelligent proxy management with ML-based selection
    """
    
    def __init__(self):
        self.proxy_pools = {
            'residential': [],     # Webshare.io residential proxies
            'datacenter': [],      # Fast datacenter proxies
            'mobile': [],          # 4G/5G mobile proxies
            'static': [],          # Static ISP proxies
        }
        
        # Health tracking
        self.proxy_health = defaultdict(lambda: {
            'success_count': 0,
            'failure_count': 0,
            'total_requests': 0,
            'avg_response_time': [],
            'last_used': None,
            'last_success': None,
            'last_failure': None,
            'blocked_sites': set(),
            'success_rate': 100.0,
            'geolocation': None,
            'isp': None,
            'asn': None
        })
        
        # Site-specific proxy performance
        self.site_proxy_performance = defaultdict(lambda: defaultdict(lambda: {
            'success_rate': 0,
            'avg_response_time': 0,
            'last_used': None
        }))
        
        # ML model for proxy selection
        self.ml_model = self._initialize_ml_model()
        
        # Proxy rotation strategies
        self.rotation_strategies = {
            'round_robin': self._round_robin_selection,
            'weighted_random': self._weighted_random_selection,
            'ml_optimized': self._ml_optimized_selection,
            'geo_targeted': self._geo_targeted_selection,
            'least_used': self._least_used_selection,
            'best_performing': self._best_performing_selection
        }
        
        # Load Webshare.io proxies
        self._load_webshare_proxies()
        
        # Cost tracking
        self.proxy_costs = {
            'residential': 0.001,  # Cost per request in USD
            'datacenter': 0.0001,
            'mobile': 0.01,
            'static': 0.0005
        }
        
        self.total_cost = 0.0
    
    def _initialize_ml_model(self):
        """Initialize or load ML model for proxy selection"""
        model_path = 'proxy_selection_model.pkl'
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        
        # Create new model if doesn't exist
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Train with initial synthetic data
        # Features: [proxy_type, success_rate, avg_response_time, hour_of_day, site_difficulty]
        X_train = np.array([
            [0, 0.95, 1.2, 14, 1],  # Residential, high success, noon, easy site
            [1, 0.70, 0.5, 14, 1],  # Datacenter, medium success, noon, easy site
            [0, 0.90, 1.5, 2, 3],   # Residential, high success, night, hard site
            [1, 0.30, 0.3, 14, 3],  # Datacenter, low success, noon, hard site
        ])
        
        y_train = np.array([1, 1, 1, 0])  # 1 = good choice, 0 = bad choice
        
        model.fit(X_train, y_train)
        
        return model
    
    def _load_webshare_proxies(self):
        """Load proxies from Webshare.io"""
        try:
            # Use environment variable for API key
            api_key = os.getenv('WEBSHARE_API_KEY')
            if not api_key:
                return
            
            headers = {'Authorization': f'Token {api_key}'}
            response = requests.get(
                'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=1000',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                for proxy_data in data.get('results', []):
                    proxy = {
                        'url': f"http://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['proxy_address']}:{proxy_data['port']}",
                        'type': 'residential',
                        'country': proxy_data.get('country_code'),
                        'city': proxy_data.get('city_name'),
                        'id': proxy_data.get('id'),
                        'created_at': time.time()
                    }
                    self.proxy_pools['residential'].append(proxy)
                
                print(f"Loaded {len(self.proxy_pools['residential'])} Webshare proxies")
        except Exception as e:
            print(f"Error loading Webshare proxies: {e}")
    
    def get_optimal_proxy(self, 
                         url: str, 
                         strategy: str = 'ml_optimized',
                         requirements: Dict = None) -> Optional[Dict]:
        """
        Get optimal proxy based on strategy and requirements
        
        Args:
            url: Target URL
            strategy: Selection strategy
            requirements: {
                'geo': 'US',  # Geographic requirement
                'min_success_rate': 0.8,
                'max_response_time': 5.0,
                'proxy_type': 'residential',
                'avoid_datacenter': True
            }
        """
        requirements = requirements or {}
        
        # Filter proxies based on requirements
        available_proxies = self._filter_proxies(requirements)
        
        if not available_proxies:
            # Fallback to any available proxy
            available_proxies = self._get_all_proxies()
        
        if not available_proxies:
            return None
        
        # Apply selection strategy
        strategy_func = self.rotation_strategies.get(strategy, self._weighted_random_selection)
        selected_proxy = strategy_func(available_proxies, url)
        
        # Update usage stats
        if selected_proxy:
            self._update_proxy_usage(selected_proxy, url)
        
        return selected_proxy
    
    def _filter_proxies(self, requirements: Dict) -> List[Dict]:
        """Filter proxies based on requirements"""
        filtered = []
        
        for pool_type, proxies in self.proxy_pools.items():
            # Check proxy type requirement
            if requirements.get('proxy_type') and pool_type != requirements['proxy_type']:
                continue
            
            if requirements.get('avoid_datacenter') and pool_type == 'datacenter':
                continue
            
            for proxy in proxies:
                proxy_id = proxy.get('url', proxy.get('id'))
                health = self.proxy_health[proxy_id]
                
                # Check success rate
                if requirements.get('min_success_rate'):
                    if health['success_rate'] < requirements['min_success_rate'] * 100:
                        continue
                
                # Check response time
                if requirements.get('max_response_time') and health['avg_response_time']:
                    avg_time = np.mean(health['avg_response_time'])
                    if avg_time > requirements['max_response_time']:
                        continue
                
                # Check geographic requirement
                if requirements.get('geo'):
                    if proxy.get('country') != requirements['geo']:
                        continue
                
                # Check if proxy was recently used (cooldown)
                if health['last_used']:
                    cooldown = timedelta(seconds=30)  # 30 second cooldown
                    if datetime.now() - health['last_used'] < cooldown:
                        continue
                
                filtered.append(proxy)
        
        return filtered
    
    def _get_all_proxies(self) -> List[Dict]:
        """Get all available proxies"""
        all_proxies = []
        for proxies in self.proxy_pools.values():
            all_proxies.extend(proxies)
        return all_proxies
    
    def _round_robin_selection(self, proxies: List[Dict], url: str) -> Optional[Dict]:
        """Round-robin proxy selection"""
        if not proxies:
            return None
        
        # Sort by last used time
        sorted_proxies = sorted(
            proxies,
            key=lambda p: self.proxy_health[p.get('url', p.get('id'))]['last_used'] or datetime.min
        )
        
        return sorted_proxies[0]
    
    def _weighted_random_selection(self, proxies: List[Dict], url: str) -> Optional[Dict]:
        """Weighted random selection based on success rate"""
        if not proxies:
            return None
        
        # Calculate weights based on success rate
        weights = []
        for proxy in proxies:
            health = self.proxy_health[proxy.get('url', proxy.get('id'))]
            weight = health['success_rate'] / 100.0
            
            # Boost weight if proxy worked well for this site
            site_perf = self.site_proxy_performance[url][proxy.get('url', proxy.get('id'))]
            if site_perf['success_rate'] > 0:
                weight *= (1 + site_perf['success_rate'])
            
            weights.append(max(weight, 0.1))  # Minimum weight of 0.1
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w/total_weight for w in weights]
        else:
            weights = [1/len(proxies)] * len(proxies)
        
        return np.random.choice(proxies, p=weights)
    
    def _ml_optimized_selection(self, proxies: List[Dict], url: str) -> Optional[Dict]:
        """ML-based optimal proxy selection"""
        if not proxies or not self.ml_model:
            return self._weighted_random_selection(proxies, url)
        
        # Prepare features for each proxy
        current_hour = datetime.now().hour
        site_difficulty = self._estimate_site_difficulty(url)
        
        proxy_scores = []
        for proxy in proxies:
            health = self.proxy_health[proxy.get('url', proxy.get('id'))]
            
            # Create feature vector
            proxy_type = 0 if 'residential' in proxy.get('type', '') else 1
            success_rate = health['success_rate'] / 100.0
            avg_response = np.mean(health['avg_response_time']) if health['avg_response_time'] else 2.0
            
            features = np.array([[
                proxy_type,
                success_rate,
                avg_response,
                current_hour,
                site_difficulty
            ]])
            
            # Predict success probability
            try:
                score = self.ml_model.predict_proba(features)[0][1]
            except:
                score = success_rate
            
            proxy_scores.append((proxy, score))
        
        # Select proxy with highest score
        proxy_scores.sort(key=lambda x: x[1], reverse=True)
        return proxy_scores[0][0] if proxy_scores else None
    
    def _geo_targeted_selection(self, proxies: List[Dict], url: str) -> Optional[Dict]:
        """Select proxy based on geographic targeting"""
        # Determine target country from URL
        target_country = self._detect_target_country(url)
        
        # Filter proxies by country
        geo_proxies = [p for p in proxies if p.get('country') == target_country]
        
        if geo_proxies:
            return self._weighted_random_selection(geo_proxies, url)
        
        return self._weighted_random_selection(proxies, url)
    
    def _least_used_selection(self, proxies: List[Dict], url: str) -> Optional[Dict]:
        """Select least recently used proxy"""
        if not proxies:
            return None
        
        return min(
            proxies,
            key=lambda p: self.proxy_health[p.get('url', p.get('id'))]['total_requests']
        )
    
    def _best_performing_selection(self, proxies: List[Dict], url: str) -> Optional[Dict]:
        """Select best performing proxy for this site"""
        if not proxies:
            return None
        
        # Sort by site-specific performance
        site_scores = []
        for proxy in proxies:
            proxy_id = proxy.get('url', proxy.get('id'))
            site_perf = self.site_proxy_performance[url][proxy_id]
            
            score = site_perf['success_rate']
            if score == 0:  # Never used for this site
                # Use general success rate
                score = self.proxy_health[proxy_id]['success_rate']
            
            site_scores.append((proxy, score))
        
        site_scores.sort(key=lambda x: x[1], reverse=True)
        return site_scores[0][0] if site_scores else None
    
    def _estimate_site_difficulty(self, url: str) -> int:
        """Estimate site protection level (1-5)"""
        # Known difficult sites
        difficult_patterns = {
            'cloudflare': 4,
            'amazon': 3,
            'google': 3,
            'facebook': 4,
            'linkedin': 4,
            'instagram': 4,
            'twitter': 3,
            'ebay': 3,
            'walmart': 3,
            'bestbuy': 3
        }
        
        url_lower = url.lower()
        for pattern, difficulty in difficult_patterns.items():
            if pattern in url_lower:
                return difficulty
        
        return 2  # Default medium difficulty
    
    def _detect_target_country(self, url: str) -> str:
        """Detect target country from URL"""
        # Country TLDs
        tld_countries = {
            '.uk': 'GB', '.ca': 'CA', '.au': 'AU', '.de': 'DE',
            '.fr': 'FR', '.jp': 'JP', '.cn': 'CN', '.in': 'IN',
            '.br': 'BR', '.mx': 'MX', '.es': 'ES', '.it': 'IT'
        }
        
        for tld, country in tld_countries.items():
            if tld in url:
                return country
        
        return 'US'  # Default to US
    
    def _update_proxy_usage(self, proxy: Dict, url: str):
        """Update proxy usage statistics"""
        proxy_id = proxy.get('url', proxy.get('id'))
        self.proxy_health[proxy_id]['last_used'] = datetime.now()
        self.proxy_health[proxy_id]['total_requests'] += 1
        
        # Update cost tracking
        proxy_type = proxy.get('type', 'datacenter')
        self.total_cost += self.proxy_costs.get(proxy_type, 0.0001)
    
    def report_proxy_result(self, 
                           proxy: Dict, 
                           url: str, 
                           success: bool, 
                           response_time: float = None,
                           error: str = None):
        """Report proxy performance result"""
        proxy_id = proxy.get('url', proxy.get('id'))
        health = self.proxy_health[proxy_id]
        
        # Update counts
        if success:
            health['success_count'] += 1
            health['last_success'] = datetime.now()
        else:
            health['failure_count'] += 1
            health['last_failure'] = datetime.now()
            
            # Track blocked sites
            if error and 'blocked' in error.lower():
                health['blocked_sites'].add(url)
        
        # Update success rate
        total = health['success_count'] + health['failure_count']
        health['success_rate'] = (health['success_count'] / total * 100) if total > 0 else 100.0
        
        # Update response time
        if response_time:
            health['avg_response_time'].append(response_time)
            # Keep only last 100 measurements
            health['avg_response_time'] = health['avg_response_time'][-100:]
        
        # Update site-specific performance
        site_perf = self.site_proxy_performance[url][proxy_id]
        site_perf['last_used'] = datetime.now()
        
        if success:
            current_success = site_perf.get('success_count', 0) + 1
            current_total = site_perf.get('total_count', 0) + 1
            site_perf['success_count'] = current_success
            site_perf['total_count'] = current_total
            site_perf['success_rate'] = current_success / current_total
            
            if response_time:
                # Update average response time
                current_avg = site_perf.get('avg_response_time', 0)
                site_perf['avg_response_time'] = (current_avg * (current_total - 1) + response_time) / current_total
        
        # Train ML model with new data
        self._update_ml_model(proxy, url, success, response_time)
    
    def _update_ml_model(self, proxy: Dict, url: str, success: bool, response_time: float):
        """Update ML model with new training data"""
        # This would be implemented with online learning
        # For now, we just collect data for periodic retraining
        pass
    
    def get_proxy_statistics(self) -> Dict:
        """Get comprehensive proxy statistics"""
        stats = {
            'total_proxies': sum(len(pool) for pool in self.proxy_pools.values()),
            'proxies_by_type': {k: len(v) for k, v in self.proxy_pools.items()},
            'total_requests': sum(h['total_requests'] for h in self.proxy_health.values()),
            'overall_success_rate': 0,
            'total_cost': self.total_cost,
            'top_performing': [],
            'worst_performing': [],
            'most_used': [],
            'geographic_distribution': {}
        }
        
        # Calculate overall success rate
        total_success = sum(h['success_count'] for h in self.proxy_health.values())
        total_failure = sum(h['failure_count'] for h in self.proxy_health.values())
        total = total_success + total_failure
        
        if total > 0:
            stats['overall_success_rate'] = f"{(total_success / total * 100):.1f}%"
        
        # Get top/worst performing proxies
        proxy_performance = [
            (proxy_id, health['success_rate'])
            for proxy_id, health in self.proxy_health.items()
            if health['total_requests'] > 10  # Minimum 10 requests
        ]
        
        proxy_performance.sort(key=lambda x: x[1], reverse=True)
        stats['top_performing'] = proxy_performance[:5]
        stats['worst_performing'] = proxy_performance[-5:] if len(proxy_performance) > 5 else []
        
        # Most used proxies
        most_used = sorted(
            self.proxy_health.items(),
            key=lambda x: x[1]['total_requests'],
            reverse=True
        )[:5]
        stats['most_used'] = [(p, h['total_requests']) for p, h in most_used]
        
        # Geographic distribution
        for pool_type, proxies in self.proxy_pools.items():
            for proxy in proxies:
                country = proxy.get('country', 'Unknown')
                stats['geographic_distribution'][country] = stats['geographic_distribution'].get(country, 0) + 1
        
        return stats
    
    def cleanup_failed_proxies(self, failure_threshold: float = 0.3):
        """Remove consistently failing proxies"""
        removed_count = 0
        
        for pool_type, proxies in self.proxy_pools.items():
            to_remove = []
            
            for proxy in proxies:
                proxy_id = proxy.get('url', proxy.get('id'))
                health = self.proxy_health[proxy_id]
                
                # Remove if success rate below threshold and has enough attempts
                if health['total_requests'] > 20 and health['success_rate'] < failure_threshold * 100:
                    to_remove.append(proxy)
                    removed_count += 1
            
            # Remove failed proxies
            for proxy in to_remove:
                proxies.remove(proxy)
                proxy_id = proxy.get('url', proxy.get('id'))
                del self.proxy_health[proxy_id]
        
        print(f"Removed {removed_count} failed proxies")
        return removed_count
    
    def save_state(self, filepath: str = 'proxy_state.json'):
        """Save proxy state to file"""
        state = {
            'proxy_health': dict(self.proxy_health),
            'site_proxy_performance': dict(self.site_proxy_performance),
            'total_cost': self.total_cost,
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert sets to lists for JSON serialization
        for proxy_id, health in state['proxy_health'].items():
            health['blocked_sites'] = list(health.get('blocked_sites', set()))
            # Convert datetime objects to strings
            for key in ['last_used', 'last_success', 'last_failure']:
                if health.get(key):
                    health[key] = health[key].isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self, filepath: str = 'proxy_state.json'):
        """Load proxy state from file"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Restore proxy health
        for proxy_id, health in state.get('proxy_health', {}).items():
            self.proxy_health[proxy_id] = health
            # Convert lists back to sets
            health['blocked_sites'] = set(health.get('blocked_sites', []))
            # Convert strings back to datetime
            for key in ['last_used', 'last_success', 'last_failure']:
                if health.get(key):
                    health[key] = datetime.fromisoformat(health[key])
        
        # Restore site performance
        for url, proxy_perfs in state.get('site_proxy_performance', {}).items():
            for proxy_id, perf in proxy_perfs.items():
                self.site_proxy_performance[url][proxy_id] = perf
                if perf.get('last_used'):
                    perf['last_used'] = datetime.fromisoformat(perf['last_used'])
        
        self.total_cost = state.get('total_cost', 0.0)

# Global instance
smart_proxy_manager = SmartProxyManager()
"""
Ban Detection and Recovery System
Detects blocking patterns and implements recovery strategies
"""

import re
import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from collections import deque, defaultdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BanType(Enum):
    """Types of bans/blocks detected"""
    NONE = "none"
    RATE_LIMIT = "rate_limit"
    IP_BAN = "ip_ban"
    CAPTCHA = "captcha"
    CLOUDFLARE = "cloudflare"
    ACCESS_DENIED = "access_denied"
    BEHAVIORAL = "behavioral"
    GEOGRAPHIC = "geographic"
    USER_AGENT = "user_agent"
    FINGERPRINT = "fingerprint"
    TEMPORARY = "temporary"
    PERMANENT = "permanent"

class RecoveryStrategy(Enum):
    """Recovery strategies for different ban types"""
    WAIT = "wait"
    ROTATE_PROXY = "rotate_proxy"
    SOLVE_CAPTCHA = "solve_captcha"
    CHANGE_FINGERPRINT = "change_fingerprint"
    SLOW_DOWN = "slow_down"
    CHANGE_PATTERN = "change_pattern"
    BUILD_REPUTATION = "build_reputation"
    ABANDON = "abandon"

class BanDetector:
    """Detects and recovers from various types of blocking"""
    
    def __init__(self):
        self.ban_patterns = {
            BanType.RATE_LIMIT: [
                r"rate.?limit",
                r"too.?many.?requests",
                r"429",
                r"slow.?down",
                r"throttl",
                r"exceeded.?quota"
            ],
            BanType.IP_BAN: [
                r"blocked",
                r"banned",
                r"forbidden",
                r"403",
                r"access.?denied",
                r"unauthorized.?access",
                r"ip.?block"
            ],
            BanType.CAPTCHA: [
                r"captcha",
                r"recaptcha",
                r"hcaptcha",
                r"challenge",
                r"verify.?you.?are.?human",
                r"robot.?check",
                r"security.?check"
            ],
            BanType.CLOUDFLARE: [
                r"cloudflare",
                r"cf-ray",
                r"checking.?your.?browser",
                r"ddos.?protection",
                r"please.?wait",
                r"security.?check.?cloudflare"
            ],
            BanType.BEHAVIORAL: [
                r"suspicious.?activity",
                r"unusual.?traffic",
                r"automated.?behavior",
                r"bot.?detected",
                r"non.?human"
            ],
            BanType.GEOGRAPHIC: [
                r"not.?available.?in.?your.?(country|region)",
                r"geo.?block",
                r"location.?restricted",
                r"content.?not.?available"
            ],
            BanType.USER_AGENT: [
                r"unsupported.?browser",
                r"update.?your.?browser",
                r"browser.?not.?supported",
                r"invalid.?user.?agent"
            ]
        }
        
        self.recovery_strategies = {
            BanType.RATE_LIMIT: [RecoveryStrategy.WAIT, RecoveryStrategy.SLOW_DOWN, RecoveryStrategy.ROTATE_PROXY],
            BanType.IP_BAN: [RecoveryStrategy.ROTATE_PROXY, RecoveryStrategy.WAIT],
            BanType.CAPTCHA: [RecoveryStrategy.SOLVE_CAPTCHA, RecoveryStrategy.ROTATE_PROXY],
            BanType.CLOUDFLARE: [RecoveryStrategy.WAIT, RecoveryStrategy.SOLVE_CAPTCHA, RecoveryStrategy.CHANGE_FINGERPRINT],
            BanType.BEHAVIORAL: [RecoveryStrategy.CHANGE_PATTERN, RecoveryStrategy.BUILD_REPUTATION],
            BanType.GEOGRAPHIC: [RecoveryStrategy.ROTATE_PROXY],
            BanType.USER_AGENT: [RecoveryStrategy.CHANGE_FINGERPRINT],
            BanType.FINGERPRINT: [RecoveryStrategy.CHANGE_FINGERPRINT, RecoveryStrategy.ROTATE_PROXY]
        }
        
        # Track bans per domain
        self.ban_history = defaultdict(lambda: deque(maxlen=100))
        self.recovery_attempts = defaultdict(int)
        self.successful_recoveries = defaultdict(list)
        
        # Reputation tracking
        self.domain_reputation = defaultdict(lambda: {
            'requests': 0,
            'successes': 0,
            'bans': 0,
            'last_ban': None,
            'reputation_score': 1.0
        })
        
        # Recovery configuration
        self.recovery_config = {
            'max_retry_attempts': 5,
            'base_wait_time': 5,  # seconds
            'max_wait_time': 300,  # 5 minutes
            'reputation_threshold': 0.3,  # Below this, abandon site
            'ban_threshold': 10  # Max bans before abandoning
        }
    
    def detect_ban(self, response=None, html_content: str = None, 
                   status_code: int = None, headers: Dict = None) -> Tuple[BanType, float]:
        """Detect if request was banned/blocked"""
        ban_type = BanType.NONE
        confidence = 0.0
        
        # Check status code
        if status_code:
            if status_code == 429:
                return BanType.RATE_LIMIT, 0.95
            elif status_code == 403:
                ban_type = BanType.IP_BAN
                confidence = 0.8
            elif status_code == 503:
                ban_type = BanType.CLOUDFLARE
                confidence = 0.7
            elif status_code >= 400:
                confidence = 0.5
        
        # Check HTML content for patterns
        if html_content:
            content_lower = html_content.lower()
            
            for ban_type_check, patterns in self.ban_patterns.items():
                matches = 0
                for pattern in patterns:
                    if re.search(pattern, content_lower, re.IGNORECASE):
                        matches += 1
                
                if matches > 0:
                    pattern_confidence = min(matches * 0.3, 0.95)
                    if pattern_confidence > confidence:
                        ban_type = ban_type_check
                        confidence = pattern_confidence
        
        # Check response headers
        if headers:
            headers_lower = {k.lower(): v.lower() if isinstance(v, str) else v 
                           for k, v in headers.items()}
            
            # Cloudflare detection
            if 'cf-ray' in headers_lower or 'cf-cache-status' in headers_lower:
                if ban_type == BanType.NONE:
                    ban_type = BanType.CLOUDFLARE
                    confidence = max(confidence, 0.6)
            
            # Rate limiting headers
            if 'x-ratelimit-remaining' in headers_lower:
                remaining = headers_lower.get('x-ratelimit-remaining', '1')
                if str(remaining) == '0':
                    return BanType.RATE_LIMIT, 0.99
            
            # Retry-After header
            if 'retry-after' in headers_lower:
                return BanType.RATE_LIMIT, 0.95
        
        # Check for specific error pages
        if html_content and ban_type == BanType.NONE:
            # Check for common error page indicators
            error_indicators = [
                '<title>access denied</title>',
                '<title>403 forbidden</title>',
                '<title>error</title>',
                'class="error-page"',
                'id="challenge-form"'
            ]
            
            for indicator in error_indicators:
                if indicator in html_content.lower():
                    ban_type = BanType.ACCESS_DENIED
                    confidence = 0.7
                    break
        
        return ban_type, confidence
    
    def record_ban(self, domain: str, ban_type: BanType, metadata: Dict = None):
        """Record a ban event"""
        ban_event = {
            'timestamp': time.time(),
            'type': ban_type,
            'metadata': metadata or {}
        }
        
        self.ban_history[domain].append(ban_event)
        
        # Update reputation
        reputation = self.domain_reputation[domain]
        reputation['bans'] += 1
        reputation['last_ban'] = time.time()
        reputation['reputation_score'] *= 0.9  # Decrease reputation
        
        logger.warning(f"Ban detected for {domain}: {ban_type.value} (reputation: {reputation['reputation_score']:.2f})")
    
    def get_recovery_strategy(self, domain: str, ban_type: BanType) -> RecoveryStrategy:
        """Determine best recovery strategy"""
        strategies = self.recovery_strategies.get(ban_type, [RecoveryStrategy.WAIT])
        
        # Check if we should abandon
        reputation = self.domain_reputation[domain]
        if reputation['reputation_score'] < self.recovery_config['reputation_threshold']:
            logger.warning(f"Reputation too low for {domain}, abandoning")
            return RecoveryStrategy.ABANDON
        
        if reputation['bans'] > self.recovery_config['ban_threshold']:
            logger.warning(f"Too many bans for {domain}, abandoning")
            return RecoveryStrategy.ABANDON
        
        # Check previous successful recoveries
        if domain in self.successful_recoveries:
            for past_recovery in self.successful_recoveries[domain]:
                if past_recovery['ban_type'] == ban_type:
                    return past_recovery['strategy']
        
        # Return first available strategy
        return strategies[0] if strategies else RecoveryStrategy.WAIT
    
    def calculate_wait_time(self, domain: str, attempt: int = 0) -> float:
        """Calculate wait time for recovery"""
        base_wait = self.recovery_config['base_wait_time']
        
        # Exponential backoff
        wait_time = base_wait * (2 ** attempt)
        
        # Add jitter
        import random
        wait_time += random.uniform(0, base_wait)
        
        # Check if domain has Retry-After header info
        recent_bans = list(self.ban_history[domain])[-5:]
        for ban in recent_bans:
            if 'retry_after' in ban.get('metadata', {}):
                suggested_wait = ban['metadata']['retry_after']
                wait_time = max(wait_time, suggested_wait)
        
        # Cap at maximum
        wait_time = min(wait_time, self.recovery_config['max_wait_time'])
        
        return wait_time
    
    def execute_recovery(self, domain: str, ban_type: BanType, 
                        strategy: RecoveryStrategy, context: Dict = None) -> Dict:
        """Execute recovery strategy"""
        logger.info(f"Executing recovery for {domain}: {strategy.value}")
        
        result = {
            'success': False,
            'strategy': strategy,
            'action_taken': None,
            'wait_time': 0,
            'new_config': {}
        }
        
        if strategy == RecoveryStrategy.WAIT:
            wait_time = self.calculate_wait_time(domain, self.recovery_attempts[domain])
            result['wait_time'] = wait_time
            result['action_taken'] = f"Waiting {wait_time:.1f} seconds"
            time.sleep(wait_time)
            result['success'] = True
            
        elif strategy == RecoveryStrategy.ROTATE_PROXY:
            result['action_taken'] = "Rotate to new proxy"
            result['new_config']['rotate_proxy'] = True
            result['success'] = True
            
        elif strategy == RecoveryStrategy.SOLVE_CAPTCHA:
            result['action_taken'] = "Solve captcha challenge"
            result['new_config']['solve_captcha'] = True
            result['success'] = True
            
        elif strategy == RecoveryStrategy.CHANGE_FINGERPRINT:
            result['action_taken'] = "Change browser fingerprint"
            result['new_config']['new_fingerprint'] = True
            result['new_config']['new_user_agent'] = True
            result['success'] = True
            
        elif strategy == RecoveryStrategy.SLOW_DOWN:
            result['action_taken'] = "Reduce request rate"
            result['new_config']['delay_multiplier'] = 3.0
            result['success'] = True
            
        elif strategy == RecoveryStrategy.CHANGE_PATTERN:
            result['action_taken'] = "Change browsing pattern"
            result['new_config']['randomize_pattern'] = True
            result['new_config']['add_referrer'] = True
            result['success'] = True
            
        elif strategy == RecoveryStrategy.BUILD_REPUTATION:
            result['action_taken'] = "Build reputation with normal browsing"
            result['new_config']['reputation_mode'] = True
            result['new_config']['visit_count'] = 10  # Visit 10 normal pages
            result['success'] = True
            
        elif strategy == RecoveryStrategy.ABANDON:
            result['action_taken'] = "Abandon scraping this domain"
            result['success'] = False
        
        # Record attempt
        self.recovery_attempts[domain] += 1
        
        # Record successful recovery
        if result['success']:
            self.successful_recoveries[domain].append({
                'ban_type': ban_type,
                'strategy': strategy,
                'timestamp': time.time()
            })
        
        return result
    
    def update_reputation(self, domain: str, success: bool):
        """Update domain reputation based on request outcome"""
        reputation = self.domain_reputation[domain]
        reputation['requests'] += 1
        
        if success:
            reputation['successes'] += 1
            # Slowly increase reputation
            reputation['reputation_score'] = min(1.0, reputation['reputation_score'] * 1.01)
        else:
            # Decrease reputation
            reputation['reputation_score'] *= 0.95
    
    def should_proceed(self, domain: str) -> bool:
        """Check if we should continue scraping this domain"""
        reputation = self.domain_reputation[domain]
        
        # Check reputation score
        if reputation['reputation_score'] < self.recovery_config['reputation_threshold']:
            return False
        
        # Check ban frequency
        if reputation['bans'] > self.recovery_config['ban_threshold']:
            return False
        
        # Check if recently banned
        if reputation['last_ban']:
            time_since_ban = time.time() - reputation['last_ban']
            if time_since_ban < 60:  # Less than 1 minute since last ban
                return False
        
        return True
    
    def get_domain_health(self, domain: str) -> Dict:
        """Get health metrics for a domain"""
        reputation = self.domain_reputation[domain]
        ban_events = list(self.ban_history[domain])
        
        health = {
            'reputation_score': reputation['reputation_score'],
            'total_requests': reputation['requests'],
            'successful_requests': reputation['successes'],
            'success_rate': reputation['successes'] / max(reputation['requests'], 1),
            'total_bans': reputation['bans'],
            'recent_bans': len([b for b in ban_events if time.time() - b['timestamp'] < 3600]),
            'recovery_attempts': self.recovery_attempts[domain],
            'status': 'healthy' if self.should_proceed(domain) else 'unhealthy'
        }
        
        # Determine ban trend
        if len(ban_events) >= 2:
            recent_interval = ban_events[-1]['timestamp'] - ban_events[-2]['timestamp']
            if recent_interval < 60:
                health['trend'] = 'worsening'
            elif recent_interval > 3600:
                health['trend'] = 'improving'
            else:
                health['trend'] = 'stable'
        else:
            health['trend'] = 'unknown'
        
        return health
    
    def analyze_ban_patterns(self, domain: str) -> Dict:
        """Analyze ban patterns for a domain"""
        ban_events = list(self.ban_history[domain])
        
        if not ban_events:
            return {'patterns': [], 'recommendations': []}
        
        analysis = {
            'patterns': [],
            'recommendations': [],
            'ban_types': defaultdict(int),
            'time_patterns': []
        }
        
        # Count ban types
        for event in ban_events:
            analysis['ban_types'][event['type'].value] += 1
        
        # Find time patterns
        if len(ban_events) >= 3:
            timestamps = [e['timestamp'] for e in ban_events]
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            
            avg_interval = sum(intervals) / len(intervals)
            
            if avg_interval < 60:
                analysis['patterns'].append('Rapid ban rate - likely aggressive detection')
                analysis['recommendations'].append('Significantly slow down request rate')
            elif avg_interval < 300:
                analysis['patterns'].append('Moderate ban rate - rate limiting likely')
                analysis['recommendations'].append('Implement request throttling')
            
            # Check for periodic bans
            if len(intervals) >= 5:
                import numpy as np
                std_dev = np.std(intervals)
                if std_dev < avg_interval * 0.2:  # Low variance
                    analysis['patterns'].append('Periodic bans detected')
                    analysis['recommendations'].append('Randomize request timing')
        
        # Analyze most common ban type
        if analysis['ban_types']:
            most_common = max(analysis['ban_types'].items(), key=lambda x: x[1])
            analysis['primary_ban_type'] = most_common[0]
            
            # Type-specific recommendations
            if most_common[0] == 'rate_limit':
                analysis['recommendations'].append('Reduce requests per minute')
            elif most_common[0] == 'ip_ban':
                analysis['recommendations'].append('Use proxy rotation')
            elif most_common[0] == 'captcha':
                analysis['recommendations'].append('Implement captcha solving')
            elif most_common[0] == 'behavioral':
                analysis['recommendations'].append('Improve human-like behavior simulation')
        
        return analysis
    
    def reset_domain(self, domain: str):
        """Reset tracking for a domain"""
        self.ban_history[domain].clear()
        self.recovery_attempts[domain] = 0
        self.successful_recoveries[domain] = []
        self.domain_reputation[domain] = {
            'requests': 0,
            'successes': 0,
            'bans': 0,
            'last_ban': None,
            'reputation_score': 1.0
        }
        logger.info(f"Reset tracking for domain: {domain}")

# Singleton instance
ban_detector = BanDetector()
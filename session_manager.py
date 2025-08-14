"""
Advanced Session Persistence Manager
Maintains long-lived browser sessions with cookies, auth, and state
"""

import os
import json
import pickle
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from collections import defaultdict

class SessionManager:
    """
    Manages persistent browser sessions and authentication states
    """
    
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = session_dir
        os.makedirs(session_dir, exist_ok=True)
        
        # Active sessions
        self.active_sessions = {}
        
        # Session pools by site
        self.session_pools = defaultdict(list)
        
        # Authentication states
        self.auth_states = {}
        
        # Cookie storage
        self.cookie_jars = defaultdict(list)
        
        # Session activity tracking
        self.session_activity = defaultdict(lambda: {
            'created_at': None,
            'last_active': None,
            'total_requests': 0,
            'auth_status': False,
            'site': None,
            'browser_type': None
        })
        
        # Heartbeat thread to keep sessions alive
        self.heartbeat_thread = None
        self.running = False
        
        # Load saved sessions
        self._load_saved_sessions()
    
    def create_persistent_session(self,
                                 site: str,
                                 browser_type: str = 'chrome',
                                 profile_dir: Optional[str] = None,
                                 auth_info: Optional[Dict] = None) -> str:
        """
        Create a new persistent session
        
        Args:
            site: Target website
            browser_type: 'chrome', 'firefox', 'edge'
            profile_dir: Browser profile directory
            auth_info: {'username': '', 'password': '', 'method': 'form'}
        """
        session_id = f"{site}_{browser_type}_{int(time.time())}"
        
        # Create browser with persistent profile
        if browser_type == 'chrome':
            driver = self._create_chrome_session(profile_dir)
        elif browser_type == 'firefox':
            driver = self._create_firefox_session(profile_dir)
        else:
            driver = self._create_chrome_session(profile_dir)
        
        # Store session
        self.active_sessions[session_id] = {
            'driver': driver,
            'site': site,
            'browser_type': browser_type,
            'profile_dir': profile_dir,
            'cookies': [],
            'local_storage': {},
            'session_storage': {},
            'auth_info': auth_info
        }
        
        # Initialize activity tracking
        self.session_activity[session_id].update({
            'created_at': datetime.now(),
            'last_active': datetime.now(),
            'site': site,
            'browser_type': browser_type
        })
        
        # Perform authentication if needed
        if auth_info:
            self.authenticate_session(session_id, auth_info)
        
        # Add to pool
        self.session_pools[site].append(session_id)
        
        return session_id
    
    def _create_chrome_session(self, profile_dir: Optional[str] = None) -> webdriver.Chrome:
        """Create Chrome session with persistent profile"""
        from selenium.webdriver.chrome.options import Options
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        
        # Use persistent profile
        if profile_dir:
            options.add_argument(f'--user-data-dir={profile_dir}')
        else:
            # Create new profile
            profile_path = os.path.join(self.session_dir, f"chrome_profile_{int(time.time())}")
            os.makedirs(profile_path, exist_ok=True)
            options.add_argument(f'--user-data-dir={profile_path}')
        
        # Standard stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Keep session alive
        options.add_argument('--keep-alive-for-test')
        
        driver = uc.Chrome(options=options, version_main=None)
        return driver
    
    def _create_firefox_session(self, profile_dir: Optional[str] = None) -> webdriver.Firefox:
        """Create Firefox session with persistent profile"""
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
        
        options = Options()
        
        if profile_dir:
            profile = FirefoxProfile(profile_dir)
        else:
            profile = FirefoxProfile()
            
        # Stealth settings
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        
        driver = webdriver.Firefox(firefox_profile=profile, options=options)
        return driver
    
    def get_session(self, site: str, require_auth: bool = False) -> Optional[str]:
        """
        Get an available session for a site
        
        Args:
            site: Target website
            require_auth: Whether session must be authenticated
        """
        available_sessions = self.session_pools.get(site, [])
        
        for session_id in available_sessions:
            if session_id not in self.active_sessions:
                continue
            
            activity = self.session_activity[session_id]
            
            # Check if authentication is required
            if require_auth and not activity['auth_status']:
                continue
            
            # Check if session is still alive
            if self._is_session_alive(session_id):
                # Update activity
                activity['last_active'] = datetime.now()
                activity['total_requests'] += 1
                return session_id
        
        # No available session, create new one
        return self.create_persistent_session(site)
    
    def _is_session_alive(self, session_id: str) -> bool:
        """Check if session is still alive"""
        if session_id not in self.active_sessions:
            return False
        
        try:
            session = self.active_sessions[session_id]
            driver = session['driver']
            
            # Try to get current URL
            _ = driver.current_url
            return True
        except:
            # Session is dead, remove it
            self._cleanup_session(session_id)
            return False
    
    def authenticate_session(self, session_id: str, auth_info: Dict) -> bool:
        """
        Authenticate a session
        
        Args:
            session_id: Session identifier
            auth_info: {
                'url': 'login page URL',
                'username': '',
                'password': '',
                'method': 'form|oauth|saml',
                'selectors': {
                    'username': '#username',
                    'password': '#password',
                    'submit': '#login-button'
                }
            }
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        driver = session['driver']
        
        try:
            # Navigate to login page
            driver.get(auth_info['url'])
            time.sleep(2)
            
            if auth_info['method'] == 'form':
                # Form-based authentication
                username_field = driver.find_element(
                    By.CSS_SELECTOR, 
                    auth_info.get('selectors', {}).get('username', '[name="username"]')
                )
                password_field = driver.find_element(
                    By.CSS_SELECTOR,
                    auth_info.get('selectors', {}).get('password', '[name="password"]')
                )
                submit_button = driver.find_element(
                    By.CSS_SELECTOR,
                    auth_info.get('selectors', {}).get('submit', '[type="submit"]')
                )
                
                # Enter credentials with human-like typing
                from anti_bot_engine_advanced import advanced_anti_bot_engine
                advanced_anti_bot_engine.human_like_typing(
                    driver, username_field, auth_info['username']
                )
                time.sleep(0.5)
                advanced_anti_bot_engine.human_like_typing(
                    driver, password_field, auth_info['password']
                )
                time.sleep(0.5)
                
                # Click submit
                submit_button.click()
                time.sleep(3)
                
                # Check if login successful (customize per site)
                if 'login' not in driver.current_url.lower():
                    self.session_activity[session_id]['auth_status'] = True
                    
                    # Save cookies
                    self.save_session_cookies(session_id)
                    return True
            
            elif auth_info['method'] == 'oauth':
                # OAuth flow (implement as needed)
                pass
            
            elif auth_info['method'] == 'saml':
                # SAML flow (implement as needed)
                pass
            
        except Exception as e:
            print(f"Authentication failed: {e}")
        
        return False
    
    def save_session_cookies(self, session_id: str):
        """Save session cookies"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        driver = session['driver']
        
        # Get all cookies
        cookies = driver.get_cookies()
        session['cookies'] = cookies
        
        # Save to file
        cookie_file = os.path.join(self.session_dir, f"{session_id}_cookies.json")
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f)
        
        # Store in cookie jar
        self.cookie_jars[session['site']] = cookies
        
        # Get localStorage and sessionStorage
        try:
            session['local_storage'] = driver.execute_script(
                "return Object.entries(localStorage);"
            )
            session['session_storage'] = driver.execute_script(
                "return Object.entries(sessionStorage);"
            )
        except:
            pass
    
    def load_session_cookies(self, session_id: str):
        """Load saved cookies into session"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        driver = session['driver']
        
        # Load from file
        cookie_file = os.path.join(self.session_dir, f"{session_id}_cookies.json")
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
            
            # Add cookies to driver
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass
            
            session['cookies'] = cookies
        
        # Restore localStorage and sessionStorage
        if session.get('local_storage'):
            for key, value in session['local_storage']:
                driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
        
        if session.get('session_storage'):
            for key, value in session['session_storage']:
                driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")
    
    def maintain_session(self, session_id: str):
        """Keep session alive with periodic activity"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        driver = session['driver']
        
        try:
            # Perform minimal activity to keep session alive
            driver.execute_script("window.scrollBy(0, 10);")
            time.sleep(0.1)
            driver.execute_script("window.scrollBy(0, -10);")
            
            # Update activity
            self.session_activity[session_id]['last_active'] = datetime.now()
            
        except:
            # Session is dead
            self._cleanup_session(session_id)
    
    def start_heartbeat(self, interval: int = 60):
        """Start heartbeat thread to keep sessions alive"""
        if self.running:
            return
        
        self.running = True
        
        def heartbeat_loop():
            while self.running:
                for session_id in list(self.active_sessions.keys()):
                    activity = self.session_activity[session_id]
                    
                    # Check if session needs heartbeat
                    if activity['last_active']:
                        time_since_active = datetime.now() - activity['last_active']
                        if time_since_active < timedelta(minutes=5):
                            self.maintain_session(session_id)
                
                time.sleep(interval)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def stop_heartbeat(self):
        """Stop heartbeat thread"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
    
    def clone_session(self, session_id: str) -> Optional[str]:
        """Clone an existing session with all cookies and state"""
        if session_id not in self.active_sessions:
            return None
        
        original = self.active_sessions[session_id]
        
        # Create new session
        new_session_id = self.create_persistent_session(
            site=original['site'],
            browser_type=original['browser_type']
        )
        
        if new_session_id not in self.active_sessions:
            return None
        
        new_session = self.active_sessions[new_session_id]
        new_driver = new_session['driver']
        
        # Navigate to site
        new_driver.get(f"https://{original['site']}")
        
        # Copy cookies
        for cookie in original['cookies']:
            try:
                new_driver.add_cookie(cookie)
            except:
                pass
        
        # Copy storage
        new_session['local_storage'] = original.get('local_storage', {})
        new_session['session_storage'] = original.get('session_storage', {})
        
        # Refresh to apply cookies
        new_driver.refresh()
        
        return new_session_id
    
    def rotate_session(self, site: str) -> str:
        """Rotate to a fresh session for a site"""
        # Get current sessions for site
        current_sessions = self.session_pools.get(site, [])
        
        # Clean up old sessions if too many
        if len(current_sessions) > 5:
            # Remove oldest session
            oldest = min(
                current_sessions,
                key=lambda s: self.session_activity[s]['created_at']
            )
            self._cleanup_session(oldest)
        
        # Create new session
        return self.create_persistent_session(site)
    
    def _cleanup_session(self, session_id: str):
        """Clean up a session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Save final state
            self.save_session_cookies(session_id)
            
            # Close driver
            try:
                session['driver'].quit()
            except:
                pass
            
            # Remove from pools
            site = session['site']
            if site in self.session_pools and session_id in self.session_pools[site]:
                self.session_pools[site].remove(session_id)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
    
    def cleanup_all_sessions(self):
        """Clean up all active sessions"""
        for session_id in list(self.active_sessions.keys()):
            self._cleanup_session(session_id)
    
    def _save_saved_sessions(self):
        """Save session metadata to disk"""
        metadata = {
            'session_activity': dict(self.session_activity),
            'auth_states': self.auth_states,
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert datetime objects
        for session_id, activity in metadata['session_activity'].items():
            for key in ['created_at', 'last_active']:
                if activity.get(key):
                    activity[key] = activity[key].isoformat()
        
        metadata_file = os.path.join(self.session_dir, 'session_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_saved_sessions(self):
        """Load saved session metadata"""
        metadata_file = os.path.join(self.session_dir, 'session_metadata.json')
        
        if not os.path.exists(metadata_file):
            return
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Restore session activity
        for session_id, activity in metadata.get('session_activity', {}).items():
            self.session_activity[session_id] = activity
            # Convert strings back to datetime
            for key in ['created_at', 'last_active']:
                if activity.get(key):
                    activity[key] = datetime.fromisoformat(activity[key])
        
        self.auth_states = metadata.get('auth_states', {})
    
    def get_statistics(self) -> Dict:
        """Get session statistics"""
        total_sessions = len(self.active_sessions)
        authenticated = sum(
            1 for a in self.session_activity.values()
            if a['auth_status']
        )
        
        sites = defaultdict(int)
        for session in self.active_sessions.values():
            sites[session['site']] += 1
        
        total_requests = sum(
            a['total_requests'] for a in self.session_activity.values()
        )
        
        return {
            'total_active_sessions': total_sessions,
            'authenticated_sessions': authenticated,
            'sessions_by_site': dict(sites),
            'total_requests': total_requests,
            'cookie_jars': len(self.cookie_jars),
            'oldest_session': min(
                (a['created_at'] for a in self.session_activity.values() if a['created_at']),
                default=None
            )
        }

# Global instance
session_manager = SessionManager()
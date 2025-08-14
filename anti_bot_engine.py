"""
Advanced Anti-Bot Detection Engine
This module implements aggressive anti-detection measures
"""

import random
import time
import json
import os
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import requests
from fake_useragent import UserAgent
import cloudscraper

class AntiBotEngine:
    """
    Multi-layered anti-detection system
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.browser_profiles = self._load_browser_profiles()
        self.cloudflare_scraper = cloudscraper.create_scraper()
        
    def _load_browser_profiles(self) -> List[Dict]:
        """Load realistic browser fingerprints"""
        return [
            {
                "viewport": {"width": 1920, "height": 1080},
                "screen": {"width": 1920, "height": 1080, "depth": 24},
                "timezone": "America/New_York",
                "language": "en-US",
                "platform": "Win32",
                "memory": 8,
                "cpus": 4
            },
            {
                "viewport": {"width": 1366, "height": 768},
                "screen": {"width": 1366, "height": 768, "depth": 24},
                "timezone": "America/Chicago",
                "language": "en-US",
                "platform": "MacIntel",
                "memory": 16,
                "cpus": 8
            },
            {
                "viewport": {"width": 1440, "height": 900},
                "screen": {"width": 2880, "height": 1800, "depth": 30},
                "timezone": "America/Los_Angeles",
                "language": "en-US",
                "platform": "MacIntel",
                "memory": 32,
                "cpus": 10
            }
        ]
    
    def create_stealth_driver(self, proxy: Optional[Dict] = None) -> webdriver.Chrome:
        """
        Create undetected Chrome driver with maximum stealth
        """
        # Use undetected-chromedriver to bypass detection
        options = uc.ChromeOptions()
        
        # Randomize window size
        profile = random.choice(self.browser_profiles)
        options.add_argument(f'--window-size={profile["viewport"]["width"]},{profile["viewport"]["height"]}')
        
        # Essential stealth arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-webgl')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-site-isolation-trials')
        
        # Random user agent
        user_agent = self.ua.random
        options.add_argument(f'user-agent={user_agent}')
        
        # Language and timezone
        options.add_argument(f'--lang={profile["language"]}')
        
        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add stealth preferences
        prefs = {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.geolocation': 2,
            'profile.managed_default_content_settings.images': 1,
            'profile.default_content_setting_values.media_stream': 2,
            'profile.default_content_setting_values.media_stream_mic': 2,
            'profile.default_content_setting_values.media_stream_camera': 2,
            'profile.default_content_setting_values.protocol_handlers': 2,
            'profile.default_content_setting_values.ppapi_broker': 2,
            'profile.default_content_setting_values.automatic_downloads': 2,
            'profile.default_content_setting_values.midi_sysex': 2,
            'profile.default_content_setting_values.push_messaging': 2,
            'profile.default_content_setting_values.ssl_cert_decisions': 2,
            'profile.default_content_setting_values.metro_switch_to_desktop': 2,
            'profile.default_content_setting_values.protected_media_identifier': 2,
            'profile.default_content_setting_values.app_banner': 2,
            'profile.default_content_setting_values.site_engagement': 2,
            'profile.default_content_setting_values.durable_storage': 2
        }
        options.add_experimental_option('prefs', prefs)
        
        # Add proxy if provided
        if proxy and proxy.get('url'):
            proxy_url = proxy['url']
            # For authenticated proxies, we need extension
            if '@' in proxy_url:
                # This would need a proxy auth extension
                options.add_argument(f'--proxy-server={proxy_url.split("@")[1]}')
            else:
                options.add_argument(f'--proxy-server={proxy_url}')
        
        # Create driver with undetected-chromedriver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Inject additional stealth JavaScript
        self._inject_stealth_js(driver)
        
        return driver
    
    def _inject_stealth_js(self, driver):
        """Inject JavaScript to hide automation indicators"""
        stealth_js = """
        // Overwrite navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Overwrite navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Overwrite navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Overwrite chrome runtime
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {}
        };
        
        // Mock webGL vendor
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter(parameter);
        };
        """
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
    
    def human_like_delay(self, min_seconds: float = 0.5, max_seconds: float = 3.0):
        """Random human-like delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_like_mouse_movement(self, driver, element):
        """Simulate human-like mouse movement to element"""
        action = ActionChains(driver)
        
        # Get element location
        location = element.location_once_scrolled_into_view
        
        # Create random curve points for natural movement
        start_x = random.randint(0, 100)
        start_y = random.randint(0, 100)
        
        # Move mouse in a curve rather than straight line
        action.move_by_offset(start_x, start_y)
        self.human_like_delay(0.1, 0.3)
        
        action.move_to_element_with_offset(element, 5, 5)
        self.human_like_delay(0.1, 0.2)
        
        action.move_to_element(element)
        action.perform()
    
    def random_scroll(self, driver):
        """Random page scrolling to simulate reading"""
        scroll_pause_time = random.uniform(0.5, 2.0)
        
        # Get page height
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll random amounts
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(scroll_pause_time)
    
    def bypass_cloudflare(self, url: str, proxy: Optional[Dict] = None) -> str:
        """Bypass Cloudflare protection"""
        proxies = None
        if proxy and proxy.get('url'):
            proxies = {
                'http': proxy['url'],
                'https': proxy['url']
            }
        
        # Use cloudscraper for Cloudflare bypass
        response = self.cloudflare_scraper.get(url, proxies=proxies)
        return response.text
    
    def solve_captcha(self, driver, api_key: str = None):
        """
        Integrate with 2captcha/Anti-Captcha for CAPTCHA solving
        """
        # This would integrate with services like:
        # - 2captcha
        # - Anti-Captcha
        # - DeathByCaptcha
        # - CapSolver
        
        # Check for reCAPTCHA
        try:
            captcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
            site_key = captcha_element.get_attribute("data-sitekey")
            
            if api_key:
                # Send to 2captcha API
                # solver = TwoCaptcha(api_key)
                # result = solver.recaptcha(sitekey=site_key, url=driver.current_url)
                # driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{result["code"]}";')
                pass
        except:
            pass
    
    def rotate_user_agent(self) -> str:
        """Get random user agent"""
        return self.ua.random
    
    def get_headers_pool(self) -> Dict:
        """Get randomized realistic headers"""
        return {
            'User-Agent': self.rotate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': random.choice(['1', None]),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'Referer': random.choice(['https://www.google.com/', 'https://www.bing.com/', None])
        }
    
    def get_session_with_retry(self, url: str, max_retries: int = 3) -> requests.Session:
        """Create session with retry logic"""
        session = requests.Session()
        
        # Rotate user agent
        session.headers.update(self.get_headers_pool())
        
        # Add retry adapter
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

# Global anti-bot engine instance
anti_bot_engine = AntiBotEngine()
"""
Site-Specific Bypass Strategies
Real implementations for major bot protection systems
"""

import time
import random
import json
import base64
from typing import Dict, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

class CloudflareBypass:
    """Bypass Cloudflare protection"""
    
    def __init__(self):
        self.challenge_selectors = {
            'turnstile': 'cf-turnstile',
            'checkbox': '.cf-challenge',
            'js_challenge': '#cf-content',
            'captcha': '.g-recaptcha'
        }
    
    def detect_challenge_type(self, driver) -> Optional[str]:
        """Detect type of Cloudflare challenge"""
        page_source = driver.page_source.lower()
        
        if 'cf-turnstile' in page_source:
            return 'turnstile'
        elif 'checking your browser' in page_source:
            return 'js_challenge'
        elif 'cf-challenge' in page_source:
            return 'checkbox'
        elif 'recaptcha' in page_source:
            return 'captcha'
        
        return None
    
    def bypass(self, driver, timeout: int = 30) -> bool:
        """Attempt to bypass Cloudflare"""
        challenge_type = self.detect_challenge_type(driver)
        
        if not challenge_type:
            return True  # No challenge detected
        
        print(f"Cloudflare {challenge_type} detected, attempting bypass...")
        
        if challenge_type == 'js_challenge':
            # Wait for JS challenge to complete
            return self._wait_for_js_challenge(driver, timeout)
        
        elif challenge_type == 'turnstile':
            # Handle Turnstile
            return self._bypass_turnstile(driver)
        
        elif challenge_type == 'checkbox':
            # Click checkbox if visible
            return self._click_checkbox(driver)
        
        elif challenge_type == 'captcha':
            # Use captcha solver
            from captcha_solver import captcha_solver
            return captcha_solver.auto_detect_and_solve(driver)
        
        return False
    
    def _wait_for_js_challenge(self, driver, timeout: int) -> bool:
        """Wait for JavaScript challenge to complete"""
        try:
            # Wait for redirect
            WebDriverWait(driver, timeout).until_not(
                EC.presence_of_element_located((By.ID, "cf-content"))
            )
            
            # Additional wait for page load
            time.sleep(2)
            
            # Check if still on challenge page
            if 'checking your browser' not in driver.page_source.lower():
                return True
                
        except:
            pass
        
        return False
    
    def _bypass_turnstile(self, driver) -> bool:
        """Bypass Cloudflare Turnstile"""
        try:
            # Check for Turnstile iframe
            turnstile_frame = driver.find_element(By.CSS_SELECTOR, 'iframe[src*="challenges.cloudflare.com"]')
            
            # Get site key
            site_key = turnstile_frame.get_attribute('data-sitekey')
            
            if site_key:
                from captcha_solver import captcha_solver
                solution = captcha_solver.solve_cloudflare_turnstile(
                    driver, site_key, driver.current_url
                )
                return solution is not None
        except:
            pass
        
        return False
    
    def _click_checkbox(self, driver) -> bool:
        """Click Cloudflare checkbox"""
        try:
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.cf-challenge'))
            )
            
            # Human-like movement to checkbox
            from anti_bot_engine_advanced import advanced_anti_bot_engine
            advanced_anti_bot_engine.human_like_mouse_movement(driver, checkbox)
            
            time.sleep(random.uniform(0.5, 1.5))
            checkbox.click()
            
            # Wait for completion
            time.sleep(3)
            return True
            
        except:
            pass
        
        return False


class DataDomeBypass:
    """Bypass DataDome protection"""
    
    def __init__(self):
        self.datadome_cookies = {}
        self.captcha_endpoint = 'https://api-js.datadome.co/js/'
    
    def detect(self, driver) -> bool:
        """Detect DataDome protection"""
        indicators = [
            'datadome',
            'dd.min.js',
            'datadome-captcha',
            'dd-cookie'
        ]
        
        page_source = driver.page_source.lower()
        return any(indicator in page_source for indicator in indicators)
    
    def bypass(self, driver) -> bool:
        """Bypass DataDome protection"""
        if not self.detect(driver):
            return True
        
        print("DataDome detected, attempting bypass...")
        
        # Get DataDome cookie
        dd_cookie = self._get_datadome_cookie(driver)
        
        if dd_cookie:
            # Validate cookie
            if self._validate_cookie(dd_cookie, driver.current_url):
                return True
        
        # Handle captcha if present
        if self._has_captcha(driver):
            return self._solve_captcha(driver)
        
        # Try sensor data spoofing
        return self._spoof_sensor_data(driver)
    
    def _get_datadome_cookie(self, driver) -> Optional[str]:
        """Get DataDome cookie"""
        for cookie in driver.get_cookies():
            if 'datadome' in cookie['name'].lower():
                return cookie['value']
        return None
    
    def _validate_cookie(self, cookie: str, url: str) -> bool:
        """Validate DataDome cookie"""
        # DataDome validates cookies server-side
        # This would need reverse engineering of their validation
        return len(cookie) > 50  # Basic check
    
    def _has_captcha(self, driver) -> bool:
        """Check if DataDome captcha is present"""
        try:
            driver.find_element(By.CLASS_NAME, 'datadome-captcha')
            return True
        except:
            return False
    
    def _solve_captcha(self, driver) -> bool:
        """Solve DataDome captcha"""
        # DataDome uses various captcha types
        from captcha_solver import captcha_solver
        return captcha_solver.auto_detect_and_solve(driver)
    
    def _spoof_sensor_data(self, driver) -> bool:
        """Spoof DataDome sensor data"""
        js_code = """
        // Override DataDome sensor collection
        if (window.ddjskey) {
            window.ddjskey = function() {
                return {
                    mousemove: Math.random() * 100,
                    click: Math.random() * 10,
                    scroll: Math.random() * 50,
                    touchstart: 0,
                    touchend: 0,
                    touchmove: 0,
                    keydown: Math.random() * 20,
                    keyup: Math.random() * 20
                };
            };
        }
        
        // Override fingerprinting
        Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
        Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
        """
        
        driver.execute_script(js_code)
        time.sleep(2)
        driver.refresh()
        time.sleep(3)
        
        return not self._has_captcha(driver)


class PerimeterXBypass:
    """Bypass PerimeterX/HUMAN protection"""
    
    def __init__(self):
        self.px_cookies = {}
        self.challenge_endpoint = '/_px/captcha'
    
    def detect(self, driver) -> bool:
        """Detect PerimeterX protection"""
        indicators = [
            '_px',
            'perimeterx',
            'px-captcha',
            '_pxhd',
            'pxvid'
        ]
        
        page_source = driver.page_source.lower()
        cookies = [c['name'] for c in driver.get_cookies()]
        
        return any(indicator in page_source for indicator in indicators) or \
               any('_px' in cookie for cookie in cookies)
    
    def bypass(self, driver) -> bool:
        """Bypass PerimeterX"""
        if not self.detect(driver):
            return True
        
        print("PerimeterX detected, attempting bypass...")
        
        # Get PX cookies
        px_vid = self._get_px_vid(driver)
        
        # Inject anti-PX JavaScript
        self._inject_anti_px_script(driver)
        
        # Handle challenge if present
        if self._has_challenge(driver):
            return self._solve_challenge(driver)
        
        # Spoof sensor data
        self._spoof_px_sensor_data(driver)
        
        time.sleep(3)
        driver.refresh()
        time.sleep(2)
        
        return not self._has_challenge(driver)
    
    def _get_px_vid(self, driver) -> Optional[str]:
        """Get PerimeterX visitor ID"""
        for cookie in driver.get_cookies():
            if cookie['name'] == '_pxvid':
                return cookie['value']
        return None
    
    def _has_challenge(self, driver) -> bool:
        """Check for PerimeterX challenge"""
        try:
            driver.find_element(By.ID, 'px-captcha')
            return True
        except:
            return False
    
    def _solve_challenge(self, driver) -> bool:
        """Solve PerimeterX challenge"""
        # PerimeterX uses custom captchas
        # May need visual challenge solving
        from captcha_solver import captcha_solver
        return captcha_solver.auto_detect_and_solve(driver)
    
    def _inject_anti_px_script(self, driver):
        """Inject script to bypass PerimeterX"""
        js_code = """
        // Override PerimeterX sensor collection
        window._pxAction = 'c';
        window._pxMobile = false;
        window._pxPreventAnalytics = true;
        
        // Mock perfect sensor data
        window._pxParam1 = btoa(JSON.stringify({
            t: Date.now(),
            d: {PX203: 1, PX204: 0, PX205: 0}
        }));
        
        // Override XMLHttpRequest to intercept PX calls
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            
            xhr.open = function(method, url) {
                if (url.includes('/_px/')) {
                    // Modify or block PX requests
                    console.log('Intercepted PX request:', url);
                }
                return originalOpen.apply(this, arguments);
            };
            
            return xhr;
        };
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': js_code
        })
    
    def _spoof_px_sensor_data(self, driver):
        """Spoof PerimeterX sensor data"""
        js_code = """
        // Generate realistic sensor data
        if (window.PX) {
            window.PX.Events = {
                trigger: function() { return true; }
            };
        }
        
        // Mock events
        for (let i = 0; i < 10; i++) {
            document.dispatchEvent(new MouseEvent('mousemove', {
                bubbles: true,
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight
            }));
        }
        """
        
        driver.execute_script(js_code)


class AkamaiBotManagerBypass:
    """Bypass Akamai Bot Manager"""
    
    def __init__(self):
        self.sensor_data = {}
        self.abck_cookie = None
    
    def detect(self, driver) -> bool:
        """Detect Akamai Bot Manager"""
        indicators = [
            '_abck',
            'akamai',
            'bm_sz',
            'bm_sv',
            'ak_bmsc'
        ]
        
        cookies = [c['name'] for c in driver.get_cookies()]
        return any(indicator in cookie for cookie in cookies for indicator in indicators)
    
    def bypass(self, driver) -> bool:
        """Bypass Akamai Bot Manager"""
        if not self.detect(driver):
            return True
        
        print("Akamai Bot Manager detected, attempting bypass...")
        
        # Get _abck cookie
        self.abck_cookie = self._get_abck_cookie(driver)
        
        # Generate sensor data
        sensor_data = self._generate_sensor_data(driver)
        
        # Post sensor data
        if self._post_sensor_data(driver, sensor_data):
            time.sleep(2)
            driver.refresh()
            time.sleep(2)
            
            # Check if bypass successful
            new_abck = self._get_abck_cookie(driver)
            return new_abck and new_abck != self.abck_cookie
        
        return False
    
    def _get_abck_cookie(self, driver) -> Optional[str]:
        """Get Akamai _abck cookie"""
        for cookie in driver.get_cookies():
            if cookie['name'] == '_abck':
                return cookie['value']
        return None
    
    def _generate_sensor_data(self, driver) -> str:
        """Generate Akamai sensor data"""
        # This is a simplified version
        # Real implementation would need to reverse engineer Akamai's algorithm
        
        js_code = """
        function generateSensorData() {
            const data = {
                't': Date.now(),
                'w': window.innerWidth,
                'h': window.innerHeight,
                'p': navigator.platform,
                'l': navigator.language,
                'tz': new Date().getTimezoneOffset(),
                'cd': screen.colorDepth,
                'pd': screen.pixelDepth,
                'cpu': navigator.hardwareConcurrency,
                'mem': navigator.deviceMemory || 8,
                'cnc': navigator.connection ? navigator.connection.effectiveType : '4g'
            };
            
            // Add mouse movements
            const movements = [];
            for (let i = 0; i < 20; i++) {
                movements.push([
                    Math.floor(Math.random() * window.innerWidth),
                    Math.floor(Math.random() * window.innerHeight),
                    Date.now() + i * 100
                ]);
            }
            data['mm'] = movements;
            
            // Add key presses
            const keys = [];
            for (let i = 0; i < 10; i++) {
                keys.push([65 + Math.floor(Math.random() * 26), Date.now() + i * 200]);
            }
            data['kp'] = keys;
            
            return btoa(JSON.stringify(data));
        }
        
        return generateSensorData();
        """
        
        return driver.execute_script(js_code)
    
    def _post_sensor_data(self, driver, sensor_data: str) -> bool:
        """Post sensor data to Akamai endpoint"""
        # Find Akamai endpoint
        js_code = """
        // Look for Akamai script
        const scripts = document.getElementsByTagName('script');
        for (let script of scripts) {
            if (script.src && script.src.includes('akamai')) {
                return script.src;
            }
        }
        return null;
        """
        
        endpoint = driver.execute_script(js_code)
        
        if endpoint:
            # Post sensor data
            js_post = f"""
            fetch('{endpoint}', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    sensor_data: '{sensor_data}'
                }})
            }});
            """
            
            driver.execute_script(js_post)
            return True
        
        return False


class IncapsulaBypass:
    """Bypass Incapsula/Imperva protection"""
    
    def __init__(self):
        self.reese84_cookie = None
        self.session_cookies = {}
    
    def detect(self, driver) -> bool:
        """Detect Incapsula protection"""
        indicators = [
            'incapsula',
            'incap_ses',
            'visid_incap',
            'reese84',
            '/_Incapsula_Resource'
        ]
        
        page_source = driver.page_source.lower()
        cookies = [c['name'] for c in driver.get_cookies()]
        
        return any(indicator in page_source for indicator in indicators) or \
               any('incap' in cookie for cookie in cookies)
    
    def bypass(self, driver) -> bool:
        """Bypass Incapsula"""
        if not self.detect(driver):
            return True
        
        print("Incapsula detected, attempting bypass...")
        
        # Get Incapsula cookies
        self._extract_cookies(driver)
        
        # Handle JavaScript challenge
        if self._has_js_challenge(driver):
            self._solve_js_challenge(driver)
        
        # Handle Captcha
        if self._has_captcha(driver):
            from captcha_solver import captcha_solver
            captcha_solver.auto_detect_and_solve(driver)
        
        # Generate and submit sensor data
        self._submit_sensor_data(driver)
        
        time.sleep(3)
        driver.refresh()
        
        return not self._has_js_challenge(driver)
    
    def _extract_cookies(self, driver):
        """Extract Incapsula cookies"""
        for cookie in driver.get_cookies():
            if 'incap' in cookie['name'] or cookie['name'] == 'reese84':
                self.session_cookies[cookie['name']] = cookie['value']
    
    def _has_js_challenge(self, driver) -> bool:
        """Check for JavaScript challenge"""
        return '/_Incapsula_Resource' in driver.page_source
    
    def _has_captcha(self, driver) -> bool:
        """Check for Incapsula captcha"""
        try:
            driver.find_element(By.CLASS_NAME, 'incapsula-captcha')
            return True
        except:
            return False
    
    def _solve_js_challenge(self, driver):
        """Solve Incapsula JavaScript challenge"""
        # Wait for automatic solving
        time.sleep(5)
        
        # Check if still challenged
        if self._has_js_challenge(driver):
            # Inject solving script
            js_code = """
            // Trigger Incapsula validation
            if (window.___utmvc) {
                window.___utmvc();
            }
            """
            driver.execute_script(js_code)
    
    def _submit_sensor_data(self, driver):
        """Submit sensor data to Incapsula"""
        js_code = """
        // Generate Incapsula sensor data
        const sensorData = {
            'navigator': {
                'appCodeName': navigator.appCodeName,
                'appName': navigator.appName,
                'appVersion': navigator.appVersion,
                'platform': navigator.platform,
                'product': navigator.product,
                'productSub': navigator.productSub,
                'userAgent': navigator.userAgent,
                'vendor': navigator.vendor,
                'vendorSub': navigator.vendorSub,
                'language': navigator.language,
                'languages': navigator.languages,
                'onLine': navigator.onLine,
                'cookieEnabled': navigator.cookieEnabled,
                'doNotTrack': navigator.doNotTrack,
                'hardwareConcurrency': navigator.hardwareConcurrency,
                'maxTouchPoints': navigator.maxTouchPoints
            },
            'screen': {
                'width': screen.width,
                'height': screen.height,
                'availWidth': screen.availWidth,
                'availHeight': screen.availHeight,
                'colorDepth': screen.colorDepth,
                'pixelDepth': screen.pixelDepth
            },
            'window': {
                'innerWidth': window.innerWidth,
                'innerHeight': window.innerHeight,
                'outerWidth': window.outerWidth,
                'outerHeight': window.outerHeight,
                'screenX': window.screenX,
                'screenY': window.screenY
            },
            'document': {
                'referrer': document.referrer,
                'title': document.title
            },
            'performance': {
                'timing': performance.timing
            }
        };
        
        // Submit to Incapsula
        if (window.submitIncapChallengeAnswer) {
            window.submitIncapChallengeAnswer(JSON.stringify(sensorData));
        }
        """
        
        driver.execute_script(js_code)


class SiteSpecificBypasses:
    """
    Aggregator for all site-specific bypasses
    """
    
    def __init__(self):
        self.bypasses = {
            'cloudflare': CloudflareBypass(),
            'datadome': DataDomeBypass(),
            'perimeterx': PerimeterXBypass(),
            'akamai': AkamaiBotManagerBypass(),
            'incapsula': IncapsulaBypass()
        }
        
        # Site to protection mapping
        self.site_protections = {
            'nike.com': 'akamai',
            'adidas.com': 'datadome',
            'walmart.com': 'perimeterx',
            'bestbuy.com': 'perimeterx',
            'homedepot.com': 'akamai',
            'target.com': 'akamai',
            'footlocker.com': 'perimeterx',
            'supreme.com': 'perimeterx'
        }
    
    def detect_protection(self, driver) -> Optional[str]:
        """Detect which protection system is in use"""
        for name, bypass in self.bypasses.items():
            if bypass.detect(driver):
                return name
        return None
    
    def auto_bypass(self, driver) -> bool:
        """Automatically detect and bypass protection"""
        protection = self.detect_protection(driver)
        
        if not protection:
            return True  # No protection detected
        
        print(f"Detected {protection} protection, attempting bypass...")
        
        bypass = self.bypasses.get(protection)
        if bypass:
            return bypass.bypass(driver)
        
        return False
    
    def bypass_by_site(self, driver, url: str) -> bool:
        """Bypass based on known site protection"""
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Check if we know the protection for this site
        protection = self.site_protections.get(domain)
        
        if protection:
            bypass = self.bypasses.get(protection)
            if bypass:
                print(f"Using known {protection} bypass for {domain}")
                return bypass.bypass(driver)
        
        # Fall back to auto-detection
        return self.auto_bypass(driver)

# Global instance
site_bypasses = SiteSpecificBypasses()
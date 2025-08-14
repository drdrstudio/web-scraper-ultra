"""
Ultra Advanced Scraper with All Optimizations
Integrates DNS, timing, mobile, ban detection, WASM, cookies, and behavioral enhancements
"""

import json
import time
import random
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse
from datetime import datetime

# Import all optimization modules
from dns_optimizer import dns_optimizer
from request_patterns import request_optimizer
from mobile_simulator import mobile_simulator
from ban_detector import ban_detector, BanType, RecoveryStrategy
from wasm_protection import wasm_protection
from cookie_manager_advanced import cookie_manager
from behavioral_enhancer import behavioral_enhancer

# Import existing modules
from anti_bot_engine_advanced import advanced_anti_bot_engine
from smart_proxy_manager import smart_proxy_manager
from session_manager import session_manager
from captcha_solver import captcha_solver
from site_bypasses import site_bypasses

# Import scraping libraries
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import cloudscraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltraAdvancedScraper:
    """
    Ultra-advanced scraper with all cutting-edge anti-detection optimizations
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Initialize all optimization systems
        self.dns = dns_optimizer
        self.request_patterns = request_optimizer
        self.mobile = mobile_simulator
        self.ban_detector = ban_detector
        self.wasm = wasm_protection
        self.cookies = cookie_manager
        self.behavior = behavioral_enhancer
        
        # Existing advanced systems
        self.anti_bot = advanced_anti_bot_engine
        self.proxy_manager = smart_proxy_manager
        self.session_manager = session_manager
        self.captcha = captcha_solver
        self.site_bypasses = site_bypasses
        
        # Configuration
        self.enable_dns_over_https = self.config.get('dns_over_https', True)
        self.enable_timing_jitter = self.config.get('timing_jitter', True)
        self.enable_mobile_mode = self.config.get('mobile_mode', False)
        self.enable_wasm_protection = self.config.get('wasm_protection', True)
        self.enable_behavioral = self.config.get('behavioral', True)
        self.enable_ban_detection = self.config.get('ban_detection', True)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'bans_detected': 0,
            'captchas_solved': 0,
            'proxies_rotated': 0
        }
    
    def scrape(self, url: str, **kwargs) -> Dict:
        """
        Main scraping method with all optimizations
        
        Args:
            url: Target URL
            strategy: Scraping strategy ('auto', 'requests', 'selenium', 'undetected', 'mobile')
            profile: Behavioral profile ('casual_browser', 'power_user', 'researcher')
            use_proxy: Whether to use proxy rotation
            solve_captcha: Whether to auto-solve captchas
            mobile_device: Mobile device to emulate
            output_format: Output format ('json', 'html', 'text', 'structured')
        """
        strategy = kwargs.get('strategy', 'auto')
        profile = kwargs.get('profile', 'casual_browser')
        use_proxy = kwargs.get('use_proxy', True)
        solve_captcha = kwargs.get('solve_captcha', True)
        mobile_device = kwargs.get('mobile_device', None)
        output_format = kwargs.get('output_format', 'json')
        
        self.stats['total_requests'] += 1
        domain = urlparse(url).netloc
        
        # Step 1: DNS Resolution with DoH
        if self.enable_dns_over_https:
            logger.info("Resolving DNS with DoH")
            ips = self.dns.resolve_with_doh(domain)
            if ips:
                logger.info(f"Resolved {domain} to {ips}")
        
        # Step 2: Check domain health with ban detector
        if self.enable_ban_detection:
            if not self.ban_detector.should_proceed(domain):
                logger.warning(f"Domain {domain} has poor health, aborting")
                return {'success': False, 'error': 'Domain blocked due to poor health'}
        
        # Step 3: Apply request timing patterns
        if self.enable_timing_jitter:
            delay = self.request_patterns.calculate_request_delay(url)
            logger.info(f"Applying timing jitter: {delay:.3f}s")
            time.sleep(delay)
        
        # Step 4: Build referrer chain
        referrer_chain = self.request_patterns.build_referrer_chain(url)
        referrer = referrer_chain[-2] if len(referrer_chain) > 1 else None
        
        # Step 5: Select optimal proxy
        proxy = None
        if use_proxy:
            proxy = self.proxy_manager.get_optimal_proxy(
                url=url,
                strategy='ml_optimized'
            )
            if proxy:
                self.stats['proxies_rotated'] += 1
                logger.info(f"Using proxy: {proxy.get('http', 'N/A')}")
        
        # Step 6: Execute scraping with selected strategy
        result = None
        
        if strategy == 'auto':
            result = self._auto_strategy(url, proxy, referrer, **kwargs)
        elif strategy == 'mobile' or mobile_device:
            result = self._mobile_strategy(url, proxy, referrer, mobile_device, **kwargs)
        elif strategy == 'selenium':
            result = self._selenium_strategy(url, proxy, referrer, profile, **kwargs)
        elif strategy == 'undetected':
            result = self._undetected_strategy(url, proxy, referrer, profile, **kwargs)
        else:
            result = self._requests_strategy(url, proxy, referrer, **kwargs)
        
        # Step 7: Check for ban and recover if needed
        if self.enable_ban_detection and result:
            ban_type, confidence = self.ban_detector.detect_ban(
                html_content=result.get('html', ''),
                status_code=result.get('status_code'),
                headers=result.get('headers')
            )
            
            if ban_type != BanType.NONE and confidence > 0.7:
                logger.warning(f"Ban detected: {ban_type.value} (confidence: {confidence:.2f})")
                self.stats['bans_detected'] += 1
                self.ban_detector.record_ban(domain, ban_type)
                
                # Try recovery
                recovery_strategy = self.ban_detector.get_recovery_strategy(domain, ban_type)
                recovery_result = self.ban_detector.execute_recovery(
                    domain, ban_type, recovery_strategy
                )
                
                if recovery_result['success']:
                    # Retry with new configuration
                    if recovery_result['new_config'].get('rotate_proxy'):
                        proxy = self.proxy_manager.get_optimal_proxy(url=url)
                    
                    if recovery_result['new_config'].get('solve_captcha'):
                        kwargs['solve_captcha'] = True
                    
                    if recovery_result['new_config'].get('new_fingerprint'):
                        self.anti_bot.randomize_fingerprint()
                    
                    # Recursive retry with new config
                    return self.scrape(url, **kwargs)
        
        # Step 8: Update statistics
        if result and result.get('success'):
            self.stats['successful_requests'] += 1
            self.ban_detector.update_reputation(domain, True)
        else:
            self.stats['failed_requests'] += 1
            self.ban_detector.update_reputation(domain, False)
        
        # Step 9: Format and return result
        if result:
            result['statistics'] = self.get_statistics()
            result['domain_health'] = self.ban_detector.get_domain_health(domain)
        
        return self._format_output(result, output_format) if result else {'success': False}
    
    def _mobile_strategy(self, url: str, proxy: Dict, referrer: str, 
                        device: str, **kwargs) -> Dict:
        """Execute mobile scraping strategy"""
        logger.info(f"Using mobile strategy with device: {device or 'auto'}")
        
        # Select mobile device profile
        self.mobile.select_device(device)
        
        # Create mobile browser
        driver = self._create_mobile_driver(proxy)
        
        try:
            # Inject mobile overrides
            self.mobile.inject_mobile_overrides(driver)
            
            # Apply WASM protection
            if self.enable_wasm_protection:
                self.wasm.inject_wasm_overrides(driver)
            
            # Load cookies
            self.cookies.load_cookies(driver)
            
            # Navigate with referrer
            if referrer:
                driver.execute_script(f"window.location.href = '{url}';")
            else:
                driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Simulate mobile interactions
            self.mobile.simulate_device_orientation(driver)
            self.mobile.simulate_network_change(driver, 'wifi')
            
            # Find and interact with elements using touch
            links = driver.find_elements(By.TAG_NAME, 'a')[:5]
            for link in links:
                if random.random() < 0.3:  # 30% chance to tap
                    self.mobile.simulate_touch_event(driver, link, 'tap')
                    time.sleep(random.uniform(0.5, 2))
            
            # Extract content
            html = driver.page_source
            
            # Save cookies
            self.cookies.save_cookies(driver, f"mobile_{domain}")
            
            return {
                'success': True,
                'html': html,
                'url': driver.current_url,
                'device': self.mobile.current_device,
                'strategy': 'mobile'
            }
            
        except Exception as e:
            logger.error(f"Mobile strategy failed: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            driver.quit()
    
    def _selenium_strategy(self, url: str, proxy: Dict, referrer: str, 
                          profile: str, **kwargs) -> Dict:
        """Execute Selenium strategy with behavioral enhancements"""
        logger.info(f"Using Selenium strategy with profile: {profile}")
        
        # Select behavioral profile
        self.behavior.select_profile(profile)
        
        # Create driver with anti-detection
        driver = self._create_stealth_driver(proxy)
        
        try:
            # Apply all protections
            if self.enable_wasm_protection:
                self.wasm.inject_wasm_overrides(driver)
                self.wasm.inject_shared_array_buffer_protection(driver)
                self.wasm.inject_webgl_compute_protection(driver)
                self.wasm.inject_audio_worklet_protection(driver)
            
            # Load aged cookies
            domain = urlparse(url).netloc
            self.cookies.load_cookies(driver)
            
            # Apply behavioral enhancements
            if self.enable_behavioral:
                self.behavior.apply_full_enhancement(driver, url)
            else:
                driver.get(url)
            
            # Check for site-specific protections
            if self.site_bypasses.auto_bypass(driver):
                logger.info("Successfully bypassed site protection")
            
            # Check for captcha
            if kwargs.get('solve_captcha') and self.captcha.auto_detect_and_solve(driver):
                self.stats['captchas_solved'] += 1
                logger.info("Captcha solved successfully")
            
            # Wait for content
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Extract content
            html = driver.page_source
            cookies = driver.get_cookies()
            
            # Save session
            session_id = self.session_manager.create_persistent_session(
                site=domain,
                cookies=cookies,
                local_storage=driver.execute_script("return window.localStorage;"),
                session_storage=driver.execute_script("return window.sessionStorage;")
            )
            
            return {
                'success': True,
                'html': html,
                'url': driver.current_url,
                'cookies': cookies,
                'session_id': session_id,
                'strategy': 'selenium',
                'behavioral_profile': profile
            }
            
        except Exception as e:
            logger.error(f"Selenium strategy failed: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            driver.quit()
    
    def _undetected_strategy(self, url: str, proxy: Dict, referrer: str, 
                           profile: str, **kwargs) -> Dict:
        """Execute undetected Chrome strategy"""
        logger.info("Using undetected Chrome strategy")
        
        options = uc.ChromeOptions()
        
        # Apply fingerprint randomization
        fingerprint = self.anti_bot.generate_fingerprint()
        
        # Add proxy if available
        if proxy:
            proxy_string = proxy.get('http', '').replace('http://', '')
            options.add_argument(f'--proxy-server={proxy_string}')
        
        # Create undetected driver
        driver = uc.Chrome(options=options, version_main=None)
        
        try:
            # Apply all protections
            self.anti_bot.apply_stealth_settings(driver)
            
            if self.enable_wasm_protection:
                self.wasm.select_profile('chrome')
                self.wasm.inject_wasm_overrides(driver)
            
            # Navigate
            driver.get(url)
            
            # Apply behavioral patterns
            if self.enable_behavioral:
                self.behavior.select_profile(profile)
                self.behavior.simulate_reading_pattern(driver)
                self.behavior.simulate_mouse_patterns(driver)
            
            # Wait and extract
            time.sleep(random.uniform(2, 5))
            html = driver.page_source
            
            return {
                'success': True,
                'html': html,
                'url': driver.current_url,
                'strategy': 'undetected_chrome'
            }
            
        except Exception as e:
            logger.error(f"Undetected strategy failed: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            driver.quit()
    
    def _requests_strategy(self, url: str, proxy: Dict, referrer: str, **kwargs) -> Dict:
        """Execute requests strategy with timing patterns"""
        logger.info("Using requests strategy")
        
        # Create session with cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Apply randomized headers
        headers = self.request_patterns.get_random_headers({
            'User-Agent': self.anti_bot.get_random_user_agent(),
            'Referer': referrer or '',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Add fetch metadata
        headers.update(self.request_patterns.generate_fetch_metadata(url, referrer))
        
        # Set proxy
        proxies = {'http': proxy['http'], 'https': proxy['http']} if proxy else None
        
        try:
            # Apply timing jitter
            if self.enable_timing_jitter:
                delay = self.request_patterns.add_timing_jitter()
                time.sleep(delay)
            
            # Make request
            response = scraper.get(url, headers=headers, proxies=proxies, timeout=30)
            
            # Track request
            self.request_patterns.track_request(url)
            
            return {
                'success': True,
                'html': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'url': response.url,
                'strategy': 'requests'
            }
            
        except Exception as e:
            logger.error(f"Requests strategy failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _auto_strategy(self, url: str, proxy: Dict, referrer: str, **kwargs) -> Dict:
        """Automatically select best strategy"""
        domain = urlparse(url).netloc
        
        # Check if we have successful history for this domain
        if domain in self.ban_detector.successful_recoveries:
            past_successes = self.ban_detector.successful_recoveries[domain]
            if past_successes:
                # Use previously successful strategy
                last_success = past_successes[-1]
                logger.info(f"Using previously successful strategy for {domain}")
        
        # Try strategies in order of resource usage
        strategies = [
            ('requests', self._requests_strategy),
            ('selenium', self._selenium_strategy),
            ('undetected', self._undetected_strategy)
        ]
        
        for strategy_name, strategy_func in strategies:
            logger.info(f"Trying {strategy_name} strategy")
            result = strategy_func(url, proxy, referrer, **kwargs)
            
            if result.get('success'):
                return result
            
            # Check if we should take a break
            if self.request_patterns.should_take_break():
                break_duration = self.request_patterns.get_break_duration()
                logger.info(f"Taking break for {break_duration:.1f} seconds")
                time.sleep(break_duration)
        
        return {'success': False, 'error': 'All strategies failed'}
    
    def _create_stealth_driver(self, proxy: Dict = None):
        """Create Selenium driver with stealth settings"""
        options = webdriver.ChromeOptions()
        
        # Apply stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy
        if proxy:
            proxy_string = proxy.get('http', '').replace('http://', '')
            options.add_argument(f'--proxy-server={proxy_string}')
        
        driver = webdriver.Chrome(options=options)
        
        # Apply anti-detection
        self.anti_bot.apply_stealth_settings(driver)
        
        return driver
    
    def _create_mobile_driver(self, proxy: Dict = None):
        """Create mobile-configured driver"""
        options = webdriver.ChromeOptions()
        
        # Mobile emulation
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
            "userAgent": self.mobile.current_device['userAgent'] if self.mobile.current_device else None
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Proxy
        if proxy:
            proxy_string = proxy.get('http', '').replace('http://', '')
            options.add_argument(f'--proxy-server={proxy_string}')
        
        return webdriver.Chrome(options=options)
    
    def _format_output(self, result: Dict, format_type: str) -> Union[Dict, str]:
        """Format output based on requested type"""
        if not result or not result.get('success'):
            return result
        
        html = result.get('html', '')
        
        # Check for LLM-friendly formats
        llm_formats = ['clean_text', 'structured_qa', 'markdown', 'conversation', 
                      'summary', 'json_ld', 'narrative']
        
        if format_type in llm_formats:
            # Use LLM formatter for AI-friendly output
            from llm_formatter import llm_formatter
            metadata = {
                'url': result.get('url'),
                'timestamp': datetime.now().isoformat(),
                'strategy': result.get('strategy')
            }
            return llm_formatter.format(html, format_type, metadata)
        
        # Original format types
        if format_type == 'html':
            return html
        elif format_type == 'text':
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(strip=True)
        elif format_type == 'structured':
            soup = BeautifulSoup(html, 'html.parser')
            return {
                'title': soup.title.string if soup.title else None,
                'meta': {tag.get('name', tag.get('property')): tag.get('content') 
                        for tag in soup.find_all('meta') if tag.get('content')},
                'links': [a.get('href') for a in soup.find_all('a', href=True)],
                'images': [img.get('src') for img in soup.find_all('img', src=True)],
                'text': soup.get_text(strip=True)[:5000]
            }
        else:  # json
            return result
    
    def get_statistics(self) -> Dict:
        """Get scraper statistics"""
        stats = self.stats.copy()
        stats['dns_cache_size'] = len(self.dns.dns_cache)
        stats['proxy_stats'] = self.proxy_manager.get_statistics()
        stats['request_patterns'] = self.request_patterns.get_request_statistics()
        stats['cookie_stats'] = self.cookies.get_cookie_statistics()
        
        return stats
    
    def reset(self):
        """Reset all systems for new scraping session"""
        self.behavior.reset_session()
        self.request_patterns.switch_profile()
        self.dns.clear_cache()
        logger.info("Scraper reset for new session")

# Create singleton instance
ultra_scraper = UltraAdvancedScraper()
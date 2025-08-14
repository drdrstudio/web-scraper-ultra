"""
Advanced Anti-Bot Detection Scraper
Implements multiple scraping strategies with maximum stealth
"""

import json
import time
import random
from typing import Dict, List, Optional, Union
from anti_bot_engine import anti_bot_engine
try:
    from anti_bot_engine_advanced import advanced_anti_bot_engine
    USE_ADVANCED_ENGINE = True
except ImportError:
    USE_ADVANCED_ENGINE = False
from proxy_manager import proxy_manager
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AdvancedScraper:
    """
    Multi-strategy scraper with anti-detection capabilities
    """
    
    def __init__(self):
        # Use advanced engine if available
        if USE_ADVANCED_ENGINE:
            self.anti_bot = advanced_anti_bot_engine
            print("✅ Using Advanced Anti-Bot Engine with fingerprint spoofing")
        else:
            self.anti_bot = anti_bot_engine
            print("Using Standard Anti-Bot Engine")
        
        self.strategies = [
            self.strategy_cloudscraper,
            self.strategy_requests_session,
            self.strategy_selenium_stealth,
            self.strategy_undetected_chrome
        ]
    
    def scrape(self, url: str, strategy: str = "auto", output_format: str = "json") -> Union[Dict, str]:
        """
        Main scraping method with automatic strategy selection
        
        Args:
            url: Target URL
            strategy: 'auto', 'cloudscraper', 'requests', 'selenium', 'undetected'
            output_format: 'json', 'html', 'text', 'markdown', 'structured'
        """
        proxy = proxy_manager.get_next_proxy() if proxy_manager.proxies else None
        
        # Auto-select best strategy
        if strategy == "auto":
            return self._auto_scrape(url, proxy, output_format)
        
        # Use specific strategy
        strategies_map = {
            'cloudscraper': self.strategy_cloudscraper,
            'requests': self.strategy_requests_session,
            'selenium': self.strategy_selenium_stealth,
            'undetected': self.strategy_undetected_chrome
        }
        
        scraper_func = strategies_map.get(strategy, self._auto_scrape)
        result = scraper_func(url, proxy)
        
        return self._format_output(result, output_format)
    
    def _auto_scrape(self, url: str, proxy: Optional[Dict], output_format: str) -> Dict:
        """
        Try multiple strategies until one succeeds
        """
        errors = []
        
        # Try each strategy in order of speed/resource usage
        for strategy_func in self.strategies:
            try:
                print(f"Trying strategy: {strategy_func.__name__}")
                result = strategy_func(url, proxy)
                if result and result.get('success'):
                    result['strategy_used'] = strategy_func.__name__
                    return self._format_output(result, output_format)
            except Exception as e:
                errors.append({
                    'strategy': strategy_func.__name__,
                    'error': str(e)
                })
                continue
        
        return {
            'success': False,
            'errors': errors,
            'message': 'All strategies failed'
        }
    
    def strategy_cloudscraper(self, url: str, proxy: Optional[Dict]) -> Dict:
        """
        Use cloudscraper for Cloudflare bypass
        """
        try:
            # Random delay
            self.anti_bot.human_like_delay(0.5, 2.0)
            
            # Get content
            content = self.anti_bot.bypass_cloudflare(url, proxy)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            return {
                'success': True,
                'html': content,
                'text': soup.get_text(),
                'title': soup.title.string if soup.title else None,
                'meta': self._extract_meta(soup),
                'links': [a.get('href') for a in soup.find_all('a', href=True)][:50],
                'images': [img.get('src') for img in soup.find_all('img', src=True)][:50]
            }
        except Exception as e:
            raise Exception(f"Cloudscraper failed: {str(e)}")
    
    def strategy_requests_session(self, url: str, proxy: Optional[Dict]) -> Dict:
        """
        Use requests with session and retry logic
        """
        try:
            session = self.anti_bot.get_session_with_retry(url)
            
            # Add proxy if available
            proxies = None
            if proxy and proxy.get('url'):
                proxies = {
                    'http': proxy['url'],
                    'https': proxy['url']
                }
            
            # Random delay
            self.anti_bot.human_like_delay(0.5, 2.0)
            
            # Make request
            response = session.get(url, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'success': True,
                'html': response.text,
                'text': soup.get_text(),
                'title': soup.title.string if soup.title else None,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'cookies': session.cookies.get_dict(),
                'meta': self._extract_meta(soup)
            }
        except Exception as e:
            raise Exception(f"Requests session failed: {str(e)}")
    
    def strategy_selenium_stealth(self, url: str, proxy: Optional[Dict]) -> Dict:
        """
        Use Selenium with stealth modifications
        """
        driver = None
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            options.add_argument(f'user-agent={self.anti_bot.rotate_user_agent()}')
            
            driver = webdriver.Chrome(options=options)
            
            # Inject stealth JS
            self.anti_bot._inject_stealth_js(driver)
            
            # Navigate to URL
            driver.get(url)
            
            # Random scrolling and delays
            self.anti_bot.random_scroll(driver)
            self.anti_bot.human_like_delay(2, 5)
            
            # Wait for content
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract JavaScript rendered data
            js_data = driver.execute_script("""
                return {
                    url: window.location.href,
                    title: document.title,
                    cookies: document.cookie,
                    localStorage: Object.entries(localStorage),
                    performance: performance.timing
                };
            """)
            
            return {
                'success': True,
                'html': page_source,
                'text': soup.get_text(),
                'title': js_data['title'],
                'js_data': js_data,
                'meta': self._extract_meta(soup)
            }
        except Exception as e:
            raise Exception(f"Selenium stealth failed: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    def strategy_undetected_chrome(self, url: str, proxy: Optional[Dict]) -> Dict:
        """
        Use undetected-chromedriver for maximum stealth
        """
        driver = None
        try:
            # Create stealth driver - use ultra stealth if available
            if USE_ADVANCED_ENGINE and hasattr(self.anti_bot, 'create_ultra_stealth_driver'):
                driver = self.anti_bot.create_ultra_stealth_driver(proxy)
            else:
                driver = self.anti_bot.create_stealth_driver(proxy)
            
            # Navigate with random delays
            self.anti_bot.human_like_delay(1, 3)
            driver.get(url)
            
            # Enhanced human-like behavior if using advanced engine
            if USE_ADVANCED_ENGINE and hasattr(self.anti_bot, 'simulate_human_behavior'):
                self.anti_bot.simulate_human_behavior(driver)
            else:
                # Fallback to standard behavior
                self.anti_bot.random_scroll(driver)
                self.anti_bot.human_like_delay(2, 5)
            
            # Check for bot detection and attempt bypass
            if USE_ADVANCED_ENGINE and hasattr(self.anti_bot, 'detect_and_bypass_protection'):
                bypass_success = self.anti_bot.detect_and_bypass_protection(driver)
                if not bypass_success:
                    print("Warning: Bot protection detected but bypass may have failed")
            
            # Wait for dynamic content
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract everything
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Get all data including AJAX calls
            network_data = driver.execute_script("""
                return window.performance.getEntriesByType('resource')
                    .filter(x => x.initiatorType === 'xmlhttprequest' || x.initiatorType === 'fetch')
                    .map(x => ({name: x.name, duration: x.duration}));
            """)
            
            # Get browser fingerprint info if using advanced engine
            fingerprint_info = None
            if USE_ADVANCED_ENGINE:
                fingerprint_info = driver.execute_script("""
                    return {
                        userAgent: navigator.userAgent,
                        platform: navigator.platform,
                        vendor: navigator.vendor,
                        languages: navigator.languages,
                        screen: {
                            width: screen.width,
                            height: screen.height,
                            colorDepth: screen.colorDepth
                        },
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        webdriver: navigator.webdriver,
                        plugins: navigator.plugins.length
                    };
                """)
            
            result = {
                'success': True,
                'html': page_source,
                'text': soup.get_text(),
                'title': driver.title,
                'url': driver.current_url,
                'network_requests': network_data,
                'meta': self._extract_meta(soup),
                'screenshots': self._take_screenshot(driver)
            }
            
            # Add fingerprint info if available
            if USE_ADVANCED_ENGINE and fingerprint_info:
                result['fingerprint_used'] = fingerprint_info
                result['anti_bot_engine'] = 'advanced'
            else:
                result['anti_bot_engine'] = 'standard'
            
            return result
        except Exception as e:
            raise Exception(f"Undetected Chrome failed: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    def _extract_meta(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from page"""
        meta = {}
        
        # Meta tags
        for tag in soup.find_all('meta'):
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                meta[name] = content
        
        # Open Graph data
        og_data = {}
        for tag in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            og_data[tag['property']] = tag.get('content')
        
        # JSON-LD structured data
        json_ld = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_ld.append(json.loads(script.string))
            except:
                pass
        
        return {
            'meta_tags': meta,
            'open_graph': og_data,
            'json_ld': json_ld
        }
    
    def _take_screenshot(self, driver) -> str:
        """Take full page screenshot"""
        try:
            import base64
            screenshot = driver.get_screenshot_as_base64()
            return f"data:image/png;base64,{screenshot}"
        except:
            return None
    
    def _format_output(self, data: Dict, format: str) -> Union[Dict, str]:
        """
        Format output in requested format
        """
        if not data.get('success'):
            return data
        
        if format == "json":
            return data
        
        elif format == "html":
            return data.get('html', '')
        
        elif format == "text":
            return data.get('text', '')
        
        elif format == "markdown":
            # Convert to markdown format
            md = f"# {data.get('title', 'Untitled')}\n\n"
            md += f"**URL**: {data.get('url', '')}\n\n"
            md += f"## Content\n\n{data.get('text', '')}\n\n"
            if data.get('links'):
                md += f"## Links\n\n"
                for link in data.get('links', [])[:20]:
                    md += f"- {link}\n"
            return md
        
        elif format == "structured":
            # Return structured data for databases
            return {
                'title': data.get('title'),
                'url': data.get('url'),
                'text': data.get('text', '')[:5000],  # Truncate for DB
                'meta': data.get('meta'),
                'links_count': len(data.get('links', [])),
                'images_count': len(data.get('images', [])),
                'strategy': data.get('strategy_used'),
                'timestamp': time.time()
            }
        
        return data

# Global instance
advanced_scraper = AdvancedScraper()
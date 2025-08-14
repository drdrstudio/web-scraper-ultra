#!/usr/bin/env python3
"""
Newsletter Subscription API
Automatically finds and subscribes to newsletters using the ultra-advanced scraper
"""

import os
import re
import json
import time
import logging
from typing import Dict, Optional, List, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random

# Import our advanced scraper components
from advanced_scraper_ultra import ultra_scraper
from behavioral_enhancer import behavioral_enhancer
from ban_detector import ban_detector
from captcha_solver import captcha_solver
from session_manager import session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.environ.get('NEWSLETTER_API_KEY', 'your-secret-api-key-here')
TEST_EMAIL = os.environ.get('TEST_EMAIL', 'test@example.com')

class NewsletterSubscriber:
    """Handles newsletter subscription logic with anti-detection"""
    
    def __init__(self):
        self.common_selectors = {
            'forms': [
                'form[action*="newsletter"]',
                'form[action*="subscribe"]',
                'form[action*="signup"]',
                'form[action*="email"]',
                'form[action*="join"]',
                'form[action*="mailchimp"]',
                'form[action*="campaign-archive"]',
                'form[action*="list-manage"]',
                'form[class*="newsletter"]',
                'form[class*="subscribe"]',
                'form[id*="newsletter"]',
                'form[id*="subscribe"]',
                'div[class*="newsletter"] form',
                'div[class*="subscribe"] form',
                'section[class*="newsletter"] form'
            ],
            'email_inputs': [
                'input[type="email"]',
                'input[name*="email"]',
                'input[id*="email"]',
                'input[placeholder*="email"]',
                'input[placeholder*="@"]',
                'input[aria-label*="email"]',
                'input[class*="email"]'
            ],
            'submit_buttons': [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[class*="subscribe"]',
                'button[class*="submit"]',
                'button[class*="newsletter"]',
                'button[class*="join"]',
                'button:contains("Subscribe")',
                'button:contains("Sign up")',
                'button:contains("Join")',
                'button:contains("Submit")',
                'a[class*="subscribe"]'
            ],
            'newsletter_indicators': [
                'newsletter', 'subscribe', 'signup', 'sign up',
                'join', 'mailing list', 'updates', 'stay informed',
                'get news', 'weekly digest', 'daily digest',
                'notifications', 'alerts', 'insider', 'exclusive'
            ]
        }
        
        self.email_patterns = {
            'standard': TEST_EMAIL,
            'plus_addressing': f"{TEST_EMAIL.split('@')[0]}+{{tag}}@{TEST_EMAIL.split('@')[1]}",
            'subdomain': f"{{tag}}.{TEST_EMAIL}"
        }
    
    def find_newsletter_form(self, driver) -> Optional[Dict]:
        """
        Find newsletter signup form on the page
        Returns dict with form, email_input, and submit_button elements
        """
        logger.info("Searching for newsletter signup form...")
        
        # Method 1: Look for obvious newsletter forms
        for form_selector in self.common_selectors['forms']:
            try:
                forms = driver.find_elements(By.CSS_SELECTOR, form_selector)
                for form in forms:
                    if not form.is_displayed():
                        continue
                    
                    # Look for email input within form
                    for email_selector in self.common_selectors['email_inputs']:
                        try:
                            email_input = form.find_element(By.CSS_SELECTOR, email_selector)
                            if email_input and email_input.is_displayed():
                                # Look for submit button
                                submit_button = self._find_submit_button(form)
                                if submit_button:
                                    logger.info(f"Found newsletter form with selector: {form_selector}")
                                    return {
                                        'form': form,
                                        'email_input': email_input,
                                        'submit_button': submit_button,
                                        'method': 'form_based'
                                    }
                        except:
                            continue
            except Exception as e:
                logger.debug(f"Error checking form selector {form_selector}: {e}")
        
        # Method 2: Look for standalone email inputs (not in forms)
        logger.info("Looking for standalone email inputs...")
        for email_selector in self.common_selectors['email_inputs']:
            try:
                email_inputs = driver.find_elements(By.CSS_SELECTOR, email_selector)
                for email_input in email_inputs:
                    if not email_input.is_displayed():
                        continue
                    
                    # Check if there's newsletter-related text nearby
                    parent = email_input.find_element(By.XPATH, './..')
                    parent_text = parent.text.lower()
                    
                    if any(indicator in parent_text for indicator in self.common_selectors['newsletter_indicators']):
                        # Look for nearby submit button
                        submit_button = self._find_nearby_submit_button(driver, email_input)
                        if submit_button:
                            logger.info("Found standalone newsletter signup")
                            return {
                                'form': None,
                                'email_input': email_input,
                                'submit_button': submit_button,
                                'method': 'standalone'
                            }
            except:
                continue
        
        # Method 3: Click on "Newsletter" links first
        logger.info("Looking for newsletter links to click...")
        newsletter_links = self._find_newsletter_links(driver)
        for link in newsletter_links[:3]:  # Try first 3 links
            try:
                # Scroll to link and click
                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                time.sleep(1)
                link.click()
                time.sleep(3)  # Wait for page/modal to load
                
                # Try to find form again
                result = self.find_newsletter_form(driver)
                if result:
                    return result
            except:
                continue
        
        return None
    
    def _find_submit_button(self, form) -> Optional[any]:
        """Find submit button within or near a form"""
        # Look within form first
        for button_selector in self.common_selectors['submit_buttons']:
            try:
                button = form.find_element(By.CSS_SELECTOR, button_selector)
                if button and button.is_displayed():
                    return button
            except:
                continue
        
        # Look for button with text
        try:
            buttons = form.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                button_text = button.text.lower()
                if any(word in button_text for word in ['subscribe', 'sign', 'join', 'submit', 'go', 'send']):
                    return button
        except:
            pass
        
        return None
    
    def _find_nearby_submit_button(self, driver, email_input) -> Optional[any]:
        """Find submit button near an email input"""
        try:
            # Look for button in same parent container
            parent = email_input.find_element(By.XPATH, './ancestor::div[1]')
            buttons = parent.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                if button.is_displayed():
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['subscribe', 'sign', 'join', 'submit']):
                        return button
            
            # Look for input submit
            submits = parent.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
            if submits and submits[0].is_displayed():
                return submits[0]
        except:
            pass
        
        return None
    
    def _find_newsletter_links(self, driver) -> List:
        """Find links that might lead to newsletter signup"""
        newsletter_links = []
        
        try:
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            for link in all_links:
                link_text = link.text.lower()
                href = link.get_attribute('href') or ''
                
                if any(word in link_text + href for word in ['newsletter', 'subscribe', 'signup', 'join']):
                    newsletter_links.append(link)
        except:
            pass
        
        return newsletter_links
    
    def generate_unique_email(self, domain: str) -> str:
        """Generate a unique email address for this subscription"""
        # Use plus addressing for tracking
        tag = domain.replace('.', '_').replace('-', '_')
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        if '+' in TEST_EMAIL:
            # Already using plus addressing
            return TEST_EMAIL
        else:
            # Add plus addressing
            parts = TEST_EMAIL.split('@')
            return f"{parts[0]}+{tag}_{timestamp}@{parts[1]}"
    
    def fill_and_submit_form(self, driver, form_elements: Dict, domain: str) -> Dict:
        """Fill out and submit the newsletter form"""
        try:
            email_input = form_elements['email_input']
            submit_button = form_elements['submit_button']
            
            # Generate unique email
            email = self.generate_unique_email(domain)
            
            # Use behavioral enhancer for human-like interaction
            behavioral_enhancer.select_profile('casual_browser')
            
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click on email input
            email_input.click()
            time.sleep(random.uniform(0.2, 0.5))
            
            # Clear any existing value
            email_input.clear()
            
            # Type email with human-like speed
            for char in email:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Random pause (like checking the email)
            time.sleep(random.uniform(0.5, 2))
            
            # Check for additional required fields
            if form_elements['form']:
                self._fill_additional_fields(form_elements['form'])
            
            # Scroll to submit button
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(random.uniform(0.5, 1))
            
            # Click submit
            submit_button.click()
            
            # Wait for response
            time.sleep(3)
            
            # Check for success indicators
            success = self._check_submission_success(driver)
            
            return {
                'success': success,
                'email_used': email,
                'method': form_elements['method']
            }
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fill_additional_fields(self, form):
        """Fill any additional required fields in the form"""
        try:
            # Check for name fields
            name_inputs = form.find_elements(By.CSS_SELECTOR, 
                'input[name*="name"], input[name*="first"], input[name*="last"]')
            
            for name_input in name_inputs:
                if name_input.is_displayed() and name_input.get_attribute('required'):
                    name_input.clear()
                    name_input.send_keys("Test User")
                    time.sleep(random.uniform(0.2, 0.5))
            
            # Check for checkboxes (consent, terms, etc.)
            checkboxes = form.find_elements(By.CSS_SELECTOR, 
                'input[type="checkbox"][required], input[type="checkbox"][name*="consent"], input[type="checkbox"][name*="agree"]')
            
            for checkbox in checkboxes:
                if checkbox.is_displayed() and not checkbox.is_selected():
                    checkbox.click()
                    time.sleep(random.uniform(0.2, 0.5))
                    
        except Exception as e:
            logger.debug(f"Error filling additional fields: {e}")
    
    def _check_submission_success(self, driver) -> bool:
        """Check if the form submission was successful"""
        try:
            # Check for success messages
            success_indicators = [
                "thank you", "thanks", "success", "confirmed", 
                "subscribed", "welcome", "check your email",
                "you're in", "you're subscribed", "almost there"
            ]
            
            # Get page text
            page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            # Check for success indicators
            for indicator in success_indicators:
                if indicator in page_text:
                    logger.info(f"Success indicator found: {indicator}")
                    return True
            
            # Check if we're redirected to a success page
            current_url = driver.current_url.lower()
            if any(word in current_url for word in ['success', 'thank', 'confirm', 'welcome']):
                logger.info(f"Success URL detected: {current_url}")
                return True
            
            # Check for success alerts/modals
            try:
                alerts = driver.find_elements(By.CSS_SELECTOR, 
                    '[role="alert"], .alert-success, .success-message, .thank-you')
                if alerts and alerts[0].is_displayed():
                    return True
            except:
                pass
            
        except Exception as e:
            logger.error(f"Error checking success: {e}")
        
        return False
    
    def subscribe_to_newsletter(self, domain: str) -> Dict:
        """Main method to subscribe to a newsletter on the given domain"""
        logger.info(f"Attempting to subscribe to newsletter on {domain}")
        
        # Ensure domain has protocol
        if not domain.startswith('http'):
            url = f"https://{domain}"
        else:
            url = domain
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Create driver with all anti-detection features
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--headless')  # Run in headless mode for API
        
        driver = webdriver.Chrome(options=options)
        
        try:
            # Apply anti-detection
            from anti_bot_engine_advanced import advanced_anti_bot_engine
            advanced_anti_bot_engine.apply_stealth_settings(driver)
            
            # Navigate to the site
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Apply behavioral patterns
            behavioral_enhancer.simulate_reading_pattern(driver, 1000)
            
            # Check for CAPTCHA
            if self._detect_captcha(driver):
                # Try to solve CAPTCHA
                captcha_solved = captcha_solver.auto_detect_and_solve(driver)
                if not captcha_solved:
                    return {
                        'success': False,
                        'error': 'CAPTCHA_DETECTED',
                        'message': 'CAPTCHA detected and could not be solved automatically'
                    }
            
            # Find newsletter form
            form_elements = self.find_newsletter_form(driver)
            
            if not form_elements:
                # Try scrolling to footer (newsletters often in footer)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                form_elements = self.find_newsletter_form(driver)
            
            if not form_elements:
                return {
                    'success': False,
                    'error': 'FORM_NOT_FOUND',
                    'message': 'No newsletter signup form could be found on the page'
                }
            
            # Fill and submit the form
            result = self.fill_and_submit_form(driver, form_elements, domain)
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Subscription form submitted successfully',
                    'email_used': result.get('email_used'),
                    'method': result.get('method')
                }
            else:
                return {
                    'success': False,
                    'error': 'SUBMISSION_FAILED',
                    'message': 'Form was found but submission failed',
                    'details': result.get('error')
                }
            
        except Exception as e:
            logger.error(f"Error during subscription process: {e}")
            return {
                'success': False,
                'error': 'PROCESS_ERROR',
                'message': str(e)
            }
        
        finally:
            driver.quit()
    
    def _detect_captcha(self, driver) -> bool:
        """Detect if there's a CAPTCHA on the page"""
        captcha_indicators = [
            'iframe[src*="recaptcha"]',
            'iframe[src*="hcaptcha"]',
            'div[class*="captcha"]',
            'div[id*="captcha"]',
            '[class*="g-recaptcha"]',
            '[class*="h-captcha"]'
        ]
        
        for selector in captcha_indicators:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    logger.info(f"CAPTCHA detected: {selector}")
                    return True
            except:
                continue
        
        return False

# Initialize subscriber
newsletter_subscriber = NewsletterSubscriber()

# Authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'status': 'error',
                'message': 'Missing Authorization header'
            }), 401
        
        # Check for Bearer token
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'status': 'error',
                'message': 'Invalid Authorization format. Use: Bearer YOUR_API_KEY'
            }), 401
        
        provided_key = auth_header.replace('Bearer ', '')
        
        if provided_key != API_KEY:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# API Routes
@app.route('/api/subscribe', methods=['POST'])
@require_api_key
def subscribe():
    """Main API endpoint for newsletter subscription"""
    
    # Validate request
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Request must be JSON'
        }), 400
    
    data = request.get_json()
    domain = data.get('domain')
    
    if not domain:
        return jsonify({
            'status': 'error',
            'message': 'Domain is required'
        }), 400
    
    # Clean domain
    domain = domain.strip().lower()
    
    # Attempt subscription
    result = newsletter_subscriber.subscribe_to_newsletter(domain)
    
    # Format response based on result
    if result['success']:
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'domain': domain,
            'details': {
                'email_used': result.get('email_used'),
                'method': result.get('method')
            }
        }), 200
    else:
        # Determine appropriate error code
        error_code = result.get('error', 'UNKNOWN')
        
        if error_code == 'FORM_NOT_FOUND':
            http_status = 404
        elif error_code == 'CAPTCHA_DETECTED':
            http_status = 422
        elif error_code == 'SUBMISSION_FAILED':
            http_status = 422
        else:
            http_status = 500
        
        return jsonify({
            'status': 'error',
            'message': result['message'],
            'domain': domain,
            'error_code': error_code,
            'details': result.get('details')
        }), http_status

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Newsletter Subscriber API',
        'version': '1.0.0'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'service': 'Newsletter Subscriber API',
        'version': '1.0.0',
        'endpoints': {
            '/api/subscribe': {
                'method': 'POST',
                'description': 'Subscribe to newsletter on given domain',
                'authentication': 'Bearer token in Authorization header',
                'request_body': {
                    'domain': 'example.com'
                },
                'response': {
                    'success': {
                        'status': 'success',
                        'message': 'Subscription form submitted successfully',
                        'domain': 'example.com'
                    },
                    'error': {
                        'status': 'error',
                        'message': 'Error description',
                        'domain': 'example.com',
                        'error_code': 'ERROR_CODE'
                    }
                }
            },
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            }
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
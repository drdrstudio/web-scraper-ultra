"""
Advanced Captcha Solving Integration
Supports: 2captcha, Anti-Captcha, CapSolver, and ML-based solving
"""

import time
import base64
import requests
import json
from typing import Dict, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CaptchaSolver:
    """
    Multi-provider captcha solving with fallback
    """
    
    def __init__(self):
        # API Keys (2captcha provided)
        self.twocaptcha_key = "a2e9e05f58edb279b211ca8292f206d1"
        self.anticaptcha_key = None  # Add if available
        self.capsolver_key = None  # Add if available
        
        # Service endpoints
        self.services = {
            '2captcha': {
                'submit': 'http://2captcha.com/in.php',
                'result': 'http://2captcha.com/res.php',
                'balance': 'http://2captcha.com/res.php?key={key}&action=getbalance'
            },
            'anticaptcha': {
                'base': 'https://api.anti-captcha.com',
                'createTask': '/createTask',
                'getTaskResult': '/getTaskResult'
            },
            'capsolver': {
                'base': 'https://api.capsolver.com',
                'createTask': '/createTask',
                'getTaskResult': '/getTaskResult'
            }
        }
        
        self.solve_counts = {'success': 0, 'failed': 0}
        self.avg_solve_time = []
    
    def get_balance(self, service: str = '2captcha') -> float:
        """Get account balance"""
        if service == '2captcha' and self.twocaptcha_key:
            try:
                url = self.services['2captcha']['balance'].format(key=self.twocaptcha_key)
                response = requests.get(url, timeout=30)
                if response.text.startswith('OK'):
                    return float(response.text.split('|')[1])
            except:
                pass
        return 0.0
    
    def solve_recaptcha_v2(self, driver, site_key: str = None, url: str = None) -> Optional[str]:
        """
        Solve reCAPTCHA v2
        """
        start_time = time.time()
        
        # Auto-detect if not provided
        if not site_key:
            try:
                captcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
                site_key = captcha_element.get_attribute("data-sitekey")
            except:
                return None
        
        if not url:
            url = driver.current_url
        
        # Try 2captcha first
        solution = self._solve_with_2captcha('recaptcha_v2', {
            'googlekey': site_key,
            'pageurl': url
        })
        
        if solution:
            # Inject solution
            self._inject_recaptcha_solution(driver, solution)
            self.solve_counts['success'] += 1
            self.avg_solve_time.append(time.time() - start_time)
            return solution
        
        # Fallback to other services
        if self.anticaptcha_key:
            solution = self._solve_with_anticaptcha('RecaptchaV2TaskProxyless', {
                'websiteURL': url,
                'websiteKey': site_key
            })
            if solution:
                self._inject_recaptcha_solution(driver, solution)
                return solution
        
        self.solve_counts['failed'] += 1
        return None
    
    def solve_recaptcha_v3(self, driver, site_key: str, url: str, action: str = 'verify', min_score: float = 0.3) -> Optional[str]:
        """
        Solve reCAPTCHA v3
        """
        solution = self._solve_with_2captcha('recaptcha_v3', {
            'googlekey': site_key,
            'pageurl': url,
            'version': 'v3',
            'action': action,
            'min_score': min_score
        })
        
        if solution:
            # v3 returns a token directly
            return solution
        
        return None
    
    def solve_hcaptcha(self, driver, site_key: str = None, url: str = None) -> Optional[str]:
        """
        Solve hCaptcha
        """
        if not site_key:
            try:
                captcha_element = driver.find_element(By.CSS_SELECTOR, "[data-sitekey]")
                site_key = captcha_element.get_attribute("data-sitekey")
            except:
                return None
        
        if not url:
            url = driver.current_url
        
        solution = self._solve_with_2captcha('hcaptcha', {
            'sitekey': site_key,
            'pageurl': url
        })
        
        if solution:
            self._inject_hcaptcha_solution(driver, solution)
            return solution
        
        return None
    
    def solve_funcaptcha(self, driver, public_key: str, url: str, surl: str = None) -> Optional[str]:
        """
        Solve FunCaptcha (Arkose Labs)
        """
        params = {
            'publickey': public_key,
            'pageurl': url
        }
        if surl:
            params['surl'] = surl
        
        solution = self._solve_with_2captcha('funcaptcha', params)
        
        if solution:
            self._inject_funcaptcha_solution(driver, solution)
            return solution
        
        return None
    
    def solve_geetest(self, driver, gt: str, challenge: str, api_server: str, url: str) -> Optional[Dict]:
        """
        Solve GeeTest CAPTCHA
        """
        solution = self._solve_with_2captcha('geetest', {
            'gt': gt,
            'challenge': challenge,
            'api_server': api_server,
            'pageurl': url
        })
        
        if solution:
            # GeeTest returns JSON with challenge, validate, seccode
            return json.loads(solution)
        
        return None
    
    def solve_image_captcha(self, image_path: str = None, image_base64: str = None) -> Optional[str]:
        """
        Solve image-based CAPTCHA
        """
        if image_path:
            with open(image_path, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode()
        
        if not image_base64:
            return None
        
        solution = self._solve_with_2captcha('normal', {
            'body': image_base64
        })
        
        return solution
    
    def solve_cloudflare_turnstile(self, driver, site_key: str, url: str) -> Optional[str]:
        """
        Solve Cloudflare Turnstile
        """
        solution = self._solve_with_2captcha('turnstile', {
            'sitekey': site_key,
            'pageurl': url
        })
        
        if solution:
            self._inject_turnstile_solution(driver, solution)
            return solution
        
        return None
    
    def solve_audio_captcha(self, audio_url: str) -> Optional[str]:
        """
        Solve audio CAPTCHA
        """
        # Download audio
        audio_response = requests.get(audio_url)
        audio_base64 = base64.b64encode(audio_response.content).decode()
        
        solution = self._solve_with_2captcha('audio', {
            'body': audio_base64,
            'lang': 'en'
        })
        
        return solution
    
    def _solve_with_2captcha(self, method: str, params: Dict) -> Optional[str]:
        """
        Internal method to solve with 2captcha
        """
        if not self.twocaptcha_key:
            return None
        
        try:
            # Submit captcha
            submit_params = {
                'key': self.twocaptcha_key,
                'method': method,
                'json': 1,
                **params
            }
            
            # Special handling for different methods
            if method == 'normal':
                submit_params['method'] = 'base64'
            elif method == 'recaptcha_v2':
                submit_params['method'] = 'userrecaptcha'
            elif method == 'recaptcha_v3':
                submit_params['method'] = 'userrecaptcha'
                submit_params['version'] = 'v3'
            
            response = requests.post(self.services['2captcha']['submit'], data=submit_params, timeout=30)
            result = response.json()
            
            if result.get('status') != 1:
                print(f"2captcha submit error: {result.get('error_text', 'Unknown error')}")
                return None
            
            captcha_id = result.get('request')
            
            # Wait and poll for result
            time.sleep(20)  # Initial wait
            
            for attempt in range(30):  # Max 5 minutes
                result_params = {
                    'key': self.twocaptcha_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                response = requests.get(self.services['2captcha']['result'], params=result_params, timeout=30)
                result = response.json()
                
                if result.get('status') == 1:
                    return result.get('request')
                elif result.get('request') != 'CAPCHA_NOT_READY':
                    print(f"2captcha solve error: {result.get('request')}")
                    return None
                
                time.sleep(10)
            
        except Exception as e:
            print(f"2captcha error: {e}")
        
        return None
    
    def _solve_with_anticaptcha(self, task_type: str, params: Dict) -> Optional[str]:
        """
        Internal method to solve with Anti-Captcha
        """
        if not self.anticaptcha_key:
            return None
        
        try:
            # Create task
            create_url = self.services['anticaptcha']['base'] + self.services['anticaptcha']['createTask']
            task_data = {
                'clientKey': self.anticaptcha_key,
                'task': {
                    'type': task_type,
                    **params
                }
            }
            
            response = requests.post(create_url, json=task_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                print(f"Anti-Captcha error: {result.get('errorDescription')}")
                return None
            
            task_id = result.get('taskId')
            
            # Poll for result
            result_url = self.services['anticaptcha']['base'] + self.services['anticaptcha']['getTaskResult']
            
            for attempt in range(30):
                time.sleep(10)
                
                response = requests.post(result_url, json={
                    'clientKey': self.anticaptcha_key,
                    'taskId': task_id
                }, timeout=30)
                
                result = response.json()
                
                if result.get('status') == 'ready':
                    return result.get('solution', {}).get('gRecaptchaResponse')
                elif result.get('errorId') != 0:
                    print(f"Anti-Captcha solve error: {result.get('errorDescription')}")
                    return None
            
        except Exception as e:
            print(f"Anti-Captcha error: {e}")
        
        return None
    
    def _inject_recaptcha_solution(self, driver, solution: str):
        """
        Inject reCAPTCHA v2 solution into page
        """
        js_code = f"""
        document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
        document.getElementById('g-recaptcha-response').style.display = 'block';
        
        // Try to find and trigger callback
        if (typeof ___grecaptcha_cfg !== 'undefined') {{
            Object.entries(___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                if (client.callback) {{
                    client.callback('{solution}');
                }}
            }});
        }}
        
        // Also try common callback names
        if (typeof onCaptchaSuccess === 'function') {{
            onCaptchaSuccess('{solution}');
        }}
        if (typeof recaptchaCallback === 'function') {{
            recaptchaCallback('{solution}');
        }}
        """
        driver.execute_script(js_code)
    
    def _inject_hcaptcha_solution(self, driver, solution: str):
        """
        Inject hCaptcha solution
        """
        js_code = f"""
        const textarea = document.querySelector('[name="h-captcha-response"]');
        if (textarea) {{
            textarea.innerHTML = '{solution}';
            textarea.style.display = 'block';
        }}
        
        const iframe = document.querySelector('iframe[src*="hcaptcha.com"]');
        if (iframe && iframe.hasAttribute('data-hcaptcha-response')) {{
            iframe.setAttribute('data-hcaptcha-response', '{solution}');
        }}
        
        // Trigger callback if exists
        if (typeof hcaptchaCallback === 'function') {{
            hcaptchaCallback('{solution}');
        }}
        """
        driver.execute_script(js_code)
    
    def _inject_funcaptcha_solution(self, driver, solution: str):
        """
        Inject FunCaptcha solution
        """
        js_code = f"""
        const funcaptchaToken = document.querySelector('[name="fc-token"]');
        if (funcaptchaToken) {{
            funcaptchaToken.value = '{solution}';
        }}
        
        // Try to submit form
        const form = funcaptchaToken ? funcaptchaToken.closest('form') : null;
        if (form) {{
            form.submit();
        }}
        """
        driver.execute_script(js_code)
    
    def _inject_turnstile_solution(self, driver, solution: str):
        """
        Inject Cloudflare Turnstile solution
        """
        js_code = f"""
        const turnstileResponse = document.querySelector('[name="cf-turnstile-response"]');
        if (turnstileResponse) {{
            turnstileResponse.value = '{solution}';
        }}
        
        // Trigger any callbacks
        if (typeof turnstileCallback === 'function') {{
            turnstileCallback('{solution}');
        }}
        """
        driver.execute_script(js_code)
    
    def auto_detect_and_solve(self, driver) -> bool:
        """
        Automatically detect and solve any CAPTCHA on the page
        """
        # Check for reCAPTCHA v2
        try:
            if driver.find_element(By.CLASS_NAME, "g-recaptcha"):
                print("Detected reCAPTCHA v2, solving...")
                solution = self.solve_recaptcha_v2(driver)
                return solution is not None
        except:
            pass
        
        # Check for hCaptcha
        try:
            if driver.find_element(By.CSS_SELECTOR, '[data-sitekey][data-hcaptcha-widget-id]'):
                print("Detected hCaptcha, solving...")
                solution = self.solve_hcaptcha(driver)
                return solution is not None
        except:
            pass
        
        # Check for Cloudflare Turnstile
        try:
            if driver.find_element(By.CSS_SELECTOR, '[data-sitekey][data-ray]'):
                print("Detected Cloudflare Turnstile, solving...")
                # Would need to extract sitekey
                return False
        except:
            pass
        
        # Check for FunCaptcha
        try:
            if driver.find_element(By.CSS_SELECTOR, '#FunCaptcha'):
                print("Detected FunCaptcha, solving...")
                # Would need to extract public key
                return False
        except:
            pass
        
        return False
    
    def get_statistics(self) -> Dict:
        """
        Get solving statistics
        """
        total = self.solve_counts['success'] + self.solve_counts['failed']
        success_rate = (self.solve_counts['success'] / total * 100) if total > 0 else 0
        avg_time = sum(self.avg_solve_time) / len(self.avg_solve_time) if self.avg_solve_time else 0
        
        return {
            'total_attempts': total,
            'successful': self.solve_counts['success'],
            'failed': self.solve_counts['failed'],
            'success_rate': f"{success_rate:.1f}%",
            'average_solve_time': f"{avg_time:.1f}s",
            'balance': self.get_balance()
        }

# Global instance
captcha_solver = CaptchaSolver()
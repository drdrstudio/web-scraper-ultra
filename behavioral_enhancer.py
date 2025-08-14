"""
Behavioral Enhancement Module
Coordinates all anti-detection features for realistic human-like behavior
"""

import random
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging

logger = logging.getLogger(__name__)

class BehavioralEnhancer:
    """Orchestrates human-like behavioral patterns"""
    
    def __init__(self):
        self.behavior_profiles = {
            'casual_browser': {
                'tab_switches': (0, 3),
                'idle_periods': (5, 30),
                'focus_changes': (1, 5),
                'paste_events': 0.1,
                'typing_speed': (150, 250),  # ms per character
                'scroll_speed': 'normal',
                'mouse_speed': 'normal',
                'attention_span': (10, 60)  # seconds on page
            },
            'power_user': {
                'tab_switches': (5, 15),
                'idle_periods': (1, 10),
                'focus_changes': (10, 30),
                'paste_events': 0.3,
                'typing_speed': (50, 150),
                'scroll_speed': 'fast',
                'mouse_speed': 'fast',
                'attention_span': (5, 30)
            },
            'researcher': {
                'tab_switches': (2, 8),
                'idle_periods': (10, 120),
                'focus_changes': (3, 10),
                'paste_events': 0.2,
                'typing_speed': (100, 200),
                'scroll_speed': 'slow',
                'mouse_speed': 'normal',
                'attention_span': (30, 300)
            },
            'bot_like': {  # Intentionally bot-like for testing
                'tab_switches': (0, 0),
                'idle_periods': (0, 1),
                'focus_changes': (0, 0),
                'paste_events': 0.8,
                'typing_speed': (10, 30),
                'scroll_speed': 'instant',
                'mouse_speed': 'instant',
                'attention_span': (1, 5)
            }
        }
        
        self.current_profile = None
        self.tab_history = []
        self.focus_history = []
        self.action_log = []
        
    def select_profile(self, profile_name: str = None):
        """Select a behavioral profile"""
        if profile_name and profile_name in self.behavior_profiles:
            self.current_profile = self.behavior_profiles[profile_name]
        else:
            # Select based on time of day
            hour = time.localtime().tm_hour
            if 9 <= hour <= 17:  # Work hours
                self.current_profile = self.behavior_profiles['power_user']
            elif 18 <= hour <= 23:  # Evening
                self.current_profile = self.behavior_profiles['casual_browser']
            else:  # Night
                self.current_profile = self.behavior_profiles['researcher']
        
        logger.info(f"Selected behavioral profile: {profile_name or 'auto'}")
        return self.current_profile
    
    def simulate_tab_switching(self, driver):
        """Simulate switching between browser tabs"""
        if not self.current_profile:
            self.select_profile()
        
        num_switches = random.randint(*self.current_profile['tab_switches'])
        
        for _ in range(num_switches):
            try:
                # Open new tab sometimes
                if random.random() < 0.3 and len(driver.window_handles) < 5:
                    driver.execute_script("window.open('');")
                    time.sleep(random.uniform(0.5, 2))
                
                # Switch to random tab
                if len(driver.window_handles) > 1:
                    current_handle = driver.current_window_handle
                    handles = [h for h in driver.window_handles if h != current_handle]
                    if handles:
                        driver.switch_to.window(random.choice(handles))
                        time.sleep(random.uniform(1, 5))
                        
                        # Sometimes close the tab
                        if random.random() < 0.2 and len(driver.window_handles) > 2:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        else:
                            # Switch back
                            driver.switch_to.window(current_handle)
                
                self.tab_history.append(time.time())
                
            except Exception as e:
                logger.warning(f"Tab switching failed: {e}")
    
    def simulate_idle_periods(self):
        """Simulate idle time between actions"""
        if not self.current_profile:
            self.select_profile()
        
        idle_duration = random.uniform(*self.current_profile['idle_periods'])
        
        # Log the idle period
        self.action_log.append({
            'action': 'idle',
            'duration': idle_duration,
            'timestamp': time.time()
        })
        
        logger.debug(f"Idle for {idle_duration:.1f} seconds")
        time.sleep(idle_duration)
    
    def simulate_focus_changes(self, driver):
        """Simulate window focus and blur events"""
        if not self.current_profile:
            self.select_profile()
        
        num_changes = random.randint(*self.current_profile['focus_changes'])
        
        for _ in range(num_changes):
            try:
                # Blur (lose focus)
                driver.execute_script("""
                    window.dispatchEvent(new Event('blur'));
                    document.dispatchEvent(new Event('visibilitychange'));
                    Object.defineProperty(document, 'hidden', {value: true, writable: true});
                    Object.defineProperty(document, 'visibilityState', {value: 'hidden', writable: true});
                """)
                
                # Wait (simulating user doing something else)
                time.sleep(random.uniform(2, 30))
                
                # Focus (regain focus)
                driver.execute_script("""
                    window.dispatchEvent(new Event('focus'));
                    document.dispatchEvent(new Event('visibilitychange'));
                    Object.defineProperty(document, 'hidden', {value: false, writable: true});
                    Object.defineProperty(document, 'visibilityState', {value: 'visible', writable: true});
                """)
                
                self.focus_history.append(time.time())
                
            except Exception as e:
                logger.warning(f"Focus change simulation failed: {e}")
    
    def simulate_paste_event(self, driver, element, text: str):
        """Simulate paste event (Ctrl+V / Cmd+V)"""
        if not self.current_profile:
            self.select_profile()
        
        use_paste = random.random() < self.current_profile['paste_events']
        
        if use_paste:
            try:
                # Click on element
                element.click()
                time.sleep(random.uniform(0.1, 0.3))
                
                # Clear existing text
                element.clear()
                
                # Simulate Ctrl+V / Cmd+V
                driver.execute_script("""
                    var element = arguments[0];
                    var text = arguments[1];
                    
                    // Create paste event
                    var pasteEvent = new ClipboardEvent('paste', {
                        clipboardData: new DataTransfer(),
                        bubbles: true,
                        cancelable: true
                    });
                    
                    // Set clipboard data
                    pasteEvent.clipboardData.setData('text/plain', text);
                    
                    // Dispatch event
                    element.dispatchEvent(pasteEvent);
                    
                    // Set value
                    element.value = text;
                    
                    // Trigger input event
                    element.dispatchEvent(new Event('input', {bubbles: true}));
                    element.dispatchEvent(new Event('change', {bubbles: true}));
                """, element, text)
                
                logger.debug("Simulated paste event")
                return True
                
            except Exception as e:
                logger.warning(f"Paste simulation failed: {e}")
        
        return False
    
    def simulate_human_typing(self, element, text: str):
        """Simulate human-like typing with variable speed and errors"""
        if not self.current_profile:
            self.select_profile()
        
        element.click()
        element.clear()
        
        typing_speed = self.current_profile['typing_speed']
        
        for i, char in enumerate(text):
            # Variable typing speed
            delay = random.uniform(typing_speed[0], typing_speed[1]) / 1000
            
            # Occasionally make typos and correct them
            if random.random() < 0.02 and i > 0 and i < len(text) - 1:  # 2% typo rate
                # Make a typo
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(delay)
                
                # Realize mistake and backspace
                time.sleep(random.uniform(0.2, 0.5))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(delay)
            
            # Type the correct character
            element.send_keys(char)
            time.sleep(delay)
            
            # Occasionally pause (thinking)
            if random.random() < 0.05:  # 5% chance
                time.sleep(random.uniform(0.5, 2))
    
    def simulate_reading_pattern(self, driver, content_length: int = None):
        """Simulate natural reading patterns with scrolling"""
        if not self.current_profile:
            self.select_profile()
        
        # Estimate reading time based on content
        if content_length:
            # Average reading speed: 200-250 words per minute
            words = content_length / 5  # Rough estimate: 5 chars per word
            base_reading_time = (words / 225) * 60  # seconds
        else:
            base_reading_time = random.uniform(*self.current_profile['attention_span'])
        
        # Add variance
        actual_reading_time = base_reading_time * random.uniform(0.7, 1.3)
        
        # Scroll patterns
        scroll_speed = self.current_profile['scroll_speed']
        
        if scroll_speed == 'slow':
            scroll_intervals = [random.uniform(3, 8) for _ in range(int(actual_reading_time / 5))]
        elif scroll_speed == 'normal':
            scroll_intervals = [random.uniform(2, 5) for _ in range(int(actual_reading_time / 3))]
        elif scroll_speed == 'fast':
            scroll_intervals = [random.uniform(1, 3) for _ in range(int(actual_reading_time / 2))]
        else:  # instant
            scroll_intervals = [0.1]
        
        start_time = time.time()
        
        for interval in scroll_intervals:
            if time.time() - start_time > actual_reading_time:
                break
            
            # Scroll down
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(interval)
            
            # Sometimes scroll back up (re-reading)
            if random.random() < 0.15:  # 15% chance
                driver.execute_script(f"window.scrollBy(0, -{scroll_amount // 2});")
                time.sleep(interval * 0.5)
            
            # Sometimes pause (focused reading)
            if random.random() < 0.1:  # 10% chance
                time.sleep(random.uniform(2, 10))
        
        # Log reading pattern
        self.action_log.append({
            'action': 'reading',
            'duration': time.time() - start_time,
            'timestamp': time.time()
        })
    
    def simulate_mouse_patterns(self, driver):
        """Simulate natural mouse movement patterns"""
        if not self.current_profile:
            self.select_profile()
        
        mouse_speed = self.current_profile['mouse_speed']
        
        try:
            # Get page dimensions
            width = driver.execute_script("return document.body.scrollWidth")
            height = driver.execute_script("return window.innerHeight")
            
            # Number of mouse movements
            if mouse_speed == 'slow':
                num_movements = random.randint(2, 5)
            elif mouse_speed == 'normal':
                num_movements = random.randint(5, 10)
            elif mouse_speed == 'fast':
                num_movements = random.randint(10, 20)
            else:  # instant
                num_movements = 1
            
            action = ActionChains(driver)
            
            for _ in range(num_movements):
                # Random position
                x = random.randint(50, min(width - 50, 1000))
                y = random.randint(50, min(height - 50, 800))
                
                # Move to position with bezier curve simulation
                driver.execute_script("""
                    var event = new MouseEvent('mousemove', {
                        clientX: %d,
                        clientY: %d,
                        bubbles: true,
                        cancelable: true
                    });
                    document.dispatchEvent(event);
                """ % (x, y))
                
                # Sometimes hover over elements
                if random.random() < 0.3:  # 30% chance
                    elements = driver.find_elements(By.TAG_NAME, 'a')
                    if elements:
                        random_element = random.choice(elements[:10])  # Pick from first 10 links
                        try:
                            action.move_to_element(random_element).perform()
                            time.sleep(random.uniform(0.5, 2))
                        except:
                            pass
                
                time.sleep(random.uniform(0.1, 1))
            
        except Exception as e:
            logger.warning(f"Mouse pattern simulation failed: {e}")
    
    def apply_full_enhancement(self, driver, url: str = None):
        """Apply all behavioral enhancements"""
        logger.info("Applying full behavioral enhancement suite")
        
        # Select appropriate profile
        self.select_profile()
        
        # Pre-page load enhancements
        self.simulate_tab_switching(driver)
        self.simulate_focus_changes(driver)
        
        # Navigate to URL if provided
        if url:
            driver.get(url)
        
        # Post-page load enhancements
        time.sleep(random.uniform(0.5, 2))  # Initial page load observation
        
        # Get content length for reading simulation
        try:
            content_length = len(driver.find_element(By.TAG_NAME, 'body').text)
        except:
            content_length = None
        
        # Apply reading and interaction patterns
        self.simulate_reading_pattern(driver, content_length)
        self.simulate_mouse_patterns(driver)
        
        # Random idle periods
        if random.random() < 0.3:  # 30% chance
            self.simulate_idle_periods()
        
        logger.info("Behavioral enhancement complete")
    
    def get_behavioral_fingerprint(self) -> Dict:
        """Get current behavioral fingerprint"""
        if not self.current_profile:
            self.select_profile()
        
        return {
            'profile': self.current_profile,
            'tab_switches': len(self.tab_history),
            'focus_changes': len(self.focus_history),
            'actions': len(self.action_log),
            'last_action': self.action_log[-1] if self.action_log else None,
            'session_duration': time.time() - self.action_log[0]['timestamp'] if self.action_log else 0
        }
    
    def reset_session(self):
        """Reset behavioral tracking for new session"""
        self.tab_history.clear()
        self.focus_history.clear()
        self.action_log.clear()
        logger.info("Behavioral session reset")

# Singleton instance
behavioral_enhancer = BehavioralEnhancer()
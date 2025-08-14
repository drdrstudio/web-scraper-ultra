"""
Mobile Device Simulation Module
Implements realistic touch events, device sensors, and mobile-specific behaviors
"""

import random
import time
import math
import json
from typing import Dict, List, Tuple, Optional
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
import logging

logger = logging.getLogger(__name__)

class MobileSimulator:
    """Simulates mobile device interactions and sensors"""
    
    def __init__(self):
        self.device_profiles = {
            'iPhone 15 Pro': {
                'viewport': {'width': 393, 'height': 852},
                'screen': {'width': 393, 'height': 852},
                'deviceScaleFactor': 3,
                'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                'hasTouch': True,
                'isMobile': True,
                'platform': 'iOS',
                'touchPoints': 5,
                'orientation': {'angle': 0, 'type': 'portrait-primary'},
                'battery': {'level': 0.85, 'charging': False},
                'connection': {'effectiveType': '4g', 'rtt': 50, 'downlink': 10}
            },
            'Samsung Galaxy S24': {
                'viewport': {'width': 412, 'height': 915},
                'screen': {'width': 412, 'height': 915},
                'deviceScaleFactor': 2.625,
                'userAgent': 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36',
                'hasTouch': True,
                'isMobile': True,
                'platform': 'Android',
                'touchPoints': 10,
                'orientation': {'angle': 0, 'type': 'portrait-primary'},
                'battery': {'level': 0.72, 'charging': True},
                'connection': {'effectiveType': '5g', 'rtt': 30, 'downlink': 50}
            },
            'iPad Pro': {
                'viewport': {'width': 1024, 'height': 1366},
                'screen': {'width': 1024, 'height': 1366},
                'deviceScaleFactor': 2,
                'userAgent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                'hasTouch': True,
                'isMobile': True,
                'platform': 'iOS',
                'touchPoints': 5,
                'orientation': {'angle': 0, 'type': 'landscape-primary'},
                'battery': {'level': 0.95, 'charging': True},
                'connection': {'effectiveType': 'wifi', 'rtt': 10, 'downlink': 100}
            },
            'Google Pixel 8': {
                'viewport': {'width': 412, 'height': 869},
                'screen': {'width': 412, 'height': 869},
                'deviceScaleFactor': 2.625,
                'userAgent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36',
                'hasTouch': True,
                'isMobile': True,
                'platform': 'Android',
                'touchPoints': 10,
                'orientation': {'angle': 0, 'type': 'portrait-primary'},
                'battery': {'level': 0.68, 'charging': False},
                'connection': {'effectiveType': '4g', 'rtt': 60, 'downlink': 8}
            }
        }
        
        self.current_device = None
        self.touch_history = []
        
    def select_device(self, device_name: str = None) -> Dict:
        """Select a mobile device profile"""
        if device_name and device_name in self.device_profiles:
            self.current_device = self.device_profiles[device_name]
        else:
            self.current_device = random.choice(list(self.device_profiles.values()))
        
        logger.info(f"Selected device profile: {self.current_device.get('platform')}")
        return self.current_device
    
    def inject_mobile_overrides(self, driver) -> bool:
        """Inject mobile device overrides into browser"""
        if not self.current_device:
            self.select_device()
        
        try:
            # Override navigator properties
            override_script = """
            Object.defineProperty(navigator, 'maxTouchPoints', {
                get: () => %d
            });
            
            Object.defineProperty(navigator, 'platform', {
                get: () => '%s'
            });
            
            // Touch event support
            window.ontouchstart = null;
            window.ontouchmove = null;
            window.ontouchend = null;
            
            // Device motion and orientation
            window.DeviceOrientationEvent = function() {};
            window.DeviceMotionEvent = function() {};
            
            // Battery API
            navigator.getBattery = async () => ({
                level: %f,
                charging: %s,
                chargingTime: %d,
                dischargingTime: %d
            });
            
            // Network Information API
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '%s',
                    rtt: %d,
                    downlink: %f,
                    saveData: false
                })
            });
            
            // Geolocation with mobile accuracy
            const originalGeolocation = navigator.geolocation.getCurrentPosition;
            navigator.geolocation.getCurrentPosition = function(success, error, options) {
                const position = {
                    coords: {
                        latitude: %f + (Math.random() - 0.5) * 0.001,
                        longitude: %f + (Math.random() - 0.5) * 0.001,
                        accuracy: %f,
                        altitude: null,
                        altitudeAccuracy: null,
                        heading: Math.random() * 360,
                        speed: Math.random() * 2
                    },
                    timestamp: Date.now()
                };
                setTimeout(() => success(position), Math.random() * 2000 + 500);
            };
            """ % (
                self.current_device['touchPoints'],
                self.current_device['platform'],
                self.current_device['battery']['level'],
                'true' if self.current_device['battery']['charging'] else 'false',
                random.randint(0, 7200),  # Charging time
                random.randint(3600, 28800),  # Discharging time
                self.current_device['connection']['effectiveType'],
                self.current_device['connection']['rtt'],
                self.current_device['connection']['downlink'],
                37.7749 + random.uniform(-0.1, 0.1),  # Latitude (San Francisco + variation)
                -122.4194 + random.uniform(-0.1, 0.1),  # Longitude
                random.uniform(5, 50)  # GPS accuracy in meters
            )
            
            driver.execute_script(override_script)
            
            # Set viewport and device metrics
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': self.current_device['viewport']['width'],
                'height': self.current_device['viewport']['height'],
                'deviceScaleFactor': self.current_device['deviceScaleFactor'],
                'mobile': self.current_device['isMobile'],
                'screenOrientation': self.current_device['orientation']
            })
            
            # Enable touch emulation
            driver.execute_cdp_cmd('Emulation.setTouchEmulationEnabled', {
                'enabled': True,
                'maxTouchPoints': self.current_device['touchPoints']
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject mobile overrides: {e}")
            return False
    
    def generate_touch_path(self, start: Tuple[int, int], end: Tuple[int, int], 
                           gesture_type: str = 'swipe') -> List[Tuple[int, int, float]]:
        """Generate realistic touch path with pressure variations"""
        points = []
        
        if gesture_type == 'tap':
            # Simple tap with slight movement
            duration = random.uniform(0.05, 0.15)
            points.append((*start, 0.3))  # Initial touch
            points.append((start[0] + random.randint(-2, 2), 
                          start[1] + random.randint(-2, 2), 0.5))  # Peak pressure
            points.append((*start, 0.1))  # Release
            
        elif gesture_type == 'swipe':
            # Bezier curve for natural swipe
            duration = random.uniform(0.2, 0.5)
            steps = 20
            
            # Control points for bezier curve
            control1 = (
                start[0] + (end[0] - start[0]) * 0.3 + random.randint(-20, 20),
                start[1] + (end[1] - start[1]) * 0.3 + random.randint(-20, 20)
            )
            control2 = (
                start[0] + (end[0] - start[0]) * 0.7 + random.randint(-20, 20),
                start[1] + (end[1] - start[1]) * 0.7 + random.randint(-20, 20)
            )
            
            for i in range(steps):
                t = i / (steps - 1)
                # Cubic bezier formula
                x = (1-t)**3 * start[0] + 3*(1-t)**2*t * control1[0] + \
                    3*(1-t)*t**2 * control2[0] + t**3 * end[0]
                y = (1-t)**3 * start[1] + 3*(1-t)**2*t * control1[1] + \
                    3*(1-t)*t**2 * control2[1] + t**3 * end[1]
                
                # Pressure curve (higher in middle)
                pressure = 0.3 + 0.4 * math.sin(t * math.pi)
                
                points.append((int(x), int(y), pressure))
        
        elif gesture_type == 'scroll':
            # Fling-like scroll with acceleration
            duration = random.uniform(0.3, 0.8)
            steps = 30
            
            for i in range(steps):
                t = i / (steps - 1)
                # Ease-out curve for deceleration
                progress = 1 - (1 - t) ** 3
                
                x = start[0] + (end[0] - start[0]) * progress
                y = start[1] + (end[1] - start[1]) * progress
                
                # Pressure decreases over time
                pressure = 0.5 * (1 - t * 0.5)
                
                points.append((int(x), int(y), pressure))
        
        elif gesture_type == 'pinch':
            # Two-finger pinch gesture
            duration = random.uniform(0.4, 0.7)
            steps = 20
            center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            
            for i in range(steps):
                t = i / (steps - 1)
                # Fingers move apart/together
                distance = 50 * (1 - t) if random.random() < 0.5 else 50 * t
                
                finger1 = (
                    center[0] - distance + random.randint(-3, 3),
                    center[1] + random.randint(-3, 3)
                )
                finger2 = (
                    center[0] + distance + random.randint(-3, 3),
                    center[1] + random.randint(-3, 3)
                )
                
                points.append((*finger1, 0.4))
                points.append((*finger2, 0.4))
        
        return points
    
    def simulate_touch_event(self, driver, element, gesture_type: str = 'tap'):
        """Simulate a touch event on an element"""
        try:
            location = element.location
            size = element.size
            
            # Random point within element
            start_x = location['x'] + random.randint(5, size['width'] - 5)
            start_y = location['y'] + random.randint(5, size['height'] - 5)
            
            if gesture_type == 'tap':
                self.perform_tap(driver, start_x, start_y)
            elif gesture_type == 'swipe':
                end_x = start_x + random.randint(-100, 100)
                end_y = start_y + random.randint(-200, 200)
                self.perform_swipe(driver, start_x, start_y, end_x, end_y)
            elif gesture_type == 'long_press':
                self.perform_long_press(driver, start_x, start_y)
            
            # Record touch event
            self.touch_history.append({
                'timestamp': time.time(),
                'gesture': gesture_type,
                'location': (start_x, start_y)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Touch simulation failed: {e}")
            return False
    
    def perform_tap(self, driver, x: int, y: int):
        """Perform a tap at coordinates"""
        script = """
        var touch = new Touch({
            identifier: Date.now(),
            target: document.elementFromPoint(%d, %d),
            clientX: %d,
            clientY: %d,
            screenX: %d,
            screenY: %d,
            pageX: %d,
            pageY: %d,
            radiusX: %f,
            radiusY: %f,
            rotationAngle: %f,
            force: %f
        });
        
        var touchEvent = new TouchEvent('touchstart', {
            touches: [touch],
            targetTouches: [touch],
            changedTouches: [touch],
            bubbles: true,
            cancelable: true
        });
        
        document.elementFromPoint(%d, %d).dispatchEvent(touchEvent);
        
        setTimeout(() => {
            var endEvent = new TouchEvent('touchend', {
                touches: [],
                targetTouches: [],
                changedTouches: [touch],
                bubbles: true,
                cancelable: true
            });
            document.elementFromPoint(%d, %d).dispatchEvent(endEvent);
        }, %d);
        """ % (
            x, y, x, y, x, y, x, y,
            random.uniform(5, 15),  # radiusX
            random.uniform(5, 15),  # radiusY
            random.uniform(0, 360),  # rotation
            random.uniform(0.3, 0.7),  # force
            x, y,
            x, y,
            random.randint(50, 150)  # tap duration
        )
        
        driver.execute_script(script)
        time.sleep(random.uniform(0.1, 0.3))
    
    def perform_swipe(self, driver, start_x: int, start_y: int, end_x: int, end_y: int):
        """Perform a swipe gesture"""
        path = self.generate_touch_path((start_x, start_y), (end_x, end_y), 'swipe')
        
        script = """
        var touches = [];
        var path = %s;
        var startTime = Date.now();
        
        function dispatchTouchEvent(type, point, index) {
            var touch = new Touch({
                identifier: 1,
                target: document.elementFromPoint(point[0], point[1]),
                clientX: point[0],
                clientY: point[1],
                screenX: point[0],
                screenY: point[1],
                pageX: point[0],
                pageY: point[1],
                radiusX: 10,
                radiusY: 10,
                rotationAngle: 0,
                force: point[2]
            });
            
            var event = new TouchEvent(type, {
                touches: type === 'touchend' ? [] : [touch],
                targetTouches: type === 'touchend' ? [] : [touch],
                changedTouches: [touch],
                bubbles: true,
                cancelable: true
            });
            
            document.elementFromPoint(point[0], point[1]).dispatchEvent(event);
        }
        
        // Start touch
        dispatchTouchEvent('touchstart', path[0], 0);
        
        // Move through path
        path.slice(1, -1).forEach((point, index) => {
            setTimeout(() => {
                dispatchTouchEvent('touchmove', point, index + 1);
            }, (index + 1) * 20);
        });
        
        // End touch
        setTimeout(() => {
            dispatchTouchEvent('touchend', path[path.length - 1], path.length - 1);
        }, path.length * 20);
        """ % json.dumps(path)
        
        driver.execute_script(script)
        time.sleep(len(path) * 0.02 + 0.1)
    
    def perform_long_press(self, driver, x: int, y: int, duration: float = None):
        """Perform a long press at coordinates"""
        if duration is None:
            duration = random.uniform(0.5, 1.5)
        
        script = """
        var touch = new Touch({
            identifier: Date.now(),
            target: document.elementFromPoint(%d, %d),
            clientX: %d,
            clientY: %d,
            screenX: %d,
            screenY: %d,
            pageX: %d,
            pageY: %d,
            radiusX: %f,
            radiusY: %f,
            rotationAngle: 0,
            force: %f
        });
        
        var startEvent = new TouchEvent('touchstart', {
            touches: [touch],
            targetTouches: [touch],
            changedTouches: [touch],
            bubbles: true,
            cancelable: true
        });
        
        document.elementFromPoint(%d, %d).dispatchEvent(startEvent);
        
        // Simulate pressure increase
        setTimeout(() => {
            touch.force = %f;
            var moveEvent = new TouchEvent('touchmove', {
                touches: [touch],
                targetTouches: [touch],
                changedTouches: [touch],
                bubbles: true,
                cancelable: true
            });
            document.elementFromPoint(%d, %d).dispatchEvent(moveEvent);
        }, 100);
        
        // End after duration
        setTimeout(() => {
            var endEvent = new TouchEvent('touchend', {
                touches: [],
                targetTouches: [],
                changedTouches: [touch],
                bubbles: true,
                cancelable: true
            });
            document.elementFromPoint(%d, %d).dispatchEvent(endEvent);
        }, %d);
        """ % (
            x, y, x, y, x, y, x, y,
            random.uniform(8, 20),  # radiusX
            random.uniform(8, 20),  # radiusY
            0.3,  # initial force
            x, y,
            0.8,  # increased force
            x, y,
            x, y,
            int(duration * 1000)
        )
        
        driver.execute_script(script)
        time.sleep(duration + 0.1)
    
    def simulate_device_orientation(self, driver, alpha: float = None, 
                                  beta: float = None, gamma: float = None):
        """Simulate device orientation changes"""
        if alpha is None:
            alpha = random.uniform(0, 360)
        if beta is None:
            beta = random.uniform(-90, 90)
        if gamma is None:
            gamma = random.uniform(-90, 90)
        
        script = """
        var event = new DeviceOrientationEvent('deviceorientation', {
            alpha: %f,
            beta: %f,
            gamma: %f,
            absolute: false
        });
        window.dispatchEvent(event);
        """ % (alpha, beta, gamma)
        
        driver.execute_script(script)
    
    def simulate_device_motion(self, driver):
        """Simulate device motion (accelerometer)"""
        script = """
        var event = new DeviceMotionEvent('devicemotion', {
            acceleration: {
                x: %f,
                y: %f,
                z: %f
            },
            accelerationIncludingGravity: {
                x: %f,
                y: %f,
                z: %f
            },
            rotationRate: {
                alpha: %f,
                beta: %f,
                gamma: %f
            },
            interval: 16
        });
        window.dispatchEvent(event);
        """ % (
            random.uniform(-0.5, 0.5),  # acceleration x
            random.uniform(-0.5, 0.5),  # acceleration y
            random.uniform(-0.5, 0.5),  # acceleration z
            random.uniform(-0.5, 0.5),  # with gravity x
            random.uniform(-10, -9),    # with gravity y (gravity)
            random.uniform(-0.5, 0.5),  # with gravity z
            random.uniform(-5, 5),       # rotation alpha
            random.uniform(-5, 5),       # rotation beta
            random.uniform(-5, 5)        # rotation gamma
        )
        
        driver.execute_script(script)
    
    def simulate_network_change(self, driver, connection_type: str = None):
        """Simulate network connection changes"""
        if connection_type is None:
            connection_type = random.choice(['wifi', '4g', '3g', 'slow-2g', 'offline'])
        
        network_profiles = {
            'wifi': {'downlink': 30, 'rtt': 10, 'effectiveType': 'wifi'},
            '4g': {'downlink': 10, 'rtt': 50, 'effectiveType': '4g'},
            '3g': {'downlink': 1.5, 'rtt': 100, 'effectiveType': '3g'},
            'slow-2g': {'downlink': 0.05, 'rtt': 300, 'effectiveType': 'slow-2g'},
            'offline': {'downlink': 0, 'rtt': 0, 'effectiveType': 'offline'}
        }
        
        profile = network_profiles[connection_type]
        
        try:
            driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
                'offline': connection_type == 'offline',
                'downloadThroughput': profile['downlink'] * 1024 * 1024 / 8,
                'uploadThroughput': profile['downlink'] * 1024 * 1024 / 16,
                'latency': profile['rtt']
            })
            logger.info(f"Network changed to: {connection_type}")
        except Exception as e:
            logger.warning(f"Could not emulate network conditions: {e}")

# Singleton instance
mobile_simulator = MobileSimulator()
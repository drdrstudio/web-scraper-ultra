"""
WebAssembly Fingerprinting Protection Module
Protects against WASM-based fingerprinting and adds noise to prevent tracking
"""

import random
import hashlib
import json
import base64
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class WASMProtection:
    """WebAssembly fingerprinting protection and spoofing"""
    
    def __init__(self):
        # WASM execution profiles from real browsers
        self.wasm_profiles = {
            'chrome_v8': {
                'compile_time_variance': (0.8, 1.2),
                'execution_time_variance': (0.9, 1.1),
                'memory_growth_rate': 65536,
                'table_growth_rate': 1,
                'features': {
                    'threads': True,
                    'simd': True,
                    'bulk_memory': True,
                    'reference_types': True,
                    'tail_call': False,
                    'gc': False,
                    'memory64': False,
                    'exception_handling': True,
                    'extended_const': True
                },
                'compile_hints': ['baseline', 'optimized'],
                'gc_characteristics': {
                    'minor_gc_interval': (100, 500),
                    'major_gc_interval': (1000, 5000)
                }
            },
            'firefox_spidermonkey': {
                'compile_time_variance': (0.7, 1.3),
                'execution_time_variance': (0.85, 1.15),
                'memory_growth_rate': 65536,
                'table_growth_rate': 1,
                'features': {
                    'threads': True,
                    'simd': True,
                    'bulk_memory': True,
                    'reference_types': True,
                    'tail_call': True,
                    'gc': False,
                    'memory64': False,
                    'exception_handling': True,
                    'extended_const': True
                },
                'compile_hints': ['baseline', 'ion'],
                'gc_characteristics': {
                    'minor_gc_interval': (150, 450),
                    'major_gc_interval': (1500, 4500)
                }
            },
            'safari_jsc': {
                'compile_time_variance': (0.9, 1.4),
                'execution_time_variance': (0.95, 1.2),
                'memory_growth_rate': 65536,
                'table_growth_rate': 1,
                'features': {
                    'threads': False,
                    'simd': True,
                    'bulk_memory': True,
                    'reference_types': True,
                    'tail_call': False,
                    'gc': False,
                    'memory64': False,
                    'exception_handling': False,
                    'extended_const': True
                },
                'compile_hints': ['bbq', 'omg'],
                'gc_characteristics': {
                    'minor_gc_interval': (200, 600),
                    'major_gc_interval': (2000, 6000)
                }
            }
        }
        
        self.current_profile = None
        self.noise_level = 0.1  # 10% noise by default
        
        # Cryptographic operation timing profiles
        self.crypto_profiles = {
            'sha256': {'base_time': 0.001, 'variance': 0.0002},
            'aes': {'base_time': 0.002, 'variance': 0.0003},
            'rsa': {'base_time': 0.01, 'variance': 0.002},
            'ecdsa': {'base_time': 0.005, 'variance': 0.001}
        }
    
    def select_profile(self, browser: str = None) -> Dict:
        """Select a WASM profile based on browser"""
        if browser and browser.lower() in ['chrome', 'chromium', 'edge']:
            self.current_profile = self.wasm_profiles['chrome_v8']
        elif browser and browser.lower() in ['firefox', 'mozilla']:
            self.current_profile = self.wasm_profiles['firefox_spidermonkey']
        elif browser and browser.lower() in ['safari', 'webkit']:
            self.current_profile = self.wasm_profiles['safari_jsc']
        else:
            self.current_profile = random.choice(list(self.wasm_profiles.values()))
        
        return self.current_profile
    
    def inject_wasm_overrides(self, driver) -> bool:
        """Inject WebAssembly API overrides"""
        if not self.current_profile:
            self.select_profile()
        
        try:
            override_script = """
            (function() {
                // Store original WebAssembly functions
                const originalCompile = WebAssembly.compile;
                const originalInstantiate = WebAssembly.instantiate;
                const originalCompileStreaming = WebAssembly.compileStreaming;
                const originalInstantiateStreaming = WebAssembly.instantiateStreaming;
                
                // Profile configuration
                const profile = %s;
                const noiseLevel = %f;
                
                // Add timing noise
                function addTimingNoise(baseTime) {
                    const variance = baseTime * noiseLevel;
                    return baseTime + (Math.random() - 0.5) * variance * 2;
                }
                
                // Override WebAssembly.compile
                WebAssembly.compile = function(bytes) {
                    const startTime = performance.now();
                    return originalCompile.call(this, bytes).then(module => {
                        // Add artificial delay based on profile
                        const compileTime = (performance.now() - startTime) * 
                            (profile.compile_time_variance[0] + Math.random() * 
                            (profile.compile_time_variance[1] - profile.compile_time_variance[0]));
                        
                        return new Promise(resolve => {
                            setTimeout(() => resolve(module), addTimingNoise(compileTime));
                        });
                    });
                };
                
                // Override WebAssembly.instantiate
                WebAssembly.instantiate = function(bytesOrModule, importObject) {
                    const startTime = performance.now();
                    return originalInstantiate.call(this, bytesOrModule, importObject).then(result => {
                        const execTime = (performance.now() - startTime) * 
                            (profile.execution_time_variance[0] + Math.random() * 
                            (profile.execution_time_variance[1] - profile.execution_time_variance[0]));
                        
                        return new Promise(resolve => {
                            setTimeout(() => resolve(result), addTimingNoise(execTime));
                        });
                    });
                };
                
                // Override streaming APIs
                if (WebAssembly.compileStreaming) {
                    WebAssembly.compileStreaming = function(source) {
                        return originalCompileStreaming.call(this, source).then(module => {
                            const delay = Math.random() * 10 + 5; // 5-15ms delay
                            return new Promise(resolve => {
                                setTimeout(() => resolve(module), delay);
                            });
                        });
                    };
                }
                
                if (WebAssembly.instantiateStreaming) {
                    WebAssembly.instantiateStreaming = function(source, importObject) {
                        return originalInstantiateStreaming.call(this, source, importObject).then(result => {
                            const delay = Math.random() * 15 + 10; // 10-25ms delay
                            return new Promise(resolve => {
                                setTimeout(() => resolve(result), delay);
                            });
                        });
                    };
                }
                
                // Override Memory growth
                const OriginalMemory = WebAssembly.Memory;
                WebAssembly.Memory = function(descriptor) {
                    // Add noise to initial memory size
                    if (descriptor.initial) {
                        descriptor.initial = Math.max(1, descriptor.initial + Math.floor(Math.random() * 3 - 1));
                    }
                    return new OriginalMemory(descriptor);
                };
                
                // Override Table
                const OriginalTable = WebAssembly.Table;
                WebAssembly.Table = function(descriptor) {
                    // Add noise to table size
                    if (descriptor.initial) {
                        descriptor.initial = Math.max(0, descriptor.initial + Math.floor(Math.random() * 2));
                    }
                    return new OriginalTable(descriptor);
                };
                
                // Feature detection spoofing
                Object.defineProperty(WebAssembly, 'validate', {
                    value: function(bytes) {
                        // Add some delay to validation
                        const delay = Math.random() * 2;
                        const result = WebAssembly.validate.call(this, bytes);
                        return new Promise(resolve => {
                            setTimeout(() => resolve(result), delay);
                        });
                    }
                });
                
                console.log('WASM protection injected');
            })();
            """ % (json.dumps(self.current_profile), self.noise_level)
            
            driver.execute_script(override_script)
            
            # Also inject performance API noise
            self._inject_performance_noise(driver)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject WASM overrides: {e}")
            return False
    
    def _inject_performance_noise(self, driver):
        """Inject noise into Performance API measurements"""
        script = """
        (function() {
            const originalNow = performance.now;
            const originalMeasure = performance.measure;
            const noiseLevel = %f;
            
            // Override performance.now()
            performance.now = function() {
                const realTime = originalNow.call(this);
                // Add microsecond-level noise
                const noise = (Math.random() - 0.5) * noiseLevel * 10; // ±5ms max at 0.1 noise level
                return realTime + noise;
            };
            
            // Override performance.measure()
            performance.measure = function(name, startMark, endMark) {
                const result = originalMeasure.call(this, name, startMark, endMark);
                // Add noise to the duration
                if (result && result.duration !== undefined) {
                    result.duration += (Math.random() - 0.5) * noiseLevel * result.duration;
                }
                return result;
            };
            
            // Override crypto.subtle timing
            if (window.crypto && window.crypto.subtle) {
                const originalDigest = crypto.subtle.digest;
                crypto.subtle.digest = async function(algorithm, data) {
                    const startTime = performance.now();
                    const result = await originalDigest.call(this, algorithm, data);
                    
                    // Add realistic processing delay
                    const processingTime = data.byteLength * 0.00001 + Math.random() * 0.001;
                    await new Promise(resolve => setTimeout(resolve, processingTime));
                    
                    return result;
                };
            }
        })();
        """ % self.noise_level
        
        driver.execute_script(script)
    
    def inject_shared_array_buffer_protection(self, driver):
        """Protect against SharedArrayBuffer timing attacks"""
        script = """
        (function() {
            // Check if SharedArrayBuffer is available
            if (typeof SharedArrayBuffer !== 'undefined') {
                const OriginalSharedArrayBuffer = SharedArrayBuffer;
                
                // Override constructor
                window.SharedArrayBuffer = function(length) {
                    // Add noise to length
                    const noisyLength = length + Math.floor(Math.random() * 16) * 4;
                    return new OriginalSharedArrayBuffer(noisyLength);
                };
                
                // Copy prototype
                window.SharedArrayBuffer.prototype = OriginalSharedArrayBuffer.prototype;
            }
            
            // Disable high-resolution timers if they exist
            if (typeof Atomics !== 'undefined') {
                const originalWait = Atomics.wait;
                Atomics.wait = function(typedArray, index, value, timeout) {
                    // Add noise to timeout
                    if (timeout !== undefined) {
                        timeout = timeout * (1 + (Math.random() - 0.5) * 0.1);
                    }
                    return originalWait.call(this, typedArray, index, value, timeout);
                };
            }
        })();
        """
        
        try:
            driver.execute_script(script)
        except Exception as e:
            logger.warning(f"Could not inject SharedArrayBuffer protection: {e}")
    
    def inject_webgl_compute_protection(self, driver):
        """Protect against WebGL compute shader fingerprinting"""
        script = """
        (function() {
            // Get WebGL contexts
            const getContext = HTMLCanvasElement.prototype.getContext;
            
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                const context = getContext.call(this, type, attributes);
                
                if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') {
                    // Override readPixels to add noise
                    const originalReadPixels = context.readPixels;
                    context.readPixels = function(x, y, width, height, format, type, pixels) {
                        originalReadPixels.call(this, x, y, width, height, format, type, pixels);
                        
                        // Add noise to pixel data
                        if (pixels) {
                            for (let i = 0; i < pixels.length; i++) {
                                if (Math.random() < 0.001) { // 0.1% of pixels
                                    pixels[i] = (pixels[i] + Math.floor(Math.random() * 3 - 1)) & 0xFF;
                                }
                            }
                        }
                    };
                    
                    // Override getParameter for compute-related queries
                    const originalGetParameter = context.getParameter;
                    context.getParameter = function(pname) {
                        let result = originalGetParameter.call(this, pname);
                        
                        // Add noise to certain parameters
                        const noiseParams = [
                            context.MAX_TEXTURE_SIZE,
                            context.MAX_VERTEX_TEXTURE_IMAGE_UNITS,
                            context.MAX_COMBINED_TEXTURE_IMAGE_UNITS,
                            context.MAX_VERTEX_ATTRIBS,
                            context.MAX_VARYING_VECTORS,
                            context.MAX_VERTEX_UNIFORM_VECTORS,
                            context.MAX_FRAGMENT_UNIFORM_VECTORS
                        ];
                        
                        if (noiseParams.includes(pname) && typeof result === 'number') {
                            // Add small variance
                            result = result + Math.floor(Math.random() * 3 - 1);
                        }
                        
                        return result;
                    };
                }
                
                return context;
            };
        })();
        """
        
        try:
            driver.execute_script(script)
        except Exception as e:
            logger.warning(f"Could not inject WebGL compute protection: {e}")
    
    def inject_audio_worklet_protection(self, driver):
        """Protect against AudioWorklet fingerprinting"""
        script = """
        (function() {
            if (window.AudioWorkletProcessor) {
                const OriginalProcessor = AudioWorkletProcessor;
                
                window.AudioWorkletProcessor = class extends OriginalProcessor {
                    process(inputs, outputs, parameters) {
                        // Add noise to audio processing
                        const result = super.process(inputs, outputs, parameters);
                        
                        // Add small amount of noise to outputs
                        for (let output of outputs) {
                            for (let channel of output) {
                                for (let i = 0; i < channel.length; i++) {
                                    channel[i] += (Math.random() - 0.5) * 0.0001;
                                }
                            }
                        }
                        
                        return result;
                    }
                };
            }
            
            // Also protect AudioContext timing
            if (window.AudioContext || window.webkitAudioContext) {
                const AudioContextClass = window.AudioContext || window.webkitAudioContext;
                const originalCurrentTime = Object.getOwnPropertyDescriptor(
                    AudioContextClass.prototype, 
                    'currentTime'
                );
                
                if (originalCurrentTime) {
                    Object.defineProperty(AudioContextClass.prototype, 'currentTime', {
                        get: function() {
                            const time = originalCurrentTime.get.call(this);
                            // Add microsecond noise
                            return time + (Math.random() - 0.5) * 0.00001;
                        }
                    });
                }
            }
        })();
        """
        
        try:
            driver.execute_script(script)
        except Exception as e:
            logger.warning(f"Could not inject AudioWorklet protection: {e}")
    
    def generate_wasm_execution_fingerprint(self) -> Dict:
        """Generate a unique but realistic WASM execution fingerprint"""
        if not self.current_profile:
            self.select_profile()
        
        fingerprint = {
            'compile_time': random.uniform(*self.current_profile['compile_time_variance']),
            'execution_time': random.uniform(*self.current_profile['execution_time_variance']),
            'memory_pages': random.randint(1, 16),
            'table_size': random.randint(0, 10),
            'features': self.current_profile['features'].copy(),
            'gc_timing': {
                'minor': random.uniform(*self.current_profile['gc_characteristics']['minor_gc_interval']),
                'major': random.uniform(*self.current_profile['gc_characteristics']['major_gc_interval'])
            }
        }
        
        # Add some randomness to features
        if random.random() < 0.1:  # 10% chance to vary features
            feature_to_toggle = random.choice(list(fingerprint['features'].keys()))
            fingerprint['features'][feature_to_toggle] = not fingerprint['features'][feature_to_toggle]
        
        return fingerprint
    
    def set_noise_level(self, level: float):
        """Set the noise level (0.0 to 1.0)"""
        self.noise_level = max(0.0, min(1.0, level))
        logger.info(f"WASM noise level set to: {self.noise_level:.2f}")

# Singleton instance
wasm_protection = WASMProtection()
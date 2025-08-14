"""
DNS Optimization Module
Implements DNS over HTTPS (DoH) and DNS fingerprint randomization
"""

import random
import socket
import ssl
import json
import base64
import struct
from typing import Dict, List, Optional, Tuple
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class DNSOptimizer:
    """Advanced DNS optimization with DoH support and fingerprint randomization"""
    
    def __init__(self):
        self.doh_providers = [
            {
                'name': 'Cloudflare',
                'url': 'https://cloudflare-dns.com/dns-query',
                'ips': ['1.1.1.1', '1.0.0.1'],
                'headers': {'accept': 'application/dns-json'}
            },
            {
                'name': 'Google',
                'url': 'https://dns.google/resolve',
                'ips': ['8.8.8.8', '8.8.4.4'],
                'headers': {'accept': 'application/dns-json'}
            },
            {
                'name': 'Quad9',
                'url': 'https://dns.quad9.net/dns-query',
                'ips': ['9.9.9.9', '149.112.112.112'],
                'headers': {'accept': 'application/dns-json'}
            },
            {
                'name': 'NextDNS',
                'url': 'https://dns.nextdns.io/dns-query',
                'ips': ['45.90.28.0', '45.90.30.0'],
                'headers': {'accept': 'application/dns-json'}
            },
            {
                'name': 'AdGuard',
                'url': 'https://dns.adguard.com/dns-query',
                'ips': ['94.140.14.14', '94.140.15.15'],
                'headers': {'accept': 'application/dns-json'}
            }
        ]
        
        self.dns_cache = {}
        self.provider_stats = {p['name']: {'success': 0, 'failure': 0} for p in self.doh_providers}
        
        # TCP fingerprint parameters
        self.tcp_params = {
            'window_sizes': [8192, 16384, 32768, 65535, 131070, 262140],
            'ttl_values': [64, 128, 255],  # Common TTL values for different OS
            'mss_values': [536, 1200, 1440, 1460],  # Maximum Segment Size values
            'window_scale': [0, 2, 4, 6, 8, 10, 14],
            'sack_permitted': [True, False],
            'timestamps': [True, False]
        }
        
    def resolve_with_doh(self, hostname: str, record_type: str = 'A') -> Optional[List[str]]:
        """Resolve hostname using DNS over HTTPS"""
        
        # Check cache first
        cache_key = f"{hostname}:{record_type}"
        if cache_key in self.dns_cache:
            cached_result, timestamp = self.dns_cache[cache_key]
            import time
            if time.time() - timestamp < 300:  # 5 minute cache
                logger.info(f"DNS cache hit for {hostname}")
                return cached_result
        
        # Select provider based on success rates
        provider = self._select_best_provider()
        
        try:
            params = {
                'name': hostname,
                'type': record_type
            }
            
            response = requests.get(
                provider['url'],
                params=params,
                headers=provider['headers'],
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'Answer' in data:
                    ips = [answer['data'] for answer in data['Answer'] 
                           if answer.get('type') in [1, 28]]  # A or AAAA records
                    
                    # Cache the result
                    import time
                    self.dns_cache[cache_key] = (ips, time.time())
                    
                    # Update stats
                    self.provider_stats[provider['name']]['success'] += 1
                    
                    logger.info(f"DoH resolved {hostname} to {ips} via {provider['name']}")
                    return ips
            
            self.provider_stats[provider['name']]['failure'] += 1
            
        except Exception as e:
            logger.error(f"DoH resolution failed for {hostname}: {e}")
            self.provider_stats[provider['name']]['failure'] += 1
        
        # Fallback to system DNS
        return self._fallback_dns_resolve(hostname)
    
    def _select_best_provider(self) -> Dict:
        """Select DoH provider based on success rates"""
        providers_with_score = []
        
        for provider in self.doh_providers:
            stats = self.provider_stats[provider['name']]
            total = stats['success'] + stats['failure']
            
            if total == 0:
                # New provider, give it a chance
                score = 0.5
            else:
                score = stats['success'] / total
            
            providers_with_score.append((provider, score))
        
        # Sort by score but add some randomization
        providers_with_score.sort(key=lambda x: x[1] + random.random() * 0.1, reverse=True)
        
        return providers_with_score[0][0]
    
    def _fallback_dns_resolve(self, hostname: str) -> Optional[List[str]]:
        """Fallback to system DNS resolution"""
        try:
            result = socket.getaddrinfo(hostname, None)
            ips = list(set([r[4][0] for r in result]))
            logger.info(f"System DNS resolved {hostname} to {ips}")
            return ips
        except Exception as e:
            logger.error(f"System DNS resolution failed for {hostname}: {e}")
            return None
    
    def get_random_tcp_fingerprint(self) -> Dict:
        """Generate random TCP fingerprint parameters"""
        return {
            'window_size': random.choice(self.tcp_params['window_sizes']),
            'ttl': random.choice(self.tcp_params['ttl_values']),
            'mss': random.choice(self.tcp_params['mss_values']),
            'window_scale': random.choice(self.tcp_params['window_scale']),
            'sack_permitted': random.choice(self.tcp_params['sack_permitted']),
            'timestamps': random.choice(self.tcp_params['timestamps'])
        }
    
    def apply_tcp_fingerprint(self, sock: socket.socket, fingerprint: Dict):
        """Apply TCP fingerprint parameters to socket"""
        try:
            # Set TCP window size
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, fingerprint['window_size'])
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, fingerprint['window_size'])
            
            # Set IP TTL
            if hasattr(socket, 'IP_TTL'):
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, fingerprint['ttl'])
            
            # Set TCP options (platform-specific, may not work on all systems)
            if hasattr(socket, 'TCP_MAXSEG'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG, fingerprint['mss'])
            
            if hasattr(socket, 'TCP_WINDOW_CLAMP'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, fingerprint['window_size'])
            
            logger.info(f"Applied TCP fingerprint: {fingerprint}")
            
        except Exception as e:
            logger.warning(f"Could not apply all TCP fingerprint parameters: {e}")
    
    def create_custom_dns_query(self, hostname: str, query_type: int = 1) -> bytes:
        """Create a custom DNS query packet with randomized parameters"""
        # DNS header with random transaction ID
        transaction_id = random.randint(0, 65535)
        flags = 0x0100  # Standard query with recursion desired
        questions = 1
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        
        header = struct.pack('>HHHHHH', 
                            transaction_id, flags, questions, 
                            answer_rrs, authority_rrs, additional_rrs)
        
        # Encode hostname
        question = b''
        for part in hostname.split('.'):
            question += bytes([len(part)]) + part.encode()
        question += b'\x00'  # End of hostname
        
        # Query type and class
        question += struct.pack('>HH', query_type, 1)  # Type A, Class IN
        
        return header + question
    
    def randomize_dns_timing(self):
        """Add random delays to DNS queries to avoid timing fingerprinting"""
        import time
        delay = random.uniform(0.01, 0.1)  # 10-100ms random delay
        time.sleep(delay)
    
    def get_dns_over_tls(self, hostname: str, server: str = '1.1.1.1') -> Optional[List[str]]:
        """Resolve using DNS over TLS (DoT)"""
        try:
            # Create TLS context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Create socket with random TCP fingerprint
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fingerprint = self.get_random_tcp_fingerprint()
            self.apply_tcp_fingerprint(sock, fingerprint)
            
            # Wrap in TLS
            secure_sock = context.wrap_socket(sock, server_hostname=server)
            secure_sock.connect((server, 853))  # DoT port
            
            # Send DNS query
            query = self.create_custom_dns_query(hostname)
            length_prefix = struct.pack('>H', len(query))
            secure_sock.send(length_prefix + query)
            
            # Receive response
            response_length = struct.unpack('>H', secure_sock.recv(2))[0]
            response = secure_sock.recv(response_length)
            
            # Parse response (simplified)
            ips = self._parse_dns_response(response)
            
            secure_sock.close()
            return ips
            
        except Exception as e:
            logger.error(f"DoT resolution failed: {e}")
            return None
    
    def _parse_dns_response(self, response: bytes) -> List[str]:
        """Parse DNS response packet (simplified)"""
        ips = []
        # Skip header (12 bytes) and question section
        offset = 12
        
        # Skip question section (simplified - assumes one question)
        while offset < len(response) and response[offset] != 0:
            offset += 1
        offset += 5  # Skip null terminator and type/class
        
        # Parse answers (simplified - assumes A records)
        try:
            while offset < len(response) - 4:
                # Skip name pointer
                if response[offset] & 0xC0 == 0xC0:
                    offset += 2
                else:
                    while offset < len(response) and response[offset] != 0:
                        offset += response[offset] + 1
                    offset += 1
                
                # Check if we have enough data
                if offset + 10 > len(response):
                    break
                
                # Read type, class, TTL, and length
                rtype = struct.unpack('>H', response[offset:offset+2])[0]
                offset += 8  # Skip type, class, and TTL
                rdlength = struct.unpack('>H', response[offset:offset+2])[0]
                offset += 2
                
                # If it's an A record, extract IP
                if rtype == 1 and rdlength == 4:
                    ip = '.'.join(str(b) for b in response[offset:offset+4])
                    ips.append(ip)
                
                offset += rdlength
                
        except Exception as e:
            logger.warning(f"Error parsing DNS response: {e}")
        
        return ips
    
    def clear_cache(self):
        """Clear DNS cache"""
        self.dns_cache.clear()
        logger.info("DNS cache cleared")
    
    def get_stats(self) -> Dict:
        """Get provider statistics"""
        return self.provider_stats

# Singleton instance
dns_optimizer = DNSOptimizer()
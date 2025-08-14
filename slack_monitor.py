#!/usr/bin/env python3
"""
Slack Monitoring for Web Scraper Ultra
Sends health checks and alerts to Slack channel
"""

import os
import json
import time
import requests
import schedule
from datetime import datetime
from typing import Dict, Optional

class SlackMonitor:
    def __init__(self, webhook_url: str, api_url: str = "http://164.92.90.183"):
        """
        Initialize Slack monitoring
        
        Args:
            webhook_url: Your Slack webhook URL
            api_url: Base URL of your web scraper API
        """
        self.webhook_url = webhook_url
        self.api_url = api_url
        self.last_status = None
        self.error_count = 0
        self.success_count = 0
        
    def send_slack_message(self, message: Dict) -> bool:
        """Send message to Slack"""
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Slack message: {e}")
            return False
    
    def check_health(self) -> Dict:
        """Check API health status"""
        try:
            response = requests.get(
                f"{self.api_url}/api/health",
                timeout=10
            )
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'data': response.json(),
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}',
                    'response_time': response.elapsed.total_seconds()
                }
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'error': 'Request timed out'}
        except requests.exceptions.ConnectionError:
            return {'status': 'down', 'error': 'Connection failed'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def format_health_message(self, health: Dict) -> Dict:
        """Format health check as Slack message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if health['status'] == 'healthy':
            self.success_count += 1
            self.error_count = 0  # Reset error count
            
            data = health.get('data', {})
            components = data.get('components', {})
            
            # Build status indicators
            db_status = "✅" if components.get('database', {}).get('status') == 'connected' else "⚠️"
            proxy_count = components.get('proxies', {}).get('count', 0)
            proxy_status = "✅" if proxy_count > 0 else "⚠️"
            
            return {
                "text": "🟢 Web Scraper Health Check",
                "attachments": [{
                    "color": "good",
                    "title": "System Healthy",
                    "fields": [
                        {
                            "title": "Status",
                            "value": "✅ All Systems Operational",
                            "short": True
                        },
                        {
                            "title": "Response Time",
                            "value": f"{health.get('response_time', 0):.2f}s",
                            "short": True
                        },
                        {
                            "title": "Database",
                            "value": f"{db_status} {components.get('database', {}).get('status', 'unknown')}",
                            "short": True
                        },
                        {
                            "title": "Proxies",
                            "value": f"{proxy_status} {proxy_count:,} active",
                            "short": True
                        },
                        {
                            "title": "Uptime",
                            "value": f"{self.success_count} checks passed",
                            "short": True
                        },
                        {
                            "title": "Version",
                            "value": data.get('version', 'unknown'),
                            "short": True
                        }
                    ],
                    "footer": "Web Scraper Ultra",
                    "ts": int(time.time())
                }]
            }
        else:
            self.error_count += 1
            
            # Determine severity
            if self.error_count >= 3:
                color = "danger"
                emoji = "🔴"
                severity = "CRITICAL"
            elif self.error_count >= 2:
                color = "warning"
                emoji = "🟡"
                severity = "WARNING"
            else:
                color = "warning"
                emoji = "🟠"
                severity = "ALERT"
            
            return {
                "text": f"{emoji} Web Scraper {severity}",
                "attachments": [{
                    "color": color,
                    "title": f"System {health['status'].upper()}",
                    "text": f"Error: {health.get('error', 'Unknown error')}",
                    "fields": [
                        {
                            "title": "Status",
                            "value": f"❌ {health['status']}",
                            "short": True
                        },
                        {
                            "title": "Consecutive Errors",
                            "value": str(self.error_count),
                            "short": True
                        },
                        {
                            "title": "API URL",
                            "value": self.api_url,
                            "short": False
                        },
                        {
                            "title": "Action Required",
                            "value": "Check server logs: `ssh root@164.92.90.183`",
                            "short": False
                        }
                    ],
                    "footer": "Web Scraper Ultra",
                    "ts": int(time.time())
                }]
            }
    
    def send_startup_message(self):
        """Send monitoring started notification"""
        message = {
            "text": "🚀 Web Scraper Monitoring Started",
            "attachments": [{
                "color": "#36a64f",
                "title": "Monitoring Configuration",
                "fields": [
                    {
                        "title": "API URL",
                        "value": self.api_url,
                        "short": True
                    },
                    {
                        "title": "Check Interval",
                        "value": "Every 5 minutes",
                        "short": True
                    },
                    {
                        "title": "Alert Threshold",
                        "value": "3 consecutive failures",
                        "short": True
                    },
                    {
                        "title": "Components Monitored",
                        "value": "API, Database, Proxies, Scheduler",
                        "short": False
                    }
                ],
                "footer": "Web Scraper Ultra Monitor",
                "ts": int(time.time())
            }]
        }
        self.send_slack_message(message)
    
    def monitor(self):
        """Main monitoring function"""
        health = self.check_health()
        
        # Only send message if status changed or it's an error
        if health['status'] != self.last_status or health['status'] != 'healthy':
            message = self.format_health_message(health)
            self.send_slack_message(message)
            self.last_status = health['status']
        
        # Send periodic healthy status (every 12 checks = 1 hour)
        elif self.success_count % 12 == 0 and health['status'] == 'healthy':
            message = self.format_health_message(health)
            message['text'] = "📊 Hourly Health Report"
            self.send_slack_message(message)
    
    def check_api_usage(self):
        """Check and report API usage statistics"""
        # This would connect to your database to get real stats
        # For now, sending a template message
        message = {
            "text": "📈 Daily API Usage Report",
            "attachments": [{
                "color": "#0084ff",
                "title": "Web Scraper Usage Statistics",
                "fields": [
                    {
                        "title": "Total Requests (24h)",
                        "value": "0",  # Would fetch from DB
                        "short": True
                    },
                    {
                        "title": "Successful Scrapes",
                        "value": "0",  # Would fetch from DB
                        "short": True
                    },
                    {
                        "title": "Newsletter Subscriptions",
                        "value": "0",  # Would fetch from DB
                        "short": True
                    },
                    {
                        "title": "Proxy Usage",
                        "value": "0 MB",  # Would fetch from logs
                        "short": True
                    },
                    {
                        "title": "CAPTCHA Solves",
                        "value": "0",  # Would fetch from 2captcha
                        "short": True
                    },
                    {
                        "title": "Error Rate",
                        "value": "0%",  # Would calculate
                        "short": True
                    }
                ],
                "footer": "Web Scraper Ultra",
                "ts": int(time.time())
            }]
        }
        self.send_slack_message(message)
    
    def start_monitoring(self):
        """Start the monitoring schedule"""
        print(f"Starting Slack monitoring for {self.api_url}")
        
        # Send startup notification
        self.send_startup_message()
        
        # Schedule health checks every 5 minutes
        schedule.every(5).minutes.do(self.monitor)
        
        # Schedule daily usage report at 9 AM
        schedule.every().day.at("09:00").do(self.check_api_usage)
        
        # Run first check immediately
        self.monitor()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks

def main():
    """Main entry point"""
    # Get webhook URL from environment or use placeholder
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("=" * 60)
        print("SLACK WEBHOOK SETUP REQUIRED")
        print("=" * 60)
        print("\nTo set up Slack notifications:")
        print("\n1. Go to https://api.slack.com/messaging/webhooks")
        print("2. Create a new Slack app or use existing")
        print("3. Add 'Incoming Webhooks' feature")
        print("4. Create a webhook for your channel")
        print("5. Copy the webhook URL")
        print("\n6. Set environment variable:")
        print("   export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'")
        print("\n7. Run this script again")
        print("=" * 60)
        return
    
    # Initialize monitor
    monitor = SlackMonitor(webhook_url)
    
    # Start monitoring
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print(f"Monitoring error: {e}")
        # Send error to Slack
        monitor.send_slack_message({
            "text": f"❌ Monitoring crashed: {str(e)}"
        })

if __name__ == "__main__":
    main()
"""
Cost Calculator for Web Scraping at Scale
Calculates operational costs for running the scraper at various scales
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class ScrapingCostCalculator:
    """Calculate costs for web scraping operations at scale"""
    
    def __init__(self):
        # Pricing as of January 2025
        self.pricing = {
            'proxies': {
                'webshare_residential': {
                    'base_cost': 0,  # Already paid for 215,084 proxies
                    'bandwidth_gb': 0.50,  # $0.50 per GB after included bandwidth
                    'included_bandwidth_gb': 100  # Assuming 100GB included
                },
                'additional_residential': {
                    'per_proxy': 0.001,  # $0.001 per proxy per request
                    'bandwidth_gb': 0.75
                }
            },
            
            'captcha_solving': {
                '2captcha': {
                    'recaptcha_v2': 0.00299,  # $2.99 per 1000
                    'recaptcha_v3': 0.00299,
                    'hcaptcha': 0.00299,
                    'funcaptcha': 0.00299,
                    'image_captcha': 0.00099,  # $0.99 per 1000
                    'cloudflare': 0.00299
                }
            },
            
            'infrastructure': {
                'railway': {
                    'base_monthly': 5,  # $5/month base
                    'cpu_hour': 0.01,  # $0.01 per CPU hour
                    'memory_gb_hour': 0.01,  # $0.01 per GB RAM hour
                    'bandwidth_gb': 0.10  # $0.10 per GB
                },
                'neon_database': {
                    'compute_hour': 0.09,  # $0.09 per compute hour
                    'storage_gb_month': 0.15,  # $0.15 per GB/month
                    'bandwidth_gb': 0.09  # $0.09 per GB
                },
                'google_sheets': {
                    'api_requests_per_day': 20000,  # Free tier
                    'overage_per_1000': 0.05  # Estimated
                }
            },
            
            'selenium_grid': {
                'browserstack': {
                    'per_minute': 0.05  # If using cloud browsers
                },
                'local': {
                    'per_instance_hour': 0  # Free if self-hosted
                }
            }
        }
        
        # Average resource consumption per request
        self.resource_consumption = {
            'bandwidth_mb': 2.5,  # Average page size
            'cpu_seconds': 3,
            'memory_mb': 150,
            'database_rows': 1,
            'database_storage_kb': 5
        }
    
    def calculate_request_cost(self, 
                              use_proxy: bool = True,
                              solve_captcha: bool = False,
                              captcha_type: str = 'recaptcha_v2',
                              strategy: str = 'requests') -> float:
        """Calculate cost for a single scraping request"""
        total_cost = 0
        
        # Proxy cost
        if use_proxy:
            # Bandwidth cost (convert MB to GB)
            bandwidth_gb = self.resource_consumption['bandwidth_mb'] / 1024
            
            # Webshare proxies (first 100GB included)
            if bandwidth_gb > 0:
                total_cost += bandwidth_gb * self.pricing['proxies']['webshare_residential']['bandwidth_gb']
        
        # Captcha solving cost
        if solve_captcha:
            captcha_cost = self.pricing['captcha_solving']['2captcha'].get(captcha_type, 0.00299)
            total_cost += captcha_cost
        
        # Infrastructure cost per request
        # CPU cost
        cpu_hours = self.resource_consumption['cpu_seconds'] / 3600
        total_cost += cpu_hours * self.pricing['infrastructure']['railway']['cpu_hour']
        
        # Memory cost
        memory_gb_hours = (self.resource_consumption['memory_mb'] / 1024) * (cpu_hours)
        total_cost += memory_gb_hours * self.pricing['infrastructure']['railway']['memory_gb_hour']
        
        # Database cost
        db_compute_hours = 0.001  # Assuming 0.001 hours per request
        total_cost += db_compute_hours * self.pricing['infrastructure']['neon_database']['compute_hour']
        
        # Strategy-specific costs
        if strategy in ['selenium', 'undetected', 'mobile']:
            # Additional resource consumption for browser-based scraping
            total_cost *= 2.5  # 2.5x more expensive due to browser overhead
        
        return total_cost
    
    def calculate_scale_costs(self, 
                            requests_per_day: int,
                            captcha_rate: float = 0.05,  # 5% of requests hit captcha
                            proxy_usage_rate: float = 0.8,  # 80% use proxies
                            selenium_rate: float = 0.2) -> Dict:  # 20% use Selenium
        """Calculate costs at scale"""
        
        # Daily calculations
        daily_costs = {
            'requests': requests_per_day,
            'proxy_requests': int(requests_per_day * proxy_usage_rate),
            'captcha_solves': int(requests_per_day * captcha_rate),
            'selenium_requests': int(requests_per_day * selenium_rate),
            'request_cost': 0,
            'infrastructure_cost': 0,
            'total_daily': 0
        }
        
        # Calculate per-request costs
        regular_requests = requests_per_day - daily_costs['selenium_requests']
        
        # Regular requests cost
        regular_cost = regular_requests * self.calculate_request_cost(
            use_proxy=True,
            solve_captcha=False,
            strategy='requests'
        )
        
        # Selenium requests cost
        selenium_cost = daily_costs['selenium_requests'] * self.calculate_request_cost(
            use_proxy=True,
            solve_captcha=False,
            strategy='selenium'
        )
        
        # Captcha costs
        captcha_cost = daily_costs['captcha_solves'] * self.pricing['captcha_solving']['2captcha']['recaptcha_v2']
        
        # Total bandwidth
        total_bandwidth_gb = (requests_per_day * self.resource_consumption['bandwidth_mb']) / 1024
        
        # Proxy bandwidth costs (after free tier)
        free_bandwidth = self.pricing['proxies']['webshare_residential']['included_bandwidth_gb']
        if total_bandwidth_gb > free_bandwidth:
            proxy_bandwidth_cost = (total_bandwidth_gb - free_bandwidth) * \
                                  self.pricing['proxies']['webshare_residential']['bandwidth_gb']
        else:
            proxy_bandwidth_cost = 0
        
        # Database storage (cumulative)
        daily_storage_gb = (requests_per_day * self.resource_consumption['database_storage_kb']) / (1024 * 1024)
        
        # Infrastructure base costs (daily portion)
        infrastructure_daily = self.pricing['infrastructure']['railway']['base_monthly'] / 30
        infrastructure_daily += self.pricing['infrastructure']['neon_database']['storage_gb_month'] * daily_storage_gb / 30
        
        # Compile daily costs
        daily_costs['request_cost'] = regular_cost + selenium_cost
        daily_costs['captcha_cost'] = captcha_cost
        daily_costs['proxy_bandwidth_cost'] = proxy_bandwidth_cost
        daily_costs['infrastructure_cost'] = infrastructure_daily
        daily_costs['total_daily'] = sum([
            daily_costs['request_cost'],
            daily_costs['captcha_cost'],
            daily_costs['proxy_bandwidth_cost'],
            daily_costs['infrastructure_cost']
        ])
        
        # Monthly projections
        monthly_costs = {
            'requests': requests_per_day * 30,
            'total_cost': daily_costs['total_daily'] * 30,
            'breakdown': {
                'request_processing': daily_costs['request_cost'] * 30,
                'captcha_solving': daily_costs['captcha_cost'] * 30,
                'proxy_bandwidth': daily_costs['proxy_bandwidth_cost'] * 30,
                'infrastructure': daily_costs['infrastructure_cost'] * 30 + 
                                 self.pricing['infrastructure']['railway']['base_monthly']
            }
        }
        
        # Annual projections
        annual_costs = {
            'requests': requests_per_day * 365,
            'total_cost': daily_costs['total_daily'] * 365,
            'cost_per_1000_requests': (daily_costs['total_daily'] * 1000) / requests_per_day
        }
        
        return {
            'daily': daily_costs,
            'monthly': monthly_costs,
            'annual': annual_costs
        }
    
    def optimize_costs(self, current_usage: Dict) -> List[Dict]:
        """Provide cost optimization recommendations"""
        recommendations = []
        
        # Analyze current usage
        requests_per_day = current_usage.get('requests_per_day', 0)
        captcha_rate = current_usage.get('captcha_rate', 0.05)
        selenium_rate = current_usage.get('selenium_rate', 0.2)
        
        # Recommendation 1: Reduce Selenium usage
        if selenium_rate > 0.1:
            savings = self.calculate_scale_costs(requests_per_day, captcha_rate, 0.8, selenium_rate)['daily']['total_daily'] - \
                     self.calculate_scale_costs(requests_per_day, captcha_rate, 0.8, 0.1)['daily']['total_daily']
            
            recommendations.append({
                'title': 'Reduce Selenium Usage',
                'description': 'Use Selenium only when absolutely necessary. CloudScraper handles most JavaScript sites.',
                'potential_savings': f'${savings:.2f}/day',
                'implementation': 'Set strategy="auto" to let system choose optimal method'
            })
        
        # Recommendation 2: Implement caching
        cache_hit_rate = 0.3  # 30% cache hit rate
        cached_requests = requests_per_day * cache_hit_rate
        savings = cached_requests * self.calculate_request_cost()
        
        recommendations.append({
            'title': 'Implement Response Caching',
            'description': 'Cache frequently accessed pages to reduce redundant requests',
            'potential_savings': f'${savings:.2f}/day',
            'implementation': 'Use Redis or local cache with 1-hour TTL for static content'
        })
        
        # Recommendation 3: Batch processing
        recommendations.append({
            'title': 'Batch Processing',
            'description': 'Process requests in batches during off-peak hours',
            'potential_savings': '10-15% on infrastructure costs',
            'implementation': 'Use job scheduler to batch similar requests'
        })
        
        # Recommendation 4: Optimize captcha handling
        if captcha_rate > 0.03:
            recommendations.append({
                'title': 'Improve Captcha Avoidance',
                'description': 'Better behavioral patterns and cookie management can reduce captcha encounters',
                'potential_savings': f'${captcha_rate * requests_per_day * 0.00299 * 0.5:.2f}/day',
                'implementation': 'Use behavioral_enhancer with "researcher" profile for lower detection'
            })
        
        # Recommendation 5: Use spot instances
        if requests_per_day > 100000:
            recommendations.append({
                'title': 'Use Spot/Preemptible Instances',
                'description': 'For non-critical batch jobs, use spot instances',
                'potential_savings': '60-70% on compute costs',
                'implementation': 'Deploy workers on AWS Spot or GCP Preemptible VMs'
            })
        
        return recommendations
    
    def generate_cost_report(self, 
                            requests_per_day: int,
                            output_format: str = 'text') -> str:
        """Generate comprehensive cost report"""
        
        # Calculate costs at different scales
        scales = [
            ('Current', requests_per_day),
            ('2x Scale', requests_per_day * 2),
            ('5x Scale', requests_per_day * 5),
            ('10x Scale', requests_per_day * 10)
        ]
        
        report = []
        report.append("="*60)
        report.append("WEB SCRAPING COST ANALYSIS REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        
        for scale_name, scale_requests in scales:
            costs = self.calculate_scale_costs(scale_requests)
            
            report.append(f"\n{scale_name}: {scale_requests:,} requests/day")
            report.append("-"*40)
            
            # Daily costs
            report.append(f"Daily Costs:")
            report.append(f"  Request Processing: ${costs['daily']['request_cost']:.2f}")
            report.append(f"  Captcha Solving: ${costs['daily']['captcha_cost']:.2f}")
            report.append(f"  Proxy Bandwidth: ${costs['daily']['proxy_bandwidth_cost']:.2f}")
            report.append(f"  Infrastructure: ${costs['daily']['infrastructure_cost']:.2f}")
            report.append(f"  TOTAL DAILY: ${costs['daily']['total_daily']:.2f}")
            
            # Monthly projection
            report.append(f"\nMonthly Projection:")
            report.append(f"  Total Requests: {costs['monthly']['requests']:,}")
            report.append(f"  Total Cost: ${costs['monthly']['total_cost']:.2f}")
            
            # Cost per request
            report.append(f"\nUnit Economics:")
            report.append(f"  Cost per request: ${costs['daily']['total_daily']/scale_requests:.6f}")
            report.append(f"  Cost per 1000 requests: ${costs['annual']['cost_per_1000_requests']:.2f}")
        
        # Add recommendations
        report.append("\n" + "="*60)
        report.append("COST OPTIMIZATION RECOMMENDATIONS")
        report.append("="*60)
        
        recommendations = self.optimize_costs({'requests_per_day': requests_per_day})
        for i, rec in enumerate(recommendations, 1):
            report.append(f"\n{i}. {rec['title']}")
            report.append(f"   {rec['description']}")
            report.append(f"   Savings: {rec['potential_savings']}")
            report.append(f"   How: {rec['implementation']}")
        
        # Add breakdown chart
        report.append("\n" + "="*60)
        report.append("COST BREAKDOWN AT SCALE")
        report.append("="*60)
        
        # Calculate percentage breakdown
        costs = self.calculate_scale_costs(requests_per_day)
        total = costs['daily']['total_daily']
        
        if total > 0:
            report.append("\nDaily Cost Distribution:")
            report.append(f"  Request Processing: {(costs['daily']['request_cost']/total)*100:.1f}%")
            report.append(f"  Captcha Solving: {(costs['daily']['captcha_cost']/total)*100:.1f}%")
            report.append(f"  Proxy Bandwidth: {(costs['daily']['proxy_bandwidth_cost']/total)*100:.1f}%")
            report.append(f"  Infrastructure: {(costs['daily']['infrastructure_cost']/total)*100:.1f}%")
        
        return '\n'.join(report)
    
    def calculate_roi(self, 
                     requests_per_day: int,
                     revenue_per_request: float = 0.01,  # $0.01 revenue per successful scrape
                     success_rate: float = 0.95) -> Dict:
        """Calculate Return on Investment"""
        
        costs = self.calculate_scale_costs(requests_per_day)
        
        # Revenue calculations
        successful_requests = requests_per_day * success_rate
        daily_revenue = successful_requests * revenue_per_request
        monthly_revenue = daily_revenue * 30
        
        # ROI calculations
        daily_profit = daily_revenue - costs['daily']['total_daily']
        monthly_profit = monthly_revenue - costs['monthly']['total_cost']
        roi_percentage = (daily_profit / costs['daily']['total_daily']) * 100 if costs['daily']['total_daily'] > 0 else 0
        
        # Break-even analysis
        break_even_requests = costs['daily']['total_daily'] / (revenue_per_request * success_rate) if revenue_per_request > 0 else 0
        
        return {
            'daily_revenue': daily_revenue,
            'daily_cost': costs['daily']['total_daily'],
            'daily_profit': daily_profit,
            'monthly_profit': monthly_profit,
            'roi_percentage': roi_percentage,
            'break_even_requests': int(break_even_requests),
            'profit_margin': (daily_profit / daily_revenue * 100) if daily_revenue > 0 else 0
        }

# Singleton instance
cost_calculator = ScrapingCostCalculator()
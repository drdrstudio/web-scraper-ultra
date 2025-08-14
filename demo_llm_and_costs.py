#!/usr/bin/env python3
"""
Demonstration of LLM-Friendly Output and Cost Analysis
Shows how to use the scraper for AI applications with cost optimization
"""

import json
from advanced_scraper_ultra import ultra_scraper
from llm_formatter import llm_formatter
from cost_calculator import cost_calculator

def demo_llm_formats():
    """Demonstrate different LLM-friendly output formats"""
    print("\n" + "="*60)
    print("LLM-FRIENDLY OUTPUT FORMATS DEMONSTRATION")
    print("="*60)
    
    # Test URL (using httpbin for consistent results)
    test_url = "https://en.wikipedia.org/wiki/Web_scraping"
    
    # Available LLM formats
    formats = [
        ('clean_text', 'Clean readable text for general LLM processing'),
        ('structured_qa', 'Q&A format for training conversational models'),
        ('markdown', 'Structured markdown for documentation'),
        ('conversation', 'Dialog format for chat training'),
        ('summary', 'Executive summary with key points'),
        ('narrative', 'Natural language description')
    ]
    
    print(f"\nScraping: {test_url}")
    print("Testing different LLM output formats...\n")
    
    for format_type, description in formats:
        print(f"\n{'='*50}")
        print(f"Format: {format_type.upper()}")
        print(f"Description: {description}")
        print("="*50)
        
        # Scrape with the specific format
        result = ultra_scraper.scrape(
            url=test_url,
            strategy='requests',  # Fast strategy for demo
            use_proxy=False,  # No proxy for demo
            output_format=format_type
        )
        
        if isinstance(result, str):
            # Show first 500 characters of formatted output
            print(result[:500])
            if len(result) > 500:
                print("\n... [truncated for demo]")
        else:
            print(f"Error: {result.get('error', 'Failed to scrape')}")
        
        print("\n" + "-"*50)

def demo_cost_analysis():
    """Demonstrate cost calculations at different scales"""
    print("\n" + "="*60)
    print("COST ANALYSIS FOR SCALING")
    print("="*60)
    
    # Different scaling scenarios
    scenarios = [
        ('Small Scale', 1000, 'Personal project or testing'),
        ('Medium Scale', 10000, 'Small business monitoring'),
        ('Large Scale', 100000, 'Enterprise data collection'),
        ('Massive Scale', 1000000, 'Big data analytics')
    ]
    
    print("\nCost Analysis for Different Scales:")
    print("-"*50)
    
    for scale_name, requests_per_day, use_case in scenarios:
        print(f"\n📊 {scale_name}: {requests_per_day:,} requests/day")
        print(f"   Use Case: {use_case}")
        
        # Calculate costs
        costs = cost_calculator.calculate_scale_costs(
            requests_per_day=requests_per_day,
            captcha_rate=0.05,  # 5% captcha rate
            proxy_usage_rate=0.8,  # 80% use proxies
            selenium_rate=0.2  # 20% need browser
        )
        
        # Display results
        print(f"\n   Daily Costs:")
        print(f"     Processing: ${costs['daily']['request_cost']:.2f}")
        print(f"     Captchas: ${costs['daily']['captcha_cost']:.2f}")
        print(f"     Bandwidth: ${costs['daily']['proxy_bandwidth_cost']:.2f}")
        print(f"     Infrastructure: ${costs['daily']['infrastructure_cost']:.2f}")
        print(f"     TOTAL: ${costs['daily']['total_daily']:.2f}")
        
        print(f"\n   Monthly Projection:")
        print(f"     Total Cost: ${costs['monthly']['total_cost']:.2f}")
        print(f"     Per 1000 requests: ${costs['annual']['cost_per_1000_requests']:.2f}")
        
        # ROI calculation (assuming $0.01 revenue per request)
        roi = cost_calculator.calculate_roi(
            requests_per_day=requests_per_day,
            revenue_per_request=0.01,
            success_rate=0.95
        )
        
        print(f"\n   ROI Analysis (at $0.01/request):")
        print(f"     Daily Revenue: ${roi['daily_revenue']:.2f}")
        print(f"     Daily Profit: ${roi['daily_profit']:.2f}")
        print(f"     Profit Margin: {roi['profit_margin']:.1f}%")
        print(f"     ROI: {roi['roi_percentage']:.1f}%")

def demo_optimization_recommendations():
    """Show cost optimization recommendations"""
    print("\n" + "="*60)
    print("COST OPTIMIZATION RECOMMENDATIONS")
    print("="*60)
    
    # Current usage scenario
    current_usage = {
        'requests_per_day': 50000,
        'captcha_rate': 0.08,  # 8% hit captchas
        'selenium_rate': 0.3,  # 30% use Selenium
        'proxy_usage_rate': 0.9  # 90% use proxies
    }
    
    print(f"\nCurrent Usage Pattern:")
    print(f"  Requests/day: {current_usage['requests_per_day']:,}")
    print(f"  Captcha rate: {current_usage['captcha_rate']*100:.1f}%")
    print(f"  Selenium usage: {current_usage['selenium_rate']*100:.1f}%")
    print(f"  Proxy usage: {current_usage['proxy_usage_rate']*100:.1f}%")
    
    # Get recommendations
    recommendations = cost_calculator.optimize_costs(current_usage)
    
    print("\n📈 Optimization Opportunities:")
    print("-"*50)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   {rec['description']}")
        print(f"   💰 Potential Savings: {rec['potential_savings']}")
        print(f"   🔧 Implementation: {rec['implementation']}")

def demo_llm_task_optimization():
    """Show optimal formats for different LLM tasks"""
    print("\n" + "="*60)
    print("OPTIMAL FORMATS FOR LLM TASKS")
    print("="*60)
    
    tasks = [
        ('summarization', 'Creating concise summaries of web content'),
        ('qa_training', 'Training Q&A models on scraped data'),
        ('content_analysis', 'Analyzing and categorizing content'),
        ('information_extraction', 'Extracting structured data'),
        ('conversation_training', 'Training chatbots and assistants'),
        ('text_generation', 'Training text generation models'),
        ('classification', 'Training classification models')
    ]
    
    print("\nRecommended formats for different AI/LLM tasks:")
    print("-"*50)
    
    for task, description in tasks:
        optimal_format = llm_formatter.optimal_format_for_task(task)
        print(f"\n📋 Task: {task}")
        print(f"   Description: {description}")
        print(f"   ✅ Optimal Format: {optimal_format}")
        
        # Show example usage
        print(f"   Usage:")
        print(f"     result = ultra_scraper.scrape(")
        print(f"         url='https://example.com',")
        print(f"         output_format='{optimal_format}'")
        print(f"     )")

def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print(" LLM-FRIENDLY WEB SCRAPING & COST ANALYSIS")
    print(" Advanced Features Demonstration")
    print("="*70)
    
    # Run demos
    demos = [
        ("LLM Output Formats", demo_llm_formats),
        ("Cost Analysis", demo_cost_analysis),
        ("Optimization Tips", demo_optimization_recommendations),
        ("LLM Task Optimization", demo_llm_task_optimization)
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*70}")
            print(f"Running: {demo_name}")
            print('='*70)
            demo_func()
        except Exception as e:
            print(f"Error in {demo_name}: {e}")
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print("""
KEY TAKEAWAYS:

1. LLM-FRIENDLY OUTPUTS:
   - 7 specialized formats for different AI tasks
   - Clean, structured data ready for model training
   - Automatic metadata inclusion for context

2. COST AT SCALE:
   - Small (1K/day): ~$0.05-0.10/day
   - Medium (10K/day): ~$0.50-1.00/day
   - Large (100K/day): ~$5-10/day
   - Massive (1M/day): ~$50-100/day

3. COST OPTIMIZATION:
   - Reduce Selenium usage by 50%: Save 40% on costs
   - Implement caching: Save 30% on redundant requests
   - Better behavioral patterns: Reduce captchas by 60%
   - Use spot instances: Save 70% on compute

4. ROI CONSIDERATIONS:
   - Break-even at ~$0.001 per request
   - Profitable at >$0.01 per request
   - Most commercial use cases: $0.05-0.50 per request value

5. BEST PRACTICES:
   - Use 'clean_text' for general LLM processing
   - Use 'structured_qa' for training Q&A models
   - Use 'summary' for quick insights
   - Monitor costs daily and optimize continuously
    """)

if __name__ == "__main__":
    main()
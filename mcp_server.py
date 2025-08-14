#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Web Scraper
Provides a simple interface for AI assistants to use the web scraper
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_scraper_ultra import ultra_scraper
from llm_formatter import llm_formatter
from cost_calculator import cost_calculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPWebScraperServer:
    """MCP Server for Web Scraping with LLM-friendly output"""
    
    def __init__(self):
        self.name = "web-scraper"
        self.version = "1.0.0"
        self.description = "Advanced web scraper with anti-bot detection and LLM-friendly output"
        
        # Available tools for MCP
        self.tools = {
            "scrape_webpage": {
                "description": "Scrape any webpage and get LLM-friendly content",
                "parameters": {
                    "url": {
                        "type": "string",
                        "required": True,
                        "description": "The URL to scrape"
                    },
                    "format": {
                        "type": "string",
                        "required": False,
                        "default": "clean_text",
                        "description": "Output format: clean_text, summary, markdown, conversation, structured_qa, narrative"
                    },
                    "use_stealth": {
                        "type": "boolean",
                        "required": False,
                        "default": True,
                        "description": "Use anti-detection features"
                    }
                }
            },
            "scrape_multiple": {
                "description": "Scrape multiple URLs efficiently",
                "parameters": {
                    "urls": {
                        "type": "array",
                        "required": True,
                        "description": "List of URLs to scrape"
                    },
                    "format": {
                        "type": "string",
                        "required": False,
                        "default": "summary",
                        "description": "Output format for all pages"
                    }
                }
            },
            "extract_data": {
                "description": "Extract specific data from a webpage",
                "parameters": {
                    "url": {
                        "type": "string",
                        "required": True,
                        "description": "The URL to extract data from"
                    },
                    "data_type": {
                        "type": "string",
                        "required": True,
                        "description": "Type of data: emails, phone_numbers, prices, dates, links, images"
                    }
                }
            },
            "monitor_website": {
                "description": "Monitor a website for changes",
                "parameters": {
                    "url": {
                        "type": "string",
                        "required": True,
                        "description": "URL to monitor"
                    },
                    "check_interval": {
                        "type": "integer",
                        "required": False,
                        "default": 3600,
                        "description": "Check interval in seconds"
                    }
                }
            },
            "analyze_website": {
                "description": "Analyze a website's structure and content",
                "parameters": {
                    "url": {
                        "type": "string",
                        "required": True,
                        "description": "Website to analyze"
                    }
                }
            },
            "estimate_cost": {
                "description": "Estimate scraping costs for a given scale",
                "parameters": {
                    "requests_per_day": {
                        "type": "integer",
                        "required": True,
                        "description": "Number of pages to scrape per day"
                    }
                }
            }
        }
        
        # Track usage for cost estimation
        self.usage_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes': 0
        }
    
    async def handle_tool_call(self, tool_name: str, parameters: Dict) -> Dict:
        """Handle MCP tool calls"""
        
        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            if tool_name == "scrape_webpage":
                return await self.scrape_webpage(**parameters)
            elif tool_name == "scrape_multiple":
                return await self.scrape_multiple(**parameters)
            elif tool_name == "extract_data":
                return await self.extract_data(**parameters)
            elif tool_name == "monitor_website":
                return await self.monitor_website(**parameters)
            elif tool_name == "analyze_website":
                return await self.analyze_website(**parameters)
            elif tool_name == "estimate_cost":
                return await self.estimate_cost(**parameters)
            else:
                return {"error": f"Tool {tool_name} not implemented"}
                
        except Exception as e:
            logger.error(f"Error in {tool_name}: {e}")
            return {"error": str(e)}
    
    async def scrape_webpage(self, url: str, format: str = "clean_text", 
                            use_stealth: bool = True) -> Dict:
        """Scrape a single webpage with LLM-friendly output"""
        
        self.usage_stats['total_requests'] += 1
        
        # Configure scraping options
        options = {
            'strategy': 'auto' if use_stealth else 'requests',
            'use_proxy': use_stealth,
            'solve_captcha': use_stealth,
            'output_format': format,
            'profile': 'casual_browser'
        }
        
        # Perform scraping
        result = ultra_scraper.scrape(url, **options)
        
        # Track stats
        if isinstance(result, dict) and result.get('success'):
            self.usage_stats['successful_requests'] += 1
        else:
            self.usage_stats['failed_requests'] += 1
        
        # Format response for MCP
        if isinstance(result, str):
            # LLM-friendly text output
            return {
                "success": True,
                "content": result,
                "format": format,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        elif isinstance(result, dict):
            if result.get('success'):
                return {
                    "success": True,
                    "content": result.get('content', result),
                    "format": format,
                    "url": url,
                    "metadata": {
                        "strategy": result.get('strategy'),
                        "timestamp": datetime.now().isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Scraping failed'),
                    "url": url
                }
        else:
            return {
                "success": False,
                "error": "Unexpected result format",
                "url": url
            }
    
    async def scrape_multiple(self, urls: List[str], format: str = "summary") -> Dict:
        """Scrape multiple URLs efficiently"""
        
        results = []
        
        for url in urls:
            # Add small delay between requests
            await asyncio.sleep(1)
            
            result = await self.scrape_webpage(url, format=format)
            results.append({
                "url": url,
                "success": result.get("success"),
                "content": result.get("content") if result.get("success") else None,
                "error": result.get("error") if not result.get("success") else None
            })
        
        # Summary statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return {
            "success": True,
            "total_urls": len(urls),
            "successful": successful,
            "failed": failed,
            "results": results,
            "format": format
        }
    
    async def extract_data(self, url: str, data_type: str) -> Dict:
        """Extract specific data types from a webpage"""
        
        import re
        from bs4 import BeautifulSoup
        
        # First scrape the page
        result = ultra_scraper.scrape(url, output_format='html')
        
        if not isinstance(result, str):
            return {"success": False, "error": "Failed to scrape page"}
        
        soup = BeautifulSoup(result, 'html.parser')
        extracted_data = []
        
        if data_type == "emails":
            # Extract email addresses
            text = soup.get_text()
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            extracted_data = list(set(emails))
            
        elif data_type == "phone_numbers":
            # Extract phone numbers
            text = soup.get_text()
            phones = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
            extracted_data = list(set(phones))
            
        elif data_type == "prices":
            # Extract prices
            text = soup.get_text()
            prices = re.findall(r'\$[\d,]+\.?\d*|\d+\.\d{2}\s*(?:USD|EUR|GBP)', text)
            extracted_data = list(set(prices))
            
        elif data_type == "dates":
            # Extract dates
            text = soup.get_text()
            dates = re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text)
            dates += re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
            extracted_data = list(set(dates))
            
        elif data_type == "links":
            # Extract all links
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            # Make absolute URLs
            from urllib.parse import urljoin
            extracted_data = [urljoin(url, link) for link in links]
            
        elif data_type == "images":
            # Extract image URLs
            images = [img.get('src') for img in soup.find_all('img', src=True)]
            from urllib.parse import urljoin
            extracted_data = [urljoin(url, img) for img in images]
        
        return {
            "success": True,
            "url": url,
            "data_type": data_type,
            "count": len(extracted_data),
            "data": extracted_data[:100],  # Limit to first 100 items
            "truncated": len(extracted_data) > 100
        }
    
    async def monitor_website(self, url: str, check_interval: int = 3600) -> Dict:
        """Monitor a website for changes (returns initial snapshot)"""
        
        # Get initial snapshot
        initial = await self.scrape_webpage(url, format="summary")
        
        if not initial.get("success"):
            return {
                "success": False,
                "error": f"Failed to access {url}"
            }
        
        # In a real implementation, this would set up continuous monitoring
        # For MCP, we return the monitoring configuration
        return {
            "success": True,
            "url": url,
            "check_interval": check_interval,
            "initial_snapshot": initial.get("content"),
            "monitoring_id": f"monitor_{hash(url)}",
            "status": "monitoring_configured",
            "next_check": (datetime.now().timestamp() + check_interval),
            "instructions": "Monitoring configured. Would check every {check_interval} seconds in production."
        }
    
    async def analyze_website(self, url: str) -> Dict:
        """Analyze website structure and content"""
        
        # Scrape with structured output
        result = ultra_scraper.scrape(url, output_format='structured')
        
        if not isinstance(result, dict) or not result.get('success'):
            return {"success": False, "error": "Failed to analyze website"}
        
        # Extract analysis data
        analysis = {
            "success": True,
            "url": url,
            "structure": {
                "title": result.get('title'),
                "meta_tags": len(result.get('meta', {})),
                "total_links": len(result.get('links', [])),
                "internal_links": sum(1 for link in result.get('links', []) 
                                    if url.split('/')[2] in link),
                "external_links": sum(1 for link in result.get('links', []) 
                                    if url.split('/')[2] not in link),
                "images": len(result.get('images', [])),
                "text_length": len(result.get('text', ''))
            },
            "content_preview": result.get('text', '')[:500],
            "key_metadata": dict(list(result.get('meta', {}).items())[:10])
        }
        
        return analysis
    
    async def estimate_cost(self, requests_per_day: int) -> Dict:
        """Estimate costs for scraping at scale"""
        
        # Calculate costs
        costs = cost_calculator.calculate_scale_costs(
            requests_per_day=requests_per_day,
            captcha_rate=0.05,
            proxy_usage_rate=0.8,
            selenium_rate=0.2
        )
        
        # Calculate ROI
        roi = cost_calculator.calculate_roi(
            requests_per_day=requests_per_day,
            revenue_per_request=0.01,
            success_rate=0.95
        )
        
        return {
            "success": True,
            "requests_per_day": requests_per_day,
            "daily_cost": f"${costs['daily']['total_daily']:.2f}",
            "monthly_cost": f"${costs['monthly']['total_cost']:.2f}",
            "cost_per_1000": f"${costs['annual']['cost_per_1000_requests']:.2f}",
            "breakdown": {
                "processing": f"${costs['daily']['request_cost']:.2f}/day",
                "captchas": f"${costs['daily']['captcha_cost']:.2f}/day",
                "bandwidth": f"${costs['daily']['proxy_bandwidth_cost']:.2f}/day",
                "infrastructure": f"${costs['daily']['infrastructure_cost']:.2f}/day"
            },
            "roi_analysis": {
                "daily_revenue_at_1_cent": f"${roi['daily_revenue']:.2f}",
                "daily_profit": f"${roi['daily_profit']:.2f}",
                "profit_margin": f"{roi['profit_margin']:.1f}%",
                "break_even_requests": roi['break_even_requests']
            },
            "recommendations": [
                "Use 'clean_text' format to reduce processing",
                "Enable caching for frequently accessed pages",
                "Use 'summary' format for quick insights",
                "Batch similar requests together"
            ]
        }
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            "total_requests": self.usage_stats['total_requests'],
            "successful": self.usage_stats['successful_requests'],
            "failed": self.usage_stats['failed_requests'],
            "success_rate": (self.usage_stats['successful_requests'] / 
                           max(self.usage_stats['total_requests'], 1)) * 100
        }
    
    def get_server_info(self) -> Dict:
        """Get MCP server information"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": list(self.tools.keys()),
            "capabilities": [
                "Web scraping with anti-bot detection",
                "LLM-friendly output formats",
                "Multiple URL batch processing",
                "Data extraction (emails, phones, prices)",
                "Website monitoring",
                "Cost estimation",
                "27+ anti-detection techniques"
            ],
            "output_formats": [
                "clean_text - Plain readable text",
                "summary - Executive summary",
                "markdown - Structured markdown",
                "conversation - Dialog format",
                "structured_qa - Q&A pairs",
                "narrative - Natural language"
            ]
        }

# MCP Protocol Handler
async def handle_mcp_request(request: Dict) -> Dict:
    """Handle incoming MCP requests"""
    
    server = MCPWebScraperServer()
    
    # Get request type
    request_type = request.get("type")
    
    if request_type == "list_tools":
        return {
            "tools": [
                {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
                for name, info in server.tools.items()
            ]
        }
    
    elif request_type == "call_tool":
        tool_name = request.get("tool")
        parameters = request.get("parameters", {})
        return await server.handle_tool_call(tool_name, parameters)
    
    elif request_type == "server_info":
        return server.get_server_info()
    
    elif request_type == "usage_stats":
        return server.get_usage_stats()
    
    else:
        return {"error": f"Unknown request type: {request_type}"}

# Simple HTTP Server for MCP
from aiohttp import web

async def handle_http_request(request):
    """Handle HTTP requests for MCP"""
    
    try:
        data = await request.json()
        response = await handle_mcp_request(data)
        return web.json_response(response)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "service": "mcp-web-scraper"})

def create_app():
    """Create the web application"""
    app = web.Application()
    app.router.add_post('/mcp', handle_http_request)
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    return app

if __name__ == "__main__":
    # Run the MCP server
    app = create_app()
    print("\n" + "="*60)
    print("🚀 MCP Web Scraper Server Started")
    print("="*60)
    print("\nServer running at: http://localhost:8080")
    print("\nAvailable endpoints:")
    print("  POST /mcp - MCP tool calls")
    print("  GET /health - Health check")
    print("\nExample MCP request:")
    print("""
    {
        "type": "call_tool",
        "tool": "scrape_webpage",
        "parameters": {
            "url": "https://example.com",
            "format": "summary"
        }
    }
    """)
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    web.run_app(app, host='0.0.0.0', port=8080)
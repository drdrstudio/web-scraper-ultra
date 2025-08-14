# 🕷️ Web Scraper Ultra - Enterprise-Grade Web Scraping Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.15-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

**The most advanced open-source web scraper with 27+ anti-detection techniques**

[Live Demo](http://164.92.90.183) | [API Docs](#api-documentation) | [Newsletter API](#newsletter-subscription-api) | [MCP Integration](#mcp-integration)

</div>

## 🚀 Features

### Core Capabilities
- **🛡️ 27+ Anti-Bot Detection Techniques** - Industry-leading evasion
- **🌐 215,084 Residential Proxies** - Pre-configured Webshare.io integration
- **🤖 ML-Powered Proxy Selection** - Smart routing based on success rates
- **🔓 Automatic CAPTCHA Solving** - 2captcha integration ($25 pre-loaded)
- **📱 Mobile Device Simulation** - 4 device profiles with touch events
- **🧠 LLM-Friendly Outputs** - 7 formats optimized for AI processing
- **📮 Newsletter Subscription API** - Auto-find and subscribe to any newsletter
- **🎯 Site-Specific Bypasses** - Cloudflare, DataDome, PerimeterX, Akamai
- **💾 Multiple Data Destinations** - CSV, PostgreSQL, Google Sheets
- **📊 Beautiful Dashboard** - Real-time monitoring and analytics

### Advanced Anti-Detection Features

#### 🔒 Browser Fingerprinting Protection
- Screen & viewport spoofing (25+ profiles)
- Hardware spoofing (CPU, GPU, memory)
- Canvas fingerprint randomization
- WebGL vendor/renderer manipulation
- AudioContext fingerprint protection
- Battery API spoofing
- Network info API spoofing

#### 🌐 Network-Level Protection
- DNS over HTTPS (5 providers)
- TLS/JA3 fingerprinting bypass
- TCP fingerprint randomization
- Request timing jitter (microsecond-level)
- Referrer chain building
- Fetch metadata generation

#### 🖱️ Human Behavior Simulation
- Bezier curve mouse movements
- Natural typing with typos
- Reading pattern simulation
- Random hovering & scrolling
- Tab switching simulation
- Idle period patterns

#### 🚨 Intelligent Recovery
- 12 ban type classifications
- ML-based pattern analysis
- Automatic recovery strategies
- Domain reputation tracking
- Exponential backoff with jitter

## 📦 Installation

### Quick Start (Local)

```bash
# Clone the repository
git clone https://github.com/yourusername/web-scraper-ultra.git
cd web-scraper-ultra

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the application
python app_complete.py
```

### 🐳 Docker Deployment

```bash
docker build -t web-scraper-ultra .
docker run -p 5000:5000 --env-file .env web-scraper-ultra
```

### ☁️ Cloud Deployment (DigitalOcean)

Already deployed at: **http://164.92.90.183**

To deploy your own instance:
```bash
./deploy_digitalocean.sh
```

## 📡 API Documentation

### Authentication
All API endpoints require Bearer token authentication:
```
Authorization: Bearer YOUR_API_KEY
```

### Core Scraping Endpoint

```http
POST /api/v3/scrape
```

**Request:**
```json
{
  "url": "https://example.com",
  "strategy": "auto",
  "use_proxy": true,
  "output_format": "llm_clean_text",
  "options": {
    "wait_for": "networkidle",
    "timeout": 30000,
    "extract_links": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": "Extracted content...",
  "metadata": {
    "strategy_used": "undetected_chrome",
    "proxy_used": "residential_US",
    "response_time": 2.34,
    "timestamp": "2025-01-14T10:00:00Z"
  }
}
```

### Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `llm_clean_text` | Clean, readable text | AI analysis |
| `structured_qa` | Q&A pairs | Training data |
| `markdown` | Formatted markdown | Documentation |
| `conversation` | Dialog format | Chatbot training |
| `summary` | Executive summary | Quick insights |
| `json_ld` | Structured data | Knowledge graphs |
| `narrative` | Natural description | Content generation |

## 📮 Newsletter Subscription API

Automatically find and subscribe to newsletters on any website.

```http
POST /api/subscribe
```

**Request:**
```json
{
  "domain": "techcrunch.com"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Subscription form submitted successfully",
  "email_used": "test+techcrunch_123456@example.com",
  "method": "form_based"
}
```

### Detection Methods
- Form-based detection (15+ strategies)
- Standalone email inputs
- Newsletter link following
- Footer scanning
- Modal/popup handling

## 🤖 MCP Integration (Claude Desktop)

This scraper includes a Model Context Protocol server for Claude Desktop integration.

### Setup

1. Install MCP tools:
```bash
./setup_mcp.sh
```

2. Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "web-scraper": {
      "command": "python",
      "args": ["/path/to/mcp_stdio_server.py"]
    }
  }
}
```

3. Available MCP Tools:
- `scrape_webpage` - Scrape with LLM formats
- `scrape_multiple` - Batch processing
- `extract_data` - Email/phone/price extraction
- `analyze_website` - Structure analysis
- `monitor_website` - Change detection
- `estimate_cost` - Cost projections

## 📊 Recipe System

Pre-configured scraping templates for common use cases:

```python
# Use a recipe
from recipe_manager import recipe_manager

# List available recipes
recipes = recipe_manager.list_recipes()

# Use e-commerce recipe
result = recipe_manager.execute_recipe(
    "e-commerce-product",
    {"url": "https://amazon.com/dp/B01234"}
)
```

### Default Recipes
- 🛍️ E-commerce Product Scraper
- 📰 News Article Extractor
- 📱 Social Media Post Collector
- 🏠 Real Estate Listing Scraper
- 💼 Job Posting Extractor

## 🔧 Configuration

### Environment Variables

```env
# API Keys
API_KEY=your-api-key
NEWSLETTER_API_KEY=your-newsletter-key

# Proxy Service (215,084 proxies included)
WEBSHARE_API_KEY=hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms

# CAPTCHA Solving
TWOCAPTCHA_API_KEY=a2e9e05f58edb279b211ca8292f206d1

# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Google Sheets
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Success Rate | 85-95% |
| Avg Response Time | 2-5 seconds |
| Concurrent Sessions | Unlimited |
| Proxy Pool | 215,084 IPs |
| CAPTCHA Success | 90%+ |
| Supported Sites | 1000+ tested |

## 💰 Cost Analysis

| Volume | Cost/Day | Per 1K Pages | Monthly |
|--------|----------|--------------|---------|
| 1,000 | $0.20 | $0.20 | $6 |
| 10,000 | $0.63 | $0.063 | $19 |
| 100,000 | $7.42 | $0.074 | $223 |
| 1,000,000 | $74.20 | $0.074 | $2,226 |

**10-70x cheaper than commercial alternatives!**

## 🔔 Monitoring

### Slack Integration

Set up real-time monitoring:

```bash
./setup_slack_monitoring.sh
```

Features:
- Health checks every 5 minutes
- Instant error alerts
- Daily usage reports
- Component status tracking

## 🛠️ Development

### Running Tests

```bash
# All tests
pytest

# Specific test suite
python test_ultra_scraper.py
python test_newsletter_api.py
```

### Adding New Bypasses

```python
from site_bypasses import site_bypasses

# Register new bypass
@site_bypasses.register("example.com")
def bypass_example(driver):
    # Your bypass logic
    return True
```

## 📝 Documentation

- [Complete Documentation](CLAUDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Scaling for Business](SCALE-FOR-BUSINESS.md)
- [Newsletter API Guide](NEWSLETTER_API_README.md)
- [MCP Integration](README_MCP.md)
- [Google Sheets Setup](GOOGLE_SHEETS_SETUP.md)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit PRs.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Claude's assistance
- Webshare.io for proxy infrastructure
- 2captcha for CAPTCHA solving
- The open-source community

## ⚠️ Disclaimer

This tool is for educational and legitimate web scraping purposes only. Always respect robots.txt, terms of service, and rate limits. The authors are not responsible for misuse.

## 📞 Support

- GitHub Issues: [Report bugs](https://github.com/yourusername/web-scraper-ultra/issues)
- Email: support@example.com
- Documentation: [Full docs](CLAUDE.md)

---

<div align="center">

**Built with ❤️ using cutting-edge anti-detection technology**

[⭐ Star this repo](https://github.com/yourusername/web-scraper-ultra) | [🍴 Fork](https://github.com/yourusername/web-scraper-ultra/fork) | [🐛 Report Bug](https://github.com/yourusername/web-scraper-ultra/issues)

</div>
# 🚀 Quick Implementation Guide for Web Scraper APIs

## API Credentials
```
Main Scraper API: ultra-scraper-cee75bd9cb10052c2d06868578ea9c61
Newsletter API: newsletter-8e2974e0e2196a04e6272b2448306554
Base URL: http://164.92.90.183
```

## 1️⃣ General Web Scraping

### Basic Usage
```javascript
// Scrape any website with anti-bot protection
const scrapeWebsite = async (url) => {
  const response = await fetch('http://164.92.90.183/api/v3/scrape', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      url: url,
      strategy: 'auto',  // Auto-selects best method
      use_proxy: true,    // Uses 215K residential proxies
      output_format: 'llm_clean_text'  // AI-friendly output
    })
  });
  return response.json();
};
```

### Output Formats
- `llm_clean_text` - Clean text for AI analysis
- `structured_qa` - Q&A pairs for training
- `markdown` - Formatted markdown
- `json_ld` - Structured data extraction

## 2️⃣ Newsletter Subscription

### Auto-Subscribe to Any Newsletter
```javascript
// Find and subscribe to newsletter on any website
const subscribeNewsletter = async (domain) => {
  const response = await fetch('http://164.92.90.183/api/subscribe', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer newsletter-8e2974e0e2196a04e6272b2448306554',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      domain: domain  // e.g., "techcrunch.com"
    })
  });
  return response.json();
};
```

## 3️⃣ Property Owner Lookup

### Search Property Records
```javascript
// Look up property owner by address
const lookupPropertyOwner = async (address) => {
  const response = await fetch('http://164.92.90.183/api/property/search', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      address: address,
      county: 'Los Angeles',  // Optional
      state: 'CA'             // Optional
    })
  });
  return response.json();
};
```

### Batch Property Search
```javascript
// Look up multiple properties at once (max 100)
const batchPropertyLookup = async (addresses) => {
  const response = await fetch('http://164.92.90.183/api/property/batch', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      addresses: addresses  // Array of address strings
    })
  });
  return response.json();
};
```

## 🎯 Python Examples

### Web Scraping
```python
import requests

def scrape_website(url):
    response = requests.post(
        'http://164.92.90.183/api/v3/scrape',
        headers={
            'Authorization': 'Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61',
            'Content-Type': 'application/json'
        },
        json={
            'url': url,
            'strategy': 'auto',
            'use_proxy': True,
            'output_format': 'llm_clean_text'
        }
    )
    return response.json()
```

### Newsletter Subscription
```python
def subscribe_to_newsletter(domain):
    response = requests.post(
        'http://164.92.90.183/api/subscribe',
        headers={
            'Authorization': 'Bearer newsletter-8e2974e0e2196a04e6272b2448306554',
            'Content-Type': 'application/json'
        },
        json={'domain': domain}
    )
    return response.json()
```

## 🛠️ cURL Examples

### Scrape a website
```bash
curl -X POST http://164.92.90.183/api/v3/scrape \
  -H "Authorization: Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "strategy": "auto", "use_proxy": true}'
```

### Subscribe to newsletter
```bash
curl -X POST http://164.92.90.183/api/subscribe \
  -H "Authorization: Bearer newsletter-8e2974e0e2196a04e6272b2448306554" \
  -H "Content-Type: application/json" \
  -d '{"domain": "techcrunch.com"}'
```

### Property lookup
```bash
curl -X POST http://164.92.90.183/api/property/search \
  -H "Authorization: Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61" \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Los Angeles, CA"}'
```

## ⚡ Quick Tips

1. **Auto Strategy**: Always use `"strategy": "auto"` - it picks the best method
2. **Proxies**: Set `"use_proxy": true` for sites with anti-bot protection
3. **LLM Output**: Use `"output_format": "llm_clean_text"` for AI processing
4. **Batch Processing**: Use batch endpoints for multiple items (faster & cheaper)
5. **Caching**: Property API has 24-hour cache (80% cost savings)

## 📊 Available Endpoints

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/api/v3/scrape` | POST | Scrape any website |
| `/api/subscribe` | POST | Subscribe to newsletters |
| `/api/property/search` | POST | Single property lookup |
| `/api/property/batch` | POST | Multiple property lookup |
| `/api/health` | GET | Check API status |

## 🔒 Features Included

- ✅ 27+ anti-bot detection bypass techniques
- ✅ 215,084 residential proxies
- ✅ Automatic CAPTCHA solving
- ✅ JavaScript rendering
- ✅ Mobile device simulation
- ✅ Human behavior simulation
- ✅ Site-specific bypasses (Cloudflare, DataDome, etc.)
- ✅ Smart caching for repeated requests

## 🆘 Troubleshooting

- **401 Error**: Check API key is correct and includes "Bearer " prefix
- **404 Error**: Verify endpoint URL is correct
- **Timeout**: Some sites are slow, default timeout is 30 seconds
- **No data**: Site might require specific strategy, try different output formats

## 📞 Support

- Health Check: http://164.92.90.183/api/health
- GitHub: https://github.com/drdrstudio/web-scraper-ultra
- All features documented in repository README

---
**Ready to use immediately - no setup required!**
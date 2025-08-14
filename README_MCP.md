# 🤖 Web Scraper MCP for Claude Desktop

## What is this?

This is a **Model Context Protocol (MCP)** server that lets Claude Desktop scrape websites for you using natural language commands. No coding required!

## 🚀 Quick Setup (5 minutes)

### Step 1: Open Terminal
- On Mac: Press `Cmd + Space`, type "Terminal", press Enter
- On Windows: Press `Win + R`, type "cmd", press Enter

### Step 2: Navigate to the Project
```bash
cd /Users/skipmatheny/Documents/cursor2/vibecoding_gemini_claude/projects/web-scraper
```

### Step 3: Run Setup
```bash
chmod +x setup_mcp.sh
./setup_mcp.sh
```

### Step 4: Restart Claude Desktop
Close and reopen the Claude Desktop application.

### ✅ That's it! You're ready to use the web scraper in Claude.

---

## 💬 How to Use in Claude

Once setup is complete, you can ask Claude to scrape websites using natural language:

### Basic Commands

#### 1. **Scrape a webpage**
```
"Scrape https://example.com and give me a summary"
```

#### 2. **Extract specific data**
```
"Extract all email addresses from https://company.com/contact"
"Find all prices on https://shop.com/products"
"Get all image URLs from https://gallery.com"
```

#### 3. **Analyze a website**
```
"Analyze the structure of https://example.com"
```

#### 4. **Scrape multiple pages**
```
"Scrape these 3 URLs and summarize each:
- https://site1.com
- https://site2.com  
- https://site3.com"
```

#### 5. **Check costs**
```
"How much would it cost to scrape 1000 pages per day?"
```

---

## 📊 Output Formats

You can specify how you want the content formatted:

| Format | Description | Best For |
|--------|-------------|----------|
| **clean_text** | Plain, readable text | General reading |
| **summary** | Key points and highlights | Quick insights |
| **markdown** | Formatted with headers | Documentation |
| **conversation** | Dialog format | Training chat models |
| **structured_qa** | Question-answer pairs | Creating FAQs |
| **narrative** | Natural language story | Content creation |

### Example:
```
"Scrape https://news.com/article and format it as a summary"
"Get https://docs.com/guide in markdown format"
```

---

## 🛡️ Features

### Anti-Detection Technology
- ✅ **27+ optimization techniques** to avoid being blocked
- ✅ **215,084 residential proxies** (if configured)
- ✅ **Captcha solving** (if configured)
- ✅ **Human-like behavior** simulation
- ✅ **Mobile device** emulation

### Smart Features
- 🧠 **Auto-detects** best scraping strategy
- 🔄 **Automatic retry** on failures
- 📈 **Cost tracking** for budget management
- 🎯 **LLM-optimized** output formats

---

## 💰 Cost Estimates

| Daily Volume | Estimated Cost | Per 1000 Pages |
|--------------|----------------|----------------|
| 1,000 pages | $0.05-0.10 | $0.05-0.10 |
| 10,000 pages | $0.50-1.00 | $0.05-0.10 |
| 100,000 pages | $5-10 | $0.05-0.10 |

---

## ⚙️ Optional: Advanced Configuration

### Add Proxy Support (Optional)
If you have a Webshare.io account:
```bash
export WEBSHARE_API_KEY='your_api_key_here'
```

### Add Captcha Solving (Optional)
If you have a 2captcha account:
```bash
export TWOCAPTCHA_API_KEY='your_api_key_here'
```

---

## 🔧 Troubleshooting

### Issue: "Claude doesn't recognize the scraper"
**Solution:** Restart Claude Desktop after setup

### Issue: "Scraping fails on some sites"
**Solution:** Try adding "use stealth mode" to your request:
```
"Scrape https://difficult-site.com with stealth mode enabled"
```

### Issue: "Getting blocked or captchas"
**Solution:** The scraper will automatically try different strategies. For best results, consider adding proxy/captcha API keys.

### Check Logs
If something isn't working, check the log file:
```bash
tail -f /tmp/mcp_scraper.log
```

---

## 📝 Example Conversations

### Research Assistant
```
You: "I need to research electric vehicles. Scrape and summarize these sites:
- https://tesla.com/models
- https://ford.com/electric
- https://rivian.com/r1t"

Claude: [Uses web scraper to get summaries of all three sites]
```

### Price Monitoring
```
You: "Extract all prices from https://store.com/laptops and tell me the range"

Claude: [Extracts prices and provides analysis]
```

### Content Analysis
```
You: "Analyze https://competitor.com and tell me about their content strategy"

Claude: [Analyzes website structure, content types, and patterns]
```

### Data Collection
```
You: "Extract all email addresses and phone numbers from https://directory.com/contacts"

Claude: [Extracts and lists all contact information found]
```

---

## 🚫 Ethical Use

Please use this tool responsibly:
- ✅ Respect robots.txt files
- ✅ Don't overload servers
- ✅ Follow website terms of service
- ✅ Use for legitimate purposes only

---

## 📚 Advanced Documentation

For developers who want to customize or extend the scraper:
- Main documentation: `CLAUDE.md`
- API reference: `mcp_server.py`
- Cost calculations: `cost_calculator.py`
- LLM formats: `llm_formatter.py`

---

## 🆘 Support

If you encounter issues:
1. Check this README
2. Look at the logs: `/tmp/mcp_scraper.log`
3. Try the troubleshooting steps above
4. Restart Claude Desktop

---

## 🎉 Quick Test

After setup, try this in Claude:
```
"Use the web scraper to get a summary of https://example.com"
```

If Claude provides a summary, everything is working! 🎉

---

*Last Updated: January 2025*
*Version: 1.0.0*
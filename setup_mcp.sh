#!/bin/bash

# MCP Web Scraper Setup Script
# This script sets up the web scraper as an MCP server for Claude Desktop

echo "=========================================="
echo "🚀 MCP Web Scraper Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
echo ""
echo "📦 Installing required packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q aiohttp  # For MCP server

echo "✅ All packages installed"

# Create Claude Desktop configuration directory if it doesn't exist
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo ""
    echo "📁 Creating Claude Desktop configuration directory..."
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Create or update MCP configuration
MCP_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo ""
echo "⚙️ Configuring MCP for Claude Desktop..."

# Check if config file exists
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "📋 Existing Claude configuration found. Creating backup..."
    cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create the MCP configuration
cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "web-scraper": {
      "command": "$SCRIPT_DIR/venv/bin/python",
      "args": ["$SCRIPT_DIR/mcp_stdio_server.py"],
      "env": {
        "PYTHONPATH": "$SCRIPT_DIR",
        "WEBSHARE_API_KEY": "${WEBSHARE_API_KEY:-}",
        "TWOCAPTCHA_API_KEY": "${TWOCAPTCHA_API_KEY:-}"
      }
    }
  }
}
EOF

echo "✅ MCP configuration created"

# Make scripts executable
chmod +x mcp_stdio_server.py
chmod +x mcp_server.py

# Test the installation
echo ""
echo "🧪 Testing the installation..."
python3 -c "from advanced_scraper_ultra import ultra_scraper; print('✅ Scraper modules loaded successfully')" 2>/dev/null || echo "⚠️ Warning: Some modules may need additional setup"

# Create a simple test script
cat > test_mcp.py << 'EOF'
#!/usr/bin/env python3
import asyncio
from mcp_server import MCPWebScraperServer

async def test():
    server = MCPWebScraperServer()
    result = await server.scrape_webpage("https://example.com", format="summary")
    if result.get("success"):
        print("✅ MCP server test successful!")
        print(f"   Scraped content preview: {result.get('content', '')[:100]}...")
    else:
        print("❌ MCP server test failed:", result.get("error"))

asyncio.run(test())
EOF

python3 test_mcp.py
rm test_mcp.py

# Instructions for the user
echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. Restart Claude Desktop application"
echo ""
echo "2. In Claude, you can now use commands like:"
echo "   - 'Use the web scraper to get content from [URL]'"
echo "   - 'Extract all email addresses from [URL]'"
echo "   - 'Summarize the content of [URL]'"
echo "   - 'Monitor [URL] for changes'"
echo "   - 'Estimate the cost of scraping 1000 pages per day'"
echo ""
echo "3. Available output formats:"
echo "   - clean_text: Plain readable text"
echo "   - summary: Executive summary"
echo "   - markdown: Formatted markdown"
echo "   - conversation: Dialog format"
echo "   - structured_qa: Q&A pairs"
echo "   - narrative: Natural language description"
echo ""
echo "⚠️ OPTIONAL: Set API keys for advanced features:"
echo "   export WEBSHARE_API_KEY='your_key_here'"
echo "   export TWOCAPTCHA_API_KEY='your_key_here'"
echo ""
echo "📚 For more information, see README_MCP.md"
echo "=========================================="
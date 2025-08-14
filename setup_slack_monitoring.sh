#!/bin/bash

echo "🔔 Slack Monitoring Setup for Web Scraper Ultra"
echo "=============================================="
echo ""
echo "This script will set up Slack notifications for your web scraper."
echo ""
echo "📝 First, you need to create a Slack webhook:"
echo ""
echo "1. Go to: https://api.slack.com/apps"
echo "2. Click 'Create New App' → 'From scratch'"
echo "3. Name it: 'Web Scraper Monitor'"
echo "4. Select your workspace"
echo "5. Go to 'Incoming Webhooks' → Turn ON"
echo "6. Click 'Add New Webhook to Workspace'"
echo "7. Choose a channel (e.g., #monitoring or #web-scraper)"
echo "8. Copy the Webhook URL"
echo ""
read -p "Enter your Slack Webhook URL: " WEBHOOK_URL

if [ -z "$WEBHOOK_URL" ]; then
    echo "❌ No webhook URL provided. Exiting."
    exit 1
fi

# Test the webhook
echo ""
echo "Testing webhook..."
curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🎉 Web Scraper Ultra monitoring connected successfully!"}' \
    "$WEBHOOK_URL"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Webhook test successful!"
else
    echo ""
    echo "❌ Webhook test failed. Please check your URL."
    exit 1
fi

# Create monitoring service file
cat > slack_monitor_service.txt << 'EOF'
[Unit]
Description=Slack Monitor for Web Scraper
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/web-scraper
Environment="SLACK_WEBHOOK_URL=WEBHOOK_URL_PLACEHOLDER"
Environment="PATH=/opt/web-scraper/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/web-scraper/venv/bin/python /opt/web-scraper/slack_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Replace placeholder with actual webhook URL
sed -i "s|WEBHOOK_URL_PLACEHOLDER|$WEBHOOK_URL|g" slack_monitor_service.txt

echo ""
echo "📋 To deploy monitoring to your server:"
echo ""
echo "1. Upload the monitoring script:"
echo "   scp -i ~/.ssh/publicrecords_key slack_monitor.py root@164.92.90.183:/opt/web-scraper/"
echo ""
echo "2. Install the service:"
echo "   scp -i ~/.ssh/publicrecords_key slack_monitor_service.txt root@164.92.90.183:/tmp/slack-monitor.service"
echo "   ssh -i ~/.ssh/publicrecords_key root@164.92.90.183 'mv /tmp/slack-monitor.service /etc/systemd/system/'"
echo "   ssh -i ~/.ssh/publicrecords_key root@164.92.90.183 'systemctl daemon-reload'"
echo "   ssh -i ~/.ssh/publicrecords_key root@164.92.90.183 'systemctl enable slack-monitor'"
echo "   ssh -i ~/.ssh/publicrecords_key root@164.92.90.183 'systemctl start slack-monitor'"
echo ""
echo "3. Check status:"
echo "   ssh -i ~/.ssh/publicrecords_key root@164.92.90.183 'systemctl status slack-monitor'"
echo ""
echo "Your webhook URL has been saved to: slack_monitor_service.txt"
echo ""
echo "🔔 Monitoring Features:"
echo "  • Health checks every 5 minutes"
echo "  • Instant alerts on errors"
echo "  • Daily usage reports at 9 AM"
echo "  • Uptime tracking"
echo "  • Component status (DB, Proxies, etc.)"
echo ""
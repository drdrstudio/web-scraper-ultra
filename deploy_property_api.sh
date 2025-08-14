#!/bin/bash

echo "🏠 Deploying Property Owner Lookup API"
echo "======================================"
echo ""
echo "This specialized API is optimized for property owner lookups at scale."
echo ""

# Upload the new API file
echo "📤 Uploading property API..."
scp -i ~/.ssh/publicrecords_key property_owner_api.py root@164.92.90.183:/opt/web-scraper/

# Connect and start the service
ssh -i ~/.ssh/publicrecords_key root@164.92.90.183 << 'REMOTE_COMMANDS'

cd /opt/web-scraper

# Install any additional dependencies
source venv/bin/activate
pip install redis

# Create systemd service for property API
cat > /etc/systemd/system/property-api.service << 'EOF'
[Unit]
Description=Property Owner Lookup API
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/web-scraper
Environment="PATH=/opt/web-scraper/venv/bin"
Environment="PROPERTY_PORT=5002"
Environment="REDIS_HOST=localhost"
Environment="REDIS_PORT=6379"
ExecStart=/opt/web-scraper/venv/bin/python property_owner_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Add Nginx configuration for property API
cat > /etc/nginx/sites-available/property-api << 'NGINX'
upstream property_api {
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name 164.92.90.183;
    
    location /api/property/ {
        proxy_pass http://property_api/api/property/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        
        # Cache successful lookups
        proxy_cache_valid 200 24h;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
NGINX

# Enable and start service
systemctl daemon-reload
systemctl enable property-api
systemctl start property-api

# Reload Nginx
ln -sf /etc/nginx/sites-available/property-api /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Get the API key
echo ""
echo "Getting API key..."
grep "^PROPERTY_API_KEY=" /opt/web-scraper/.env || echo "PROPERTY_API_KEY=property-$(openssl rand -hex 16)" >> /opt/web-scraper/.env

# Check status
sleep 3
systemctl status property-api --no-pager | head -10

REMOTE_COMMANDS

echo ""
echo "✅ Property API Deployment Complete!"
echo ""
echo "📍 API Endpoints:"
echo "   Search: http://164.92.90.183/api/property/search"
echo "   Batch: http://164.92.90.183/api/property/batch"
echo "   Counties: http://164.92.90.183/api/property/counties"
echo "   Stats: http://164.92.90.183/api/property/stats"
echo ""
echo "🔑 Use your existing API key:"
echo "   ultra-scraper-cee75bd9cb10052c2d06868578ea9c61"
echo ""
echo "📝 Example Usage:"
echo 'curl -X POST http://164.92.90.183/api/property/search \'
echo '  -H "Authorization: Bearer ultra-scraper-cee75bd9cb10052c2d06868578ea9c61" \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{\"address\": \"123 Main St, Los Angeles, CA\"}"'
echo ""
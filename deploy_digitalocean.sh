#!/bin/bash
# DigitalOcean Deployment Script for Web Scraper
# Run this after creating your droplet

set -e  # Exit on error

echo "🚀 Web Scraper DigitalOcean Deployment"
echo "======================================="

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"test@example.com"}
API_KEY=${3:-"your-api-key-here"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Step 1: System Update${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}Step 2: Install System Dependencies${NC}"
apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    supervisor \
    git \
    curl \
    wget \
    chromium-browser \
    chromium-chromedriver \
    ufw

echo -e "${GREEN}Step 3: Configure Firewall${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo -e "${GREEN}Step 4: Setup Project Directory${NC}"
mkdir -p /opt/web-scraper
cd /opt/web-scraper

# Copy project files (adjust based on your setup)
echo -e "${YELLOW}Copying project files...${NC}"
# Option 1: Clone from git
# git clone https://github.com/yourusername/web-scraper.git .

# Option 2: Copy from local (you'll need to upload first)
# For now, we'll create the structure
cp -r /root/web-scraper/* /opt/web-scraper/ 2>/dev/null || true

echo -e "${GREEN}Step 5: Setup Python Environment${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install wheel setuptools

# Create requirements if not exists
if [ ! -f requirements.txt ]; then
    cat > requirements.txt << 'EOF'
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
undetected-chromedriver==3.5.4
cloudscraper==1.2.71
fake-useragent==1.4.0
pandas==2.1.3
numpy==1.26.2
python-dotenv==1.0.0
schedule==1.2.0
webdriver-manager==4.0.1
psycopg2-binary==2.9.9
redis==5.0.1
gunicorn==21.2.0
aiohttp==3.9.1
dnspython==2.4.2
scikit-learn==1.3.2
EOF
fi

pip install -r requirements.txt

echo -e "${GREEN}Step 6: Setup PostgreSQL${NC}"
sudo -u postgres psql << EOF
CREATE DATABASE webscraper;
CREATE USER webscraperuser WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE webscraper TO webscraperuser;
EOF

echo -e "${GREEN}Step 7: Configure Redis${NC}"
sed -i 's/supervised no/supervised systemd/g' /etc/redis/redis.conf
sed -i 's/# maxmemory <bytes>/maxmemory 256mb/g' /etc/redis/redis.conf
sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/g' /etc/redis/redis.conf
systemctl restart redis-server

echo -e "${GREEN}Step 8: Create Application Configuration${NC}"
cat > /opt/web-scraper/.env << EOF
# Flask Configuration
FLASK_APP=app_complete.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://webscraperuser:secure_password_here@localhost/webscraper

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
API_KEY=$API_KEY
NEWSLETTER_API_KEY=$API_KEY
TEST_EMAIL=$EMAIL

# Proxy Configuration (optional)
WEBSHARE_API_KEY=${WEBSHARE_API_KEY:-}
TWOCAPTCHA_API_KEY=${TWOCAPTCHA_API_KEY:-}

# Server
PORT=5000
WORKERS=4
EOF

echo -e "${GREEN}Step 9: Create Gunicorn Configuration${NC}"
cat > /opt/web-scraper/gunicorn_config.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 2
preload_app = True
accesslog = "/var/log/web-scraper/access.log"
errorlog = "/var/log/web-scraper/error.log"
loglevel = "info"
EOF

mkdir -p /var/log/web-scraper

echo -e "${GREEN}Step 10: Create Systemd Service${NC}"
cat > /etc/systemd/system/web-scraper.service << 'EOF'
[Unit]
Description=Web Scraper API
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/web-scraper
Environment="PATH=/opt/web-scraper/venv/bin"
ExecStart=/opt/web-scraper/venv/bin/gunicorn \
    --config /opt/web-scraper/gunicorn_config.py \
    app_complete:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Step 11: Create Newsletter API Service${NC}"
cat > /etc/systemd/system/newsletter-api.service << 'EOF'
[Unit]
Description=Newsletter Subscriber API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/web-scraper
Environment="PATH=/opt/web-scraper/venv/bin"
Environment="DISPLAY=:99"
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 &
ExecStart=/opt/web-scraper/venv/bin/python newsletter_subscriber_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Step 12: Configure Nginx${NC}"
cat > /etc/nginx/sites-available/web-scraper << EOF
upstream web_scraper {
    server 127.0.0.1:5000;
}

upstream newsletter_api {
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 10M;

    # Main API
    location /api/ {
        proxy_pass http://web_scraper;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # Newsletter API
    location /newsletter/ {
        rewrite ^/newsletter/(.*) /\$1 break;
        proxy_pass http://newsletter_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://web_scraper/health;
        access_log off;
    }

    # Static files (if any)
    location /static {
        alias /opt/web-scraper/static;
        expires 30d;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

ln -sf /etc/nginx/sites-available/web-scraper /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo -e "${GREEN}Step 13: Set Permissions${NC}"
chown -R www-data:www-data /opt/web-scraper
chmod -R 755 /opt/web-scraper
chmod 600 /opt/web-scraper/.env

echo -e "${GREEN}Step 14: Start Services${NC}"
systemctl daemon-reload
systemctl enable web-scraper
systemctl enable newsletter-api
systemctl enable redis-server
systemctl enable postgresql

systemctl start web-scraper
systemctl start newsletter-api

echo -e "${GREEN}Step 15: Setup Monitoring (Optional)${NC}"
# Install monitoring
apt-get install -y htop nethogs iotop

# Create monitoring script
cat > /usr/local/bin/check-web-scraper << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet web-scraper; then
    echo "Web scraper is down, restarting..."
    systemctl restart web-scraper
    echo "Web scraper restarted at $(date)" >> /var/log/web-scraper/restarts.log
fi
EOF

chmod +x /usr/local/bin/check-web-scraper

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-web-scraper") | crontab -

echo -e "${GREEN}Step 16: Setup SSL with Certbot (Optional)${NC}"
if [ "$DOMAIN" != "your-domain.com" ]; then
    apt-get install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
fi

echo -e "${GREEN}Step 17: Create Helper Scripts${NC}"

# Status check script
cat > /usr/local/bin/scraper-status << 'EOF'
#!/bin/bash
echo "=== Web Scraper Status ==="
systemctl status web-scraper --no-pager | head -n 10
echo ""
echo "=== Newsletter API Status ==="
systemctl status newsletter-api --no-pager | head -n 10
echo ""
echo "=== Recent Logs ==="
tail -n 20 /var/log/web-scraper/error.log
echo ""
echo "=== System Resources ==="
free -h
df -h /
echo ""
echo "=== Active Connections ==="
ss -tulpn | grep -E ':(5000|5001|80|443)'
EOF

chmod +x /usr/local/bin/scraper-status

# Restart script
cat > /usr/local/bin/scraper-restart << 'EOF'
#!/bin/bash
echo "Restarting all services..."
systemctl restart redis-server
systemctl restart postgresql
systemctl restart web-scraper
systemctl restart newsletter-api
systemctl restart nginx
echo "All services restarted!"
scraper-status
EOF

chmod +x /usr/local/bin/scraper-restart

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your Web Scraper API is now running!"
echo ""
echo "📍 Main API: http://$DOMAIN/api/"
echo "📍 Newsletter API: http://$DOMAIN/newsletter/"
echo "📍 Health Check: http://$DOMAIN/health"
echo ""
echo "📝 Useful Commands:"
echo "  scraper-status  - Check service status"
echo "  scraper-restart - Restart all services"
echo "  journalctl -u web-scraper -f - View logs"
echo ""
echo "🔐 Security Note:"
echo "  1. Change the PostgreSQL password in .env"
echo "  2. Update API_KEY in .env"
echo "  3. Configure your domain's DNS to point to this server"
echo ""
echo "📊 Monitor your server:"
echo "  htop - CPU and memory usage"
echo "  nethogs - Network usage by process"
echo "  tail -f /var/log/web-scraper/error.log - Error logs"
echo ""

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
echo "🌐 Server IP: $SERVER_IP"
echo ""
echo "Next steps:"
echo "1. Update DNS to point $DOMAIN to $SERVER_IP"
echo "2. Test the API: curl http://$SERVER_IP/health"
echo "3. Enable SSL: certbot --nginx -d $DOMAIN"
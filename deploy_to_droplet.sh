#!/bin/bash
# Deployment script for web-scraper-ultra droplet
# This script will be run ON the droplet after SSH access is configured

set -e

echo "🚀 Starting Web Scraper Ultra Deployment on DigitalOcean"
echo "========================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Update system
echo -e "${GREEN}Step 1: Updating system packages${NC}"
apt-get update
apt-get upgrade -y

# Step 2: Install Python and dependencies
echo -e "${GREEN}Step 2: Installing Python and system dependencies${NC}"
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
    ufw \
    htop \
    nethogs \
    iotop

# Step 3: Configure firewall
echo -e "${GREEN}Step 3: Configuring firewall${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp  # Flask app
ufw allow 5001/tcp  # Newsletter API
ufw --force enable

# Step 4: Clone the repository
echo -e "${GREEN}Step 4: Setting up project directory${NC}"
mkdir -p /opt/web-scraper
cd /opt/web-scraper

# Create a temporary upload script
cat > upload_files.sh << 'UPLOAD_SCRIPT'
#!/bin/bash
echo "Please upload your web scraper files to this server."
echo "You can use one of these methods:"
echo ""
echo "1. From your local machine, run:"
echo "   scp -r /Users/skipmatheny/Documents/cursor2/vibecoding_gemini_claude/projects/web-scraper/* root@164.92.90.183:/opt/web-scraper/"
echo ""
echo "2. Or use rsync for better performance:"
echo "   rsync -avz --progress /Users/skipmatheny/Documents/cursor2/vibecoding_gemini_claude/projects/web-scraper/ root@164.92.90.183:/opt/web-scraper/"
echo ""
echo "After uploading, press Enter to continue..."
read
UPLOAD_SCRIPT

chmod +x upload_files.sh
./upload_files.sh

# Step 5: Setup Python environment
echo -e "${GREEN}Step 5: Setting up Python virtual environment${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Step 6: Install Python packages
echo -e "${GREEN}Step 6: Installing Python dependencies${NC}"
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    # Install core packages if requirements.txt is missing
    pip install Flask==3.0.0 flask-cors==4.0.0 requests==2.31.0 \
        beautifulsoup4==4.12.2 selenium==4.15.2 undetected-chromedriver==3.5.4 \
        cloudscraper==1.2.71 fake-useragent==1.4.0 pandas==2.1.3 numpy==1.26.2 \
        python-dotenv==1.0.0 schedule==1.2.0 webdriver-manager==4.0.1 \
        psycopg2-binary==2.9.9 redis==5.0.1 gunicorn==21.2.0 aiohttp==3.9.1 \
        dnspython==2.4.2 scikit-learn==1.3.2 twocaptcha==1.2.5 gspread==5.12.0 \
        oauth2client==4.1.3
fi

# Step 7: Setup PostgreSQL
echo -e "${GREEN}Step 7: Configuring PostgreSQL${NC}"
sudo -u postgres psql << EOF
CREATE DATABASE webscraper;
CREATE USER webscraperuser WITH PASSWORD 'WebScr@per2025!';
GRANT ALL PRIVILEGES ON DATABASE webscraper TO webscraperuser;
EOF

# Step 8: Configure Redis
echo -e "${GREEN}Step 8: Configuring Redis${NC}"
sed -i 's/supervised no/supervised systemd/g' /etc/redis/redis.conf
sed -i 's/# maxmemory <bytes>/maxmemory 512mb/g' /etc/redis/redis.conf
sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/g' /etc/redis/redis.conf
systemctl restart redis-server

# Step 9: Create environment configuration
echo -e "${GREEN}Step 9: Creating environment configuration${NC}"
cat > /opt/web-scraper/.env << 'ENV_CONFIG'
# Flask Configuration
FLASK_APP=app_complete.py
FLASK_ENV=production
FLASK_SECRET_KEY=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://webscraperuser:WebScr@per2025!@localhost/webscraper

# Alternative Neon Database (if preferred)
# DATABASE_URL=postgres://neondb_owner:npg_kz3TbqPcgwK8@ep-square-hat-ad5p8p5z-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
API_KEY=ultra-scraper-api-key-$(openssl rand -hex 16)
NEWSLETTER_API_KEY=newsletter-api-key-$(openssl rand -hex 16)
TEST_EMAIL=test@example.com

# Proxy Configuration (Webshare.io)
WEBSHARE_API_KEY=hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms

# 2captcha
TWOCAPTCHA_API_KEY=a2e9e05f58edb279b211ca8292f206d1

# Google Sheets
GOOGLE_CLIENT_ID=1098095756657-evjf9phjvb33jttoumhottedcod5ttge.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Server
PORT=5000
WORKERS=4
ENV_CONFIG

# Replace the openssl commands with actual values
SECRET1=$(openssl rand -hex 32)
SECRET2=$(openssl rand -hex 32)
API1=$(openssl rand -hex 16)
API2=$(openssl rand -hex 16)

sed -i "s/\$(openssl rand -hex 32)/$SECRET1/g" /opt/web-scraper/.env
sed -i "s/\$(openssl rand -hex 32)/$SECRET2/g" /opt/web-scraper/.env
sed -i "s/\$(openssl rand -hex 16)/$API1/g" /opt/web-scraper/.env
sed -i "s/\$(openssl rand -hex 16)/$API2/g" /opt/web-scraper/.env

# Step 10: Create Gunicorn configuration
echo -e "${GREEN}Step 10: Creating Gunicorn configuration${NC}"
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

# Step 11: Create systemd services
echo -e "${GREEN}Step 11: Creating systemd services${NC}"

# Main web scraper service
cat > /etc/systemd/system/web-scraper.service << 'EOF'
[Unit]
Description=Web Scraper Ultra API
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

# Newsletter API service
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
Environment="PORT=5001"
ExecStart=/opt/web-scraper/venv/bin/python newsletter_subscriber_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 12: Configure Nginx
echo -e "${GREEN}Step 12: Configuring Nginx${NC}"
cat > /etc/nginx/sites-available/web-scraper << 'NGINX_CONFIG'
upstream web_scraper {
    server 127.0.0.1:5000;
}

upstream newsletter_api {
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name 164.92.90.183;
    client_max_body_size 10M;

    # Main API
    location /api/ {
        proxy_pass http://web_scraper;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # Newsletter API
    location /newsletter/ {
        rewrite ^/newsletter/(.*) /$1 break;
        proxy_pass http://newsletter_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Dashboard
    location / {
        proxy_pass http://web_scraper;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://web_scraper/health;
        access_log off;
    }

    # Static files
    location /static {
        alias /opt/web-scraper/static;
        expires 30d;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
NGINX_CONFIG

ln -sf /etc/nginx/sites-available/web-scraper /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Step 13: Set permissions
echo -e "${GREEN}Step 13: Setting permissions${NC}"
chown -R www-data:www-data /opt/web-scraper
chmod -R 755 /opt/web-scraper
chmod 600 /opt/web-scraper/.env

# Step 14: Start services
echo -e "${GREEN}Step 14: Starting services${NC}"
systemctl daemon-reload
systemctl enable web-scraper
systemctl enable newsletter-api
systemctl enable redis-server
systemctl enable postgresql
systemctl enable nginx

systemctl start web-scraper
systemctl start newsletter-api

# Step 15: Create helper scripts
echo -e "${GREEN}Step 15: Creating helper scripts${NC}"

# Status check script
cat > /usr/local/bin/scraper-status << 'EOF'
#!/bin/bash
echo "=== Web Scraper Ultra Status ==="
systemctl status web-scraper --no-pager | head -n 10
echo ""
echo "=== Newsletter API Status ==="
systemctl status newsletter-api --no-pager | head -n 10
echo ""
echo "=== Recent Logs ==="
tail -n 20 /var/log/web-scraper/error.log 2>/dev/null || echo "No error logs yet"
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

# Step 16: Display completion message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your Web Scraper Ultra API is now running!"
echo ""
echo "📍 Access Points:"
echo "   Main API: http://164.92.90.183/api/"
echo "   Dashboard: http://164.92.90.183/"
echo "   Newsletter API: http://164.92.90.183/newsletter/"
echo "   Health Check: http://164.92.90.183/health"
echo ""
echo "📝 API Keys (saved in /opt/web-scraper/.env):"
grep "^API_KEY=" /opt/web-scraper/.env
grep "^NEWSLETTER_API_KEY=" /opt/web-scraper/.env
echo ""
echo "📝 Useful Commands:"
echo "   scraper-status  - Check service status"
echo "   scraper-restart - Restart all services"
echo "   journalctl -u web-scraper -f - View logs"
echo ""
echo "🔐 Security Notes:"
echo "   1. Save the API keys shown above"
echo "   2. Consider setting up a domain name"
echo "   3. Enable SSL with Let's Encrypt"
echo ""
echo "📊 Monitor your server:"
echo "   htop - CPU and memory usage"
echo "   nethogs - Network usage by process"
echo "   tail -f /var/log/web-scraper/error.log - Error logs"
echo ""
echo "🚀 Test the API:"
echo "   curl http://164.92.90.183/health"
echo ""
# 🚀 Web Scraper Deployment Guide

## 📊 Current Status
- ✅ **Phases 1-6 Complete**: Core scraping, UI, proxies, API, webhooks
- 🟡 **Phase 7 Pending**: Recipes, scheduling
- 🟡 **Phase 8 Pending**: Production deployment

## 🎯 Recommended Production Stack

### Option A: **Railway** (Recommended - $5/month)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Option B: **Render** (Free tier available)
1. Connect GitHub repo at [render.com](https://render.com)
2. Create new Web Service
3. Set environment variables
4. Deploy automatically on push

### Database: **Neon** (Free 0.5GB)
1. Sign up at [neon.tech](https://neon.tech)
2. Create database
3. Copy connection string to `.env.production`

## 🔧 Setup Steps

### 1. Create Neon Database
```bash
# Using Neon CLI
neonctl auth
neonctl projects create --name web-scraper
neonctl databases create --name scraper_db
neonctl connection-string
```

### 2. Update Environment Variables
```bash
# Copy production env template
cp .env.production .env

# Update with your Neon connection string
DATABASE_URL=postgresql://user:pass@host.neon.tech/database
```

### 3. Deploy to Railway
```bash
# Create railway.json
cat > railway.json << EOF
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Add Procfile for production
echo "web: gunicorn app:app --bind 0.0.0.0:$PORT" > Procfile

# Deploy
railway up
```

## 📝 For Your Team

### API Documentation
```python
# Authentication
headers = {"X-API-Key": "your-api-key"}

# Trigger scrape
POST /api/scrape
{
  "url": "https://example.com",
  "destination": "database",  # or "csv", "google_sheet"
  "webhook_url": "https://your-webhook.com/notify"
}

# Check status
GET /api/status/{job_id}

# Get results  
GET /api/results/{job_id}
```

### Environment Variables Needed
- `DATABASE_URL` - Neon PostgreSQL connection
- `WEBSHARE_API_KEY` - Your proxy API key
- `API_KEY` - Secure key for API access
- `PORT` - Server port (Railway/Render provide this)

### Quick Start for Team Members
```bash
# Clone repo
git clone [your-repo]

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run locally
python app.py

# Access at http://localhost:5000
```

## 🎯 Next Steps to Complete PRD

### Phase 7: Advanced Features (1-2 days)
- [ ] Recipe system for saved configs
- [ ] Job scheduling with APScheduler
- [ ] Enhanced dashboard

### Phase 8: Production (1 day)
- [ ] Deploy to Railway/Render
- [ ] Set up monitoring
- [ ] Create Docker container
- [ ] Add rate limiting

## 💰 Cost Breakdown
- **Railway**: $5/month (backend hosting)
- **Neon**: Free (0.5GB database)
- **Webshare**: Your existing plan
- **Total**: ~$5/month

## 🔒 Security Checklist
- [x] API key authentication
- [x] Environment variables for secrets
- [ ] Rate limiting (add with Flask-Limiter)
- [ ] HTTPS only in production
- [ ] Input validation
- [ ] SQL injection protection (using ORM)

## 📈 Scaling Options
1. **Add Redis** for job queue (Railway Redis $5/month)
2. **Use Celery** for better background jobs
3. **Add CloudFlare** for DDoS protection
4. **Upgrade Neon** for more storage
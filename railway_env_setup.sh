#\!/bin/bash

# Set all environment variables for Railway deployment

# Neon Database
railway variables set DATABASE_URL="postgres://neondb_owner:npg_kz3TbqPcgwK8@ep-square-hat-ad5p8p5z-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Webshare.io
railway variables set WEBSHARE_API_KEY="hiya2vn2k5mx5lahgl4aexfvto34gf3jx0ehq3ms"

# Google OAuth
railway variables set GOOGLE_CLIENT_ID="1098095756657-evjf9phjvb33jttoumhottedcod5ttge.apps.googleusercontent.com"
railway variables set GOOGLE_CLIENT_SECRET="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"

# Flask Config
railway variables set FLASK_SECRET_KEY="$(openssl rand -hex 32)"
railway variables set FLASK_PORT="$PORT"
railway variables set API_KEY="$(openssl rand -hex 16)"

# 2captcha
railway variables set TWOCAPTCHA_API_KEY="a2e9e05f58edb279b211ca8292f206d1"

echo "All environment variables set\!"

#!/bin/bash
# Quick deployment script - run this from your LOCAL machine
# This will upload files and deploy to your DigitalOcean droplet

DROPLET_IP="164.92.90.183"
LOCAL_DIR="/Users/skipmatheny/Documents/cursor2/vibecoding_gemini_claude/projects/web-scraper"

echo "🚀 Web Scraper Ultra - Quick Deploy to DigitalOcean"
echo "===================================================="
echo ""
echo "This script will:"
echo "1. Upload your web scraper files to the droplet"
echo "2. Install all dependencies"
echo "3. Configure the server"
echo "4. Start the services"
echo ""
echo "⚠️  Prerequisites:"
echo "   - SSH access to root@$DROPLET_IP must be configured"
echo "   - You need to have your SSH key added to the droplet"
echo ""
echo "To add SSH access, you can either:"
echo "1. Use the DigitalOcean web console to add your public key"
echo "2. Use password authentication if enabled"
echo ""
read -p "Do you have SSH access configured? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please configure SSH access first. Here's how:"
    echo ""
    echo "Option 1: Generate an SSH key (if you don't have one):"
    echo "   ssh-keygen -t ed25519 -C 'your-email@example.com'"
    echo ""
    echo "Option 2: Copy your public key to clipboard:"
    echo "   pbcopy < ~/.ssh/id_ed25519.pub"
    echo ""
    echo "Option 3: Add it via DigitalOcean console:"
    echo "   1. Go to https://cloud.digitalocean.com/droplets"
    echo "   2. Click on 'web-scraper-ultra'"
    echo "   3. Access -> Launch Droplet Console"
    echo "   4. Login as root and run:"
    echo "      mkdir -p ~/.ssh"
    echo "      echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
    echo "      chmod 600 ~/.ssh/authorized_keys"
    echo ""
    exit 1
fi

echo ""
echo "📦 Step 1: Uploading files to droplet..."
echo "----------------------------------------"

# Create remote directory
ssh root@$DROPLET_IP "mkdir -p /opt/web-scraper" 2>/dev/null

# Upload files using rsync (excludes venv and other unnecessary files)
rsync -avz --progress \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'scraped_data.csv' \
    --exclude 'proxies.json' \
    --exclude 'webshare_proxies.txt' \
    "$LOCAL_DIR/" root@$DROPLET_IP:/opt/web-scraper/

if [ $? -ne 0 ]; then
    echo "❌ Failed to upload files. Please check your SSH configuration."
    exit 1
fi

echo "✅ Files uploaded successfully!"
echo ""
echo "🔧 Step 2: Running deployment on droplet..."
echo "-------------------------------------------"

# Upload and run the deployment script
scp "$LOCAL_DIR/deploy_digitalocean.sh" root@$DROPLET_IP:/tmp/deploy.sh
ssh root@$DROPLET_IP "chmod +x /tmp/deploy.sh && /tmp/deploy.sh '$DROPLET_IP' 'admin@example.com' 'secure-api-key-here'"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your Web Scraper Ultra is now live at:"
echo "   Dashboard: http://$DROPLET_IP/"
echo "   API: http://$DROPLET_IP/api/"
echo "   Newsletter API: http://$DROPLET_IP/newsletter/"
echo "   Health: http://$DROPLET_IP/health"
echo ""
echo "📝 Next steps:"
echo "1. Test the API: curl http://$DROPLET_IP/health"
echo "2. Get your API keys: ssh root@$DROPLET_IP 'grep API_KEY /opt/web-scraper/.env'"
echo "3. Consider adding a domain name"
echo "4. Enable SSL with Let's Encrypt"
echo ""
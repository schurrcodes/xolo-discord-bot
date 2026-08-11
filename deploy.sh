#!/bin/bash
set -e

echo "Starting deployment..."

# Pull latest updates from GitHub
git pull origin main

# Activate virtual environment & update packages
source .venv/bin/activate
pip install -r requirements.txt

# Restart if process exists, otherwise start it for the first time
echo "Reloading Discord bot in PM2..."
pm2 restart discord-bot || pm2 start .venv/bin/python --name "discord-bot" -- main.py

# Save PM2 state
pm2 save

echo "✅ Deployment complete!"

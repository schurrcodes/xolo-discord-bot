#!/bin/bash

set -e

echo "Starting deployment..."

# Pull latest changes from github
git pull origin main

# Activate virual environment & update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Restart PM2 service process
pm2 restart discord-bot

echo "Deployment Completed."

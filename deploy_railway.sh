#!/bin/bash

# Railway Deployment Script
echo "🚀 Deploying Laser Equipment Intelligence to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (interactive)
echo "🔐 Please login to Railway..."
railway login

# Deploy API server
echo "📡 Deploying API server..."
railway up --service laser-api

# Deploy worker
echo "🕷️ Deploying worker..."
railway up --service laser-worker --config railway_worker.json

# Get deployment URLs
echo "🌐 Getting deployment URLs..."
API_URL=$(railway domain --service laser-api)
echo "API URL: https://$API_URL"

# Update frontend environment
echo "🔧 Updating frontend environment..."
echo "NEXT_PUBLIC_API_URL=https://$API_URL" > web/.env.production

echo "✅ Deployment complete!"
echo "📱 Update your frontend deployment with:"
echo "NEXT_PUBLIC_API_URL=https://$API_URL"

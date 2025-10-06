#!/bin/bash

echo "🚀 Deploying Laser Equipment Intelligence to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "🔐 Please login to Railway (this will open a browser window)..."
railway login

if [ $? -ne 0 ]; then
    echo "❌ Railway login failed. Please try again."
    exit 1
fi

echo "📡 Deploying API server..."
railway up --service laser-api

if [ $? -ne 0 ]; then
    echo "❌ API server deployment failed."
    exit 1
fi

echo "🕷️ Deploying worker..."
railway up --service laser-worker --config railway_worker.json

if [ $? -ne 0 ]; then
    echo "❌ Worker deployment failed."
    exit 1
fi

echo "🌐 Getting API URL..."
API_URL=$(railway domain --service laser-api)
echo "✅ API URL: https://$API_URL"

echo ""
echo "🔧 Next steps:"
echo "1. Update your frontend deployment with:"
echo "   NEXT_PUBLIC_API_URL=https://$API_URL"
echo ""
echo "2. Test the API:"
echo "   curl https://$API_URL/health"
echo "   curl https://$API_URL/api/v1/lasermatch/items?limit=5"
echo ""
echo "✅ Deployment complete!"

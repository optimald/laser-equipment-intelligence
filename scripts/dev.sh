#!/bin/bash

# Development script for Laser Equipment Intelligence
# Starts the frontend development server on port 3001

echo "🚀 Starting Laser Equipment Intelligence Development Server"
echo "=================================================="

# Kill any existing processes on port 3001
echo "🔧 Cleaning up port 3001..."
lsof -ti:3001 | xargs kill -9 2>/dev/null || echo "No processes found on port 3001"

# Wait a moment for cleanup
sleep 2

# Navigate to web directory
cd "$(dirname "$0")/../web"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server on port 3001
echo "🌐 Starting Next.js development server on port 3001..."
echo "📍 Frontend will be available at: http://localhost:3001"
echo "🔗 API URL: $(grep NEXT_PUBLIC_API_URL .env.local | cut -d'=' -f2)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

PORT=3001 npm run dev

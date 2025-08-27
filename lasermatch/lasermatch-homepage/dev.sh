#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Kill any existing process on port 3005
echo "🔴 Stopping any existing process on port 3005..."
lsof -ti:3005 | xargs kill -9 2>/dev/null || echo "No process found on port 3005"

# Wait a moment for the port to be freed
sleep 1

# Start the Vite dev server on port 3005
echo "🟢 Starting LaserMatch.io homepage on port 3005..."
npm run dev -- --port 3005

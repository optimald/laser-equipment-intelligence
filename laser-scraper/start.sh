#!/bin/bash
set -e

echo "Starting Laser Equipment Intelligence API..."

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the API
echo "Starting uvicorn server..."
exec uvicorn api.main:app --host 0.0.0.0 --port $PORT

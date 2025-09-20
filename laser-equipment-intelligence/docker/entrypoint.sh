#!/bin/bash

# Laser Equipment Intelligence Platform Entrypoint

set -e

echo "Starting Laser Equipment Intelligence Platform..."

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h postgres -p 5432 -U laser_user; do
    sleep 1
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h redis -p 6379 ping; do
    sleep 1
done
echo "Redis is ready!"

# Run database migrations
echo "Running database migrations..."
python -m laser_intelligence.migrate

# Start Scrapyd daemon
echo "Starting Scrapyd daemon..."
scrapyd &

# Wait for Scrapyd to start
sleep 5

# Deploy spiders
echo "Deploying spiders..."
scrapyd-deploy

# Start monitoring
echo "Starting monitoring..."
python -m laser_intelligence.monitor &

# Keep container running
echo "Platform is ready!"
tail -f /dev/null

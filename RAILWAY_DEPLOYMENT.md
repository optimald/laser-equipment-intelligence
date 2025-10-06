# Railway Deployment Guide

## Architecture Overview

This system uses Railway for:
1. **API Server**: FastAPI server with PostgreSQL database
2. **Worker**: Periodic scraper to keep data updated
3. **Database**: PostgreSQL for persistent data storage

## Deployment Steps

### 1. Deploy API Server
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy API server
railway up --service api-server
```

### 2. Deploy Worker
```bash
# Deploy worker service
railway up --service worker --config railway_worker.json
```

### 3. Set Environment Variables
In Railway dashboard, set:
- `DATABASE_URL`: PostgreSQL connection string
- `PYTHONPATH`: "."

### 4. Update Frontend
Update `NEXT_PUBLIC_API_URL` to point to Railway API URL:
```
NEXT_PUBLIC_API_URL=https://your-railway-api-url.railway.app
```

## Services

### API Server (`railway.json`)
- **Purpose**: Serves LaserMatch data via REST API
- **Health Check**: `/health`
- **Database**: PostgreSQL with persistent storage
- **CORS**: Configured for frontend access

### Worker (`railway_worker.json`)
- **Purpose**: Periodic data updates from LaserMatch.io
- **Schedule**: Runs every 6 hours (configurable)
- **Tasks**: 
  - Scrape LaserMatch data
  - Update database
  - Clean up old data

## Database Schema

### `lasermatch_items`
- Primary table for laser equipment data
- Includes: title, brand, model, condition, price, location, etc.
- Indexed for performance

### `notes`
- User notes for equipment items
- Linked to `lasermatch_items` via foreign key

### `sources`
- Alternative sources for equipment
- Contact information and pricing

### `spider_urls`
- URLs discovered by spiders
- Status tracking for follow-up

## Monitoring

- **API Health**: `https://your-api.railway.app/health`
- **Database Status**: `https://your-api.railway.app/db-test`
- **Worker Logs**: Available in Railway dashboard

## Benefits

1. **Reliability**: Database persists data between deployments
2. **Performance**: Indexed database queries
3. **Scalability**: Railway handles scaling automatically
4. **Monitoring**: Built-in logging and health checks
5. **Updates**: Worker keeps data fresh automatically

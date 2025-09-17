# Laser Equipment Intelligence Platform - Deployment Guide

## Quick Start

### 1. Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+
- Tesseract OCR (for PDF processing)

### 2. Environment Setup
```bash
# Clone and navigate to project
cd laser-equipment-intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install Tesseract OCR (macOS)
brew install tesseract

# Install Tesseract OCR (Ubuntu)
sudo apt-get install tesseract-ocr

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/laser_intelligence
REDIS_URL=redis://localhost:6379/0
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### 4. Database Setup
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Initialize database
psql $DATABASE_URL -f docker/init.sql

# Run migrations (if any)
python scripts/migrate.py
```

### 5. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up -d scrapyd postgres redis prometheus grafana
```

### 6. Verify Deployment
```bash
# Check service status
docker-compose ps

# Test API endpoints
curl http://localhost:5000/api/v1/health

# Check Scrapyd web interface
open http://localhost:6800

# Check Grafana dashboards
open http://localhost:3000 (admin/admin)
```

## Production Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
```bash
# Launch t3.large instance (2 vCPU, 8GB RAM)
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=laser-intelligence}]'
```

#### 2. Configure Instance
```bash
# Connect to instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python 3.9
sudo yum install -y python39 python39-pip

# Install Tesseract
sudo yum install -y tesseract
```

#### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/your-org/laser-equipment-intelligence.git
cd laser-equipment-intelligence

# Configure environment
cp .env.example .env
nano .env

# Start services
docker-compose up -d
```

#### 4. Configure Load Balancer
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name laser-intelligence-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
  --security-groups sg-xxxxxxxxx

# Create target group
aws elbv2 create-target-group \
  --name laser-intelligence-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-xxxxxxxxx \
  --target-type instance

# Register targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/laser-intelligence-tg/xxxxxxxxx \
  --targets Id=i-xxxxxxxxx
```

### Kubernetes Deployment

#### 1. Create Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: laser-intelligence
```

#### 2. Deploy PostgreSQL
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: laser-intelligence
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: laser-intelligence
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: laser_intelligence
        - name: POSTGRES_USER
          value: laser_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

#### 3. Deploy Scrapyd
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scrapyd
  namespace: laser-intelligence
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scrapyd
  template:
    metadata:
      labels:
        app: scrapyd
    spec:
      containers:
      - name: scrapyd
        image: laser-intelligence:latest
        ports:
        - containerPort: 6800
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
```

## Monitoring & Maintenance

### Health Checks
```bash
# Check service health
curl http://localhost:5000/api/v1/health

# Check database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Check Redis connectivity
redis-cli ping

# Check Scrapyd status
curl http://localhost:6800/daemonstatus.json
```

### Log Monitoring
```bash
# View application logs
docker-compose logs -f scrapyd

# View specific spider logs
docker-compose exec scrapyd tail -f /var/log/scrapyd/spider.log

# View system logs
journalctl -u docker -f
```

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity"

# Check Redis memory usage
redis-cli info memory
```

### Backup & Recovery
```bash
# Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup Redis data
redis-cli --rdb backup_$(date +%Y%m%d_%H%M%S).rdb

# Restore database
psql $DATABASE_URL < backup_20240101_120000.sql

# Restore Redis data
redis-cli --pipe < backup_20240101_120000.rdb
```

## Troubleshooting

### Common Issues

#### 1. Spider Not Starting
```bash
# Check spider syntax
scrapy check spider_name

# Check dependencies
pip list | grep scrapy

# Check logs
docker-compose logs scrapyd
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT version()"
```

#### 3. Proxy Issues
```bash
# Check proxy configuration
curl -x http://proxy:port http://httpbin.org/ip

# Test proxy rotation
python scripts/test_proxies.py
```

#### 4. CAPTCHA Issues
```bash
# Check 2Captcha balance
python scripts/check_captcha_balance.py

# Test CAPTCHA solving
python scripts/test_captcha_solver.py
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_listings_brand_model ON listings(brand, model);
CREATE INDEX CONCURRENTLY idx_listings_score ON listings(score_overall);
CREATE INDEX CONCURRENTLY idx_listings_discovered_at ON listings(discovered_at);

-- Analyze table statistics
ANALYZE listings;
```

#### 2. Redis Optimization
```bash
# Configure Redis for better performance
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

#### 3. Scrapy Optimization
```python
# Optimize Scrapy settings
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
```

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use secrets management for production
- Rotate API keys regularly

### 2. Database Security
- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular security updates

### 3. Proxy Security
- Use reputable proxy providers
- Rotate proxy credentials
- Monitor proxy usage
- Implement rate limiting

### 4. API Security
- Implement authentication
- Use HTTPS in production
- Rate limit API endpoints
- Monitor for abuse

## Scaling

### Horizontal Scaling
```bash
# Scale Scrapyd instances
docker-compose up -d --scale scrapyd=5

# Scale with Kubernetes
kubectl scale deployment scrapyd --replicas=5
```

### Vertical Scaling
```bash
# Increase memory limits
docker-compose up -d --scale scrapyd=3 -e MEMORY_LIMIT=4g

# Increase CPU limits
docker-compose up -d --scale scrapyd=3 -e CPU_LIMIT=2
```

### Load Balancing
```bash
# Configure nginx load balancer
upstream scrapyd_backend {
    server scrapyd1:6800;
    server scrapyd2:6800;
    server scrapyd3:6800;
}

server {
    listen 80;
    location / {
        proxy_pass http://scrapyd_backend;
    }
}
```

## Maintenance Schedule

### Daily
- Monitor system health
- Check error logs
- Verify spider performance
- Review alert notifications

### Weekly
- Update dependencies
- Review compliance reports
- Analyze performance metrics
- Backup data

### Monthly
- Security updates
- Performance optimization
- Capacity planning
- Disaster recovery testing

### Quarterly
- Full system audit
- Compliance review
- Performance benchmarking
- Architecture review

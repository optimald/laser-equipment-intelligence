#!/bin/bash

# Laser Equipment Intelligence Platform Deployment Script

set -e

echo "🚀 Starting Laser Equipment Intelligence Platform Deployment..."

# Configuration
PROJECT_NAME="laser-intelligence"
DOCKER_COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        log_warning "Please edit .env file with your configuration before continuing."
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    log_success "Prerequisites check completed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build main application image
    docker build -t laser-intelligence:latest .
    
    log_success "Docker images built successfully"
}

# Start services
start_services() {
    log_info "Starting services with Docker Compose..."
    
    # Start all services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    log_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    until docker exec laser-postgres pg_isready -U laser_user -d laser_intelligence; do
        sleep 2
    done
    log_success "PostgreSQL is ready"
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    until docker exec laser-redis redis-cli ping; do
        sleep 2
    done
    log_success "Redis is ready"
    
    # Wait for Scrapyd
    log_info "Waiting for Scrapyd..."
    until curl -f http://localhost:6800/daemonstatus.json; do
        sleep 2
    done
    log_success "Scrapyd is ready"
    
    # Wait for Prometheus
    log_info "Waiting for Prometheus..."
    until curl -f http://localhost:9090/-/healthy; do
        sleep 2
    done
    log_success "Prometheus is ready"
    
    # Wait for Grafana
    log_info "Waiting for Grafana..."
    until curl -f http://localhost:3000/api/health; do
        sleep 2
    done
    log_success "Grafana is ready"
}

# Deploy spiders
deploy_spiders() {
    log_info "Deploying spiders to Scrapyd..."
    
    # Deploy all spiders
    docker exec laser-scrapyd scrapyd-deploy
    
    log_success "Spiders deployed successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Run migrations
    docker exec laser-scrapyd python -m laser_intelligence.migrate
    
    log_success "Database migrations completed"
}

# Start initial spider jobs
start_spider_jobs() {
    log_info "Starting initial spider jobs..."
    
    # Start DOTmed spider
    curl -X POST http://localhost:6800/schedule.json \
        -d project=$PROJECT_NAME \
        -d spider=dotmed_auctions
    
    # Start eBay spider
    curl -X POST http://localhost:6800/schedule.json \
        -d project=$PROJECT_NAME \
        -d spider=ebay_laser
    
    # Start GovDeals spider
    curl -X POST http://localhost:6800/schedule.json \
        -d project=$PROJECT_NAME \
        -d spider=govdeals
    
    log_success "Initial spider jobs started"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Import Grafana dashboards
    # This would typically involve API calls to Grafana
    log_info "Grafana dashboards will be available at http://localhost:3000"
    log_info "Default credentials: admin/admin"
    
    log_success "Monitoring setup completed"
}

# Display status
display_status() {
    log_info "Deployment Status:"
    echo ""
    echo "🌐 Web Interfaces:"
    echo "  - Scrapyd Web UI: http://localhost:6800"
    echo "  - Grafana Dashboards: http://localhost:3000 (admin/admin)"
    echo "  - Prometheus Metrics: http://localhost:9090"
    echo ""
    echo "📊 Services Status:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    echo ""
    echo "🕷️ Active Spider Jobs:"
    curl -s http://localhost:6800/listjobs.json | jq '.running[] | {spider: .spider, start_time: .start_time}' 2>/dev/null || echo "No active jobs"
    echo ""
    echo "📈 Recent Listings:"
    docker exec laser-postgres psql -U laser_user -d laser_intelligence -c "SELECT COUNT(*) as total_listings FROM listings;" 2>/dev/null || echo "Database not accessible"
    echo ""
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check all services
    services=("laser-scrapyd" "laser-postgres" "laser-redis" "laser-prometheus" "laser-grafana")
    
    for service in "${services[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$service"; then
            log_success "$service is running"
        else
            log_error "$service is not running"
        fi
    done
    
    # Check Scrapyd API
    if curl -f http://localhost:6800/daemonstatus.json > /dev/null 2>&1; then
        log_success "Scrapyd API is accessible"
    else
        log_error "Scrapyd API is not accessible"
    fi
    
    # Check database connection
    if docker exec laser-postgres pg_isready -U laser_user -d laser_intelligence > /dev/null 2>&1; then
        log_success "Database connection is healthy"
    else
        log_error "Database connection failed"
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Add cleanup logic here if needed
}

# Main deployment function
main() {
    log_info "Starting Laser Equipment Intelligence Platform deployment..."
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    build_images
    start_services
    wait_for_services
    run_migrations
    deploy_spiders
    start_spider_jobs
    setup_monitoring
    health_check
    display_status
    
    log_success "🎉 Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Monitor spider jobs at http://localhost:6800"
    echo "2. View dashboards at http://localhost:3000"
    echo "3. Check logs with: docker-compose logs -f"
    echo "4. Stop services with: docker-compose down"
    echo ""
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        log_success "Services restarted"
        ;;
    "status")
        display_status
        ;;
    "health")
        health_check
        ;;
    "logs")
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
        ;;
    "update")
        log_info "Updating deployment..."
        docker-compose -f $DOCKER_COMPOSE_FILE pull
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        deploy_spiders
        log_success "Deployment updated"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|status|health|logs|update}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show deployment status"
        echo "  health   - Perform health check"
        echo "  logs     - Show service logs"
        echo "  update   - Update deployment"
        exit 1
        ;;
esac

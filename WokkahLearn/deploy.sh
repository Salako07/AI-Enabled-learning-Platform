#!/bin/bash

# CodeMaster Learning Platform Deployment Script

set -e  # Exit on any error

echo "íº€ Starting CodeMaster Learning Platform Deployment..."

# Configuration
PROJECT_NAME="codemaster_platform"
DOMAIN="${DOMAIN:-localhost}"
ENVIRONMENT="${ENVIRONMENT:-production}"
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-docker-compose.yml}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    log "Prerequisites check passed âœ…"
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        warn ".env file not found. Creating from template..."
        cp .env.example .env 2>/dev/null || {
            warn "No .env.example found. Please create .env manually."
            return
        }
    fi
    
    # Generate secret key if not set
    if ! grep -q "SECRET_KEY=django-insecure" .env; then
        SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        log "Generated new SECRET_KEY"
    fi
    
    log "Environment setup complete âœ…"
}

# Build and start services
deploy_services() {
    log "Building and starting services..."
    
    # Build images
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    # Start services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    log "Services started âœ…"
}

# Wait for database
wait_for_db() {
    log "Waiting for database to be ready..."
    
    timeout=60
    while ! docker-compose exec db pg_isready -h localhost -p 5432 > /dev/null 2>&1; do
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            error "Database failed to start within 60 seconds"
        fi
        sleep 1
    done
    
    log "Database is ready âœ…"
}

# Run migrations and setup
setup_database() {
    log "Setting up database..."
    
    # Run migrations
    docker-compose exec web python manage.py migrate_platform
    
    # Setup initial data
    docker-compose exec web python manage.py setup_platform
    
    # Create sample content for development
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose exec web python manage.py create_sample_content
    fi
    
    log "Database setup complete âœ…"
}

# Setup SSL (for production)
setup_ssl() {
    if [ "$ENVIRONMENT" = "production" ] && [ "$DOMAIN" != "localhost" ]; then
        log "Setting up SSL certificate..."
        
        # This would integrate with Let's Encrypt
        # docker-compose exec nginx certbot --nginx -d $DOMAIN
        
        warn "SSL setup skipped. Configure manually for production."
    fi
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check web service
    if docker-compose exec web python manage.py check > /dev/null 2>&1; then
        log "Django health check passed âœ…"
    else
        error "Django health check failed"
    fi
    
    # Check if web server is responding
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        log "Web server health check passed âœ…"
    else
        warn "Web server not responding on port 8000"
    fi
}

# Show deployment summary
show_summary() {
    log "Deployment Summary"
    echo "===================="
    echo "Project: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "Domain: $DOMAIN"
    echo "Status: $(docker-compose ps --services --filter status=running | wc -l) services running"
    echo ""
    echo "Services:"
    docker-compose ps
    echo ""
    echo "Access URLs:"
    echo "- Web Application: http://$DOMAIN:8000"
    echo "- API Documentation: http://$DOMAIN:8000/api/docs/"
    echo "- Admin Panel: http://$DOMAIN:8000/admin/"
    echo ""
    echo "Logs: docker-compose logs -f"
    echo "Stop: docker-compose down"
    echo ""
    log "Deployment completed successfully! í¾‰"
}

# Main deployment flow
main() {
    log "Starting deployment for environment: $ENVIRONMENT"
    
    check_prerequisites
    setup_environment
    deploy_services
    wait_for_db
    setup_database
    setup_ssl
    health_check
    show_summary
}

# Run main function
main "$@"

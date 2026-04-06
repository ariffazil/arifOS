#!/bin/bash
# =============================================================================
# ArifOS MCP Server - SSL Certificate Initialization Script
# =============================================================================
# This script initializes SSL certificates using Let's Encrypt
# Run this on the VPS server after initial deployment
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${DOMAIN:-arifosmcp.arif-fazil.com}"
EMAIL="${ADMIN_EMAIL:-admin@arif-fazil.com}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
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
    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if domain is set
    if [[ "$DOMAIN" == "arifosmcp.arif-fazil.com" && -z "$ADMIN_EMAIL" ]]; then
        log_warn "Using default domain. Make sure to update DOMAIN and ADMIN_EMAIL in .env"
    fi
    
    log_info "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p nginx/ssl
    mkdir -p nginx/snippets
    mkdir -p logs/nginx
    mkdir -p certbot-data
    mkdir -p certbot-www
    
    log_info "Directories created"
}

# Start nginx with temporary config for certbot challenge
start_temp_nginx() {
    log_info "Starting Nginx with temporary configuration..."
    
    # Create temporary nginx config for certbot
    cat > nginx/conf.d/temp-certbot.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 "Certbot challenge server";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Start nginx
    docker compose -f "$COMPOSE_FILE" up -d nginx
    
    # Wait for nginx to be ready
    sleep 5
    
    log_info "Nginx started with temporary configuration"
}

# Obtain SSL certificate
obtain_certificate() {
    log_info "Obtaining SSL certificate for $DOMAIN..."
    
    # Run certbot
    docker run -it --rm \
        -v "$(pwd)/certbot-data:/etc/letsencrypt" \
        -v "$(pwd)/certbot-www:/var/www/certbot" \
        --network host \
        certbot/certbot certonly \
        --standalone \
        --agree-tos \
        --no-eff-email \
        --email "$EMAIL" \
        -d "$DOMAIN"
    
    if [[ $? -eq 0 ]]; then
        log_info "SSL certificate obtained successfully!"
    else
        log_error "Failed to obtain SSL certificate"
        exit 1
    fi
}

# Update nginx configuration
update_nginx_config() {
    log_info "Updating Nginx configuration..."
    
    # Remove temporary config
    rm -f nginx/conf.d/temp-certbot.conf
    
    # Restart nginx with full configuration
    docker compose -f "$COMPOSE_FILE" restart nginx
    
    log_info "Nginx configuration updated"
}

# Setup auto-renewal
setup_auto_renewal() {
    log_info "Setting up auto-renewal..."
    
    # Add cron job for certificate renewal
    CRON_JOB="0 3 * * * cd $(pwd) && docker compose -f $COMPOSE_FILE run --rm certbot renew --quiet && docker compose -f $COMPOSE_FILE restart nginx"
    
    # Check if cron job already exists
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        log_info "Auto-renewal cron job added"
    else
        log_info "Auto-renewal cron job already exists"
    fi
}

# Verify SSL certificate
verify_certificate() {
    log_info "Verifying SSL certificate..."
    
    # Check certificate expiry
    CERT_PATH="certbot-data/live/$DOMAIN/fullchain.pem"
    
    if [[ -f "$CERT_PATH" ]]; then
        EXPIRY=$(openssl x509 -in "$CERT_PATH" -noout -dates | grep notAfter | cut -d= -f2)
        log_info "Certificate expires: $EXPIRY"
        
        # Test HTTPS connection
        if curl -sf "https://$DOMAIN" > /dev/null 2>&1; then
            log_info "HTTPS connection test successful!"
        else
            log_warn "HTTPS connection test failed - may need a few minutes to propagate"
        fi
    else
        log_error "Certificate file not found at $CERT_PATH"
        exit 1
    fi
}

# Main function
main() {
    log_info "Starting SSL certificate initialization for $DOMAIN"
    
    check_root
    check_prerequisites
    create_directories
    start_temp_nginx
    obtain_certificate
    update_nginx_config
    setup_auto_renewal
    verify_certificate
    
    log_info "SSL certificate initialization completed!"
    log_info "Your MCP server should now be accessible at https://$DOMAIN"
}

# Run main function
main "$@"

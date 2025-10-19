#!/bin/bash

# =============================================================================
# MINDSURVE PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="mindsurve"
APP_DIR="/opt/mindsurve"
SERVICE_USER="www-data"
SERVICE_GROUP="www-data"
PYTHON_VERSION="3.9"

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

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root for security reasons"
        exit 1
    fi
}

check_dependencies() {
    log_info "Checking system dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi
    
    # Check MongoDB
    if ! command -v mongod &> /dev/null; then
        log_warning "MongoDB is not installed. Please install MongoDB 6.0+"
    fi
    
    log_success "Dependencies check completed"
}

create_directories() {
    log_info "Creating application directories..."
    
    sudo mkdir -p $APP_DIR
    sudo mkdir -p $APP_DIR/logs
    sudo mkdir -p $APP_DIR/local_uploads
    sudo mkdir -p $APP_DIR/uploads
    sudo mkdir -p $APP_DIR/venv
    
    log_success "Directories created"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    cd $APP_DIR
    sudo python3 -m venv venv
    sudo chown -R $SERVICE_USER:$SERVICE_GROUP venv
    
    # Activate virtual environment and install dependencies
    sudo -u $SERVICE_USER bash -c "source venv/bin/activate && pip install --upgrade pip"
    sudo -u $SERVICE_USER bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    log_success "Python environment setup completed"
}

copy_application_files() {
    log_info "Copying application files..."
    
    # Copy all application files
    sudo cp -r . $APP_DIR/
    
    # Set proper ownership
    sudo chown -R $SERVICE_USER:$SERVICE_GROUP $APP_DIR
    
    # Set proper permissions
    sudo chmod -R 755 $APP_DIR
    sudo chmod 644 $APP_DIR/.env
    sudo chmod +x $APP_DIR/start_production.py
    
    log_success "Application files copied"
}

setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f "$APP_DIR/.env" ]; then
        log_warning ".env file not found. Creating from template..."
        sudo cp $APP_DIR/env.example $APP_DIR/.env
        sudo chown $SERVICE_USER:$SERVICE_GROUP $APP_DIR/.env
        log_warning "Please edit $APP_DIR/.env with your production settings"
    fi
    
    log_success "Environment configuration setup completed"
}

setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    # Copy service file
    sudo cp mindsurve.service /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable mindsurve
    
    log_success "Systemd service setup completed"
}

setup_nginx() {
    log_info "Setting up Nginx configuration..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/mindsurve > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:55000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /health {
        proxy_pass http://127.0.0.1:55000/health;
        access_log off;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/mindsurve /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    log_success "Nginx configuration setup completed"
}

setup_logrotate() {
    log_info "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/mindsurve > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
    postrotate
        systemctl reload mindsurve
    endscript
}
EOF
    
    log_success "Log rotation setup completed"
}

start_services() {
    log_info "Starting services..."
    
    # Start MongoDB if not running
    if ! systemctl is-active --quiet mongod; then
        sudo systemctl start mongod
        sudo systemctl enable mongod
    fi
    
    # Start Mindsurve
    sudo systemctl start mindsurve
    
    # Check status
    sleep 5
    if systemctl is-active --quiet mindsurve; then
        log_success "Mindsurve service started successfully"
    else
        log_error "Failed to start Mindsurve service"
        sudo journalctl -u mindsurve --no-pager -l
        exit 1
    fi
}

show_status() {
    log_info "Deployment Status:"
    echo "=================="
    echo "Service Status: $(systemctl is-active mindsurve)"
    echo "Service Enabled: $(systemctl is-enabled mindsurve)"
    echo "Application URL: http://localhost"
    echo "Health Check: http://localhost/health"
    echo "Logs: sudo journalctl -u mindsurve -f"
    echo "Config: $APP_DIR/.env"
    echo "=================="
}

main() {
    log_info "Starting Mindsurve production deployment..."
    
    check_root
    check_dependencies
    create_directories
    setup_python_environment
    copy_application_files
    setup_environment
    setup_systemd_service
    setup_nginx
    setup_logrotate
    start_services
    show_status
    
    log_success "Deployment completed successfully!"
    log_warning "Don't forget to:"
    log_warning "1. Edit $APP_DIR/.env with your production settings"
    log_warning "2. Configure SSL/TLS certificates for HTTPS"
    log_warning "3. Set up firewall rules"
    log_warning "4. Configure monitoring and backups"
}

# Run main function
main "$@"

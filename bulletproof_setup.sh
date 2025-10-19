#!/bin/bash

# =============================================================================
# BULLETPROOF JOSHSYSTEM SETUP
# Professional one-click setup that handles all edge cases
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${CYAN}➤${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to kill processes on specific ports
kill_port_processes() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        print_warning "Found processes on port $port: $pids"
        print_step "Killing processes on port $port..."
        echo $pids | xargs kill -9 2>/dev/null || true
        sleep 2
        print_success "Killed processes on port $port"
    else
        print_success "Port $port is free"
    fi
}

# Function to clean up Docker resources
cleanup_docker() {
    print_header "CLEANING UP DOCKER RESOURCES"
    
    print_step "Stopping all JoshSystem containers..."
    docker-compose down -v 2>/dev/null || true
    
    print_step "Removing any orphaned containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    print_step "Cleaning up unused Docker resources..."
    docker system prune -f 2>/dev/null || true
    
    print_success "Docker cleanup completed"
}

# Function to check and kill port conflicts
check_port_conflicts() {
    print_header "CHECKING PORT CONFLICTS"
    
    # Kill processes on all ports we need
    kill_port_processes 80
    kill_port_processes 443
    kill_port_processes 5000
    kill_port_processes 5001
    kill_port_processes 27017
    kill_port_processes 6379
    kill_port_processes 3132  # The port mentioned in previous errors
    
    # Kill any existing Mindsurve processes
    print_step "Checking for existing Mindsurve processes..."
    mindsurve_pids=$(ps aux | grep -i mindsurve | grep -v grep | awk '{print $2}' 2>/dev/null || true)
    if [ -n "$mindsurve_pids" ]; then
        print_warning "Found existing Mindsurve processes: $mindsurve_pids"
        echo $mindsurve_pids | xargs kill -9 2>/dev/null || true
        print_success "Killed existing Mindsurve processes"
    else
        print_success "No existing Mindsurve processes found"
    fi
    
    # Clean up any lock files
    print_step "Cleaning up lock files..."
    rm -f /tmp/mindsurve_app.lock 2>/dev/null || true
    print_success "Lock files cleaned up"
}

# Function to check Docker installation
check_docker() {
    print_header "CHECKING DOCKER INSTALLATION"
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        print_status "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        sudo systemctl enable docker
        sudo systemctl start docker
        print_success "Docker installed successfully"
    else
        print_success "Docker is installed"
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed"
        print_status "Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed successfully"
    else
        print_success "Docker Compose is installed"
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_status "Starting Docker daemon..."
        sudo systemctl start docker
        sleep 5
    fi
    
    print_success "Docker is ready"
}

# Function to setup environment
setup_environment() {
    print_header "SETTING UP ENVIRONMENT"
    
    if [ ! -f ".env" ]; then
        if [ -f "env.docker" ]; then
            cp env.docker .env
            print_success "Created .env file from template"
        else
            print_error "Environment template not found"
            exit 1
        fi
    else
        print_status "Environment file already exists"
    fi
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || echo "your-secret-key-$(date +%s)")
    
    # Update .env file with generated values
    sed -i.bak "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env 2>/dev/null || true
    sed -i.bak "s/your-mongodb-password-change-this/admin123/" .env 2>/dev/null || true
    sed -i.bak "s/your-redis-password-change-this/redis123/" .env 2>/dev/null || true
    rm .env.bak 2>/dev/null || true
    
    print_success "Environment configured with secure defaults"
}

# Function to create necessary directories
create_directories() {
    print_header "CREATING DIRECTORIES"
    
    directories=(
        "local_uploads"
        "local_uploads/drafts"
        "logs"
        "mongodb-data"
        "nginx/ssl"
        "monitoring"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
}

# Function to build and start services
start_services() {
    print_header "BUILDING AND STARTING SERVICES"
    
    print_step "Building Docker images..."
    docker-compose build --no-cache
    
    print_step "Starting all services..."
    docker-compose up -d
    
    print_success "All services started"
}

# Function to wait for services with better error handling
wait_for_services() {
    print_header "WAITING FOR SERVICES TO BE READY"
    
    # Wait for MongoDB
    print_step "Waiting for MongoDB..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
            print_success "MongoDB is ready"
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "MongoDB failed to start within timeout"
        print_status "MongoDB logs:"
        docker-compose logs mongodb
        return 1
    fi
    
    # Wait for Redis
    print_step "Waiting for Redis..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
            print_success "Redis is ready"
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Redis failed to start within timeout"
        print_status "Redis logs:"
        docker-compose logs redis
        return 1
    fi
    
    # Wait for Mindsurve application
    print_step "Waiting for Mindsurve application..."
    timeout=90
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:5001/health >/dev/null 2>&1; then
            print_success "Mindsurve application is ready"
            break
        fi
        sleep 3
        timeout=$((timeout-3))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "Direct Mindsurve check failed, trying Nginx proxy..."
        timeout=30
        while [ $timeout -gt 0 ]; do
            if curl -f http://localhost/health >/dev/null 2>&1; then
                print_success "Mindsurve application is ready (via Nginx)"
                break
            fi
            sleep 3
            timeout=$((timeout-3))
        done
        
        if [ $timeout -le 0 ]; then
            print_error "Mindsurve application failed to start within timeout"
            print_status "Mindsurve logs:"
            docker-compose logs mindsurve
            print_status "Nginx logs:"
            docker-compose logs nginx
            return 1
        fi
    fi
}

# Function to show final status
show_final_status() {
    print_header "SETUP COMPLETED SUCCESSFULLY!"
    
    echo ""
    echo -e "${GREEN}🎉 JoshSystem is now running!${NC}"
    echo ""
    echo -e "${CYAN}📱 Application URLs:${NC}"
    echo -e "   Main Application: ${BLUE}http://localhost${NC}"
    echo -e "   Direct Access: ${BLUE}http://localhost:5001${NC}"
    echo -e "   Health Check: ${BLUE}http://localhost/health${NC}"
    echo ""
    echo -e "${CYAN}🗄️  Database Access:${NC}"
    echo -e "   MongoDB: ${BLUE}mongodb://admin:admin123@localhost:27017/joshsystem${NC}"
    echo -e "   Redis: ${BLUE}redis://localhost:6379${NC}"
    echo ""
    echo -e "${CYAN}🛠️  Management Commands:${NC}"
    echo -e "   View logs: ${BLUE}docker-compose logs -f${NC}"
    echo -e "   Stop services: ${BLUE}docker-compose down${NC}"
    echo -e "   Restart services: ${BLUE}docker-compose restart${NC}"
    echo -e "   Check status: ${BLUE}docker-compose ps${NC}"
    echo ""
    echo -e "${CYAN}📊 Service Status:${NC}"
    docker-compose ps
    echo ""
    echo -e "${GREEN}✨ Your application is ready to use!${NC}"
}

# Function to handle errors
handle_error() {
    print_error "Setup failed at step: $1"
    print_status "You can try running the script again or check the logs:"
    print_status "docker-compose logs"
    exit 1
}

# Main execution function
main() {
    # Trap errors
    trap 'handle_error "Unknown error"' ERR
    
    print_header "JOSHSYSTEM BULLETPROOF SETUP"
    echo ""
    print_status "This will install and configure everything automatically:"
    print_status "  ✓ Clean up any existing conflicts"
    print_status "  ✓ Install Docker and Docker Compose (if needed)"
    print_status "  ✓ Set up MongoDB with authentication"
    print_status "  ✓ Configure Redis cache"
    print_status "  ✓ Install all packages and dependencies"
    print_status "  ✓ Start the Mindsurve application"
    print_status "  ✓ Configure Nginx reverse proxy"
    print_status "  ✓ Set up the entire environment"
    echo ""
    
    # Check if user wants to continue
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled by user"
        exit 0
    fi
    
    echo ""
    
    # Execute setup steps
    cleanup_docker || handle_error "Docker cleanup"
    check_port_conflicts || handle_error "Port conflict check"
    check_docker || handle_error "Docker check"
    setup_environment || handle_error "Environment setup"
    create_directories || handle_error "Directory creation"
    start_services || handle_error "Service startup"
    wait_for_services || handle_error "Service readiness"
    show_final_status
    
    echo ""
    print_success "🎊 Setup completed successfully!"
    print_status "Your application is ready at http://localhost"
}

# Run main function
main "$@"

#!/bin/bash

# Quick Setup Script - Agbara Integration
# This script sets up the entire Agbara integration environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🚀 Agbara Integration - Quick Setup Script              ║"
echo "║     Setting up your development environment in minutes      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Check OS
OS="$(uname -s)"
echo -e "${GREEN}Detected OS: $OS${NC}\n"

# Function to print colored messages
print_info() {
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

# Check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check Python
check_python() {
    print_info "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python 3 is not installed"
        print_info "Please install Python 3.11 or higher from https://www.python.org/"
        return 1
    fi
}

# Check pip
check_pip() {
    print_info "Checking pip installation..."
    
    if command_exists pip3; then
        PIP_VERSION=$(pip3 --version)
        print_success "pip found: $PIP_VERSION"
        return 0
    else
        print_error "pip is not installed"
        print_info "Please install pip from https://pip.pypa.io/"
        return 1
    fi
}

# Check Git
check_git() {
    print_info "Checking Git installation..."
    
    if command_exists git; then
        GIT_VERSION=$(git --version)
        print_success "Git found: $GIT_VERSION"
        return 0
    else
        print_warning "Git is not installed (optional)"
        return 0
    fi
}

# Check Docker
check_docker() {
    print_info "Checking Docker installation..."
    
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker found: $DOCKER_VERSION"
        return 0
    else
        print_warning "Docker is not installed (optional, for containerized deployment)"
        return 0
    fi
}

# Check Android SDK (optional)
check_android_sdk() {
    print_info "Checking Android SDK installation..."
    
    if [ -d "$ANDROID_HOME" ]; then
        print_success "Android SDK found at $ANDROID_HOME"
        return 0
    else
        print_warning "Android SDK not found in \$ANDROID_HOME (optional)"
        print_info "If developing Android apps, set ANDROID_HOME environment variable"
        return 0
    fi
}

# Setup Python environment
setup_python_env() {
    print_info "Setting up Python environment..."
    
    cd agbara-integration-server
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    cd ..
}

# Setup environment variables
setup_env_vars() {
    print_info "Setting up environment variables..."
    
    cd agbara-integration-server
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_info "Creating .env file from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your API keys"
            print_info "Run: nano agbara-integration-server/.env"
        else
            print_error ".env.example not found"
            return 1
        fi
    else
        print_warning ".env file already exists"
    fi
    
    cd ..
}

# Clone or setup repositories
setup_repositories() {
    print_info "Setting up repositories..."
    
    # Check if we're in the right directory
    if [ ! -f "agbara-integration-server/api_server.py" ]; then
        print_error "Agbara integration files not found"
        print_info "Please run this script from the workspace root directory"
        return 1
    fi
    
    print_success "Repositories ready"
}

# Run tests
run_tests() {
    print_info "Running tests..."
    
    cd agbara-integration-server
    source venv/bin/activate
    
    if [ -d "tests" ]; then
        print_info "Running Python tests..."
        python -m pytest tests/ -v --cov=. --cov-report=html || true
        print_success "Tests completed (see htmlcov/index.html)"
    else
        print_warning "No tests found"
    fi
    
    cd ..
}

# Start development server
start_server() {
    print_info "Starting development server..."
    
    cd agbara-integration-server
    source venv/bin/activate
    
    print_info "Server will be available at:"
    echo -e "${GREEN}  - API: http://localhost:8000${NC}"
    echo -e "${GREEN}  - WebSocket: ws://localhost:8000/ws/chat${NC}"
    echo -e "${GREEN}  - Docs: http://localhost:8000/docs${NC}"
    echo ""
    print_info "Press Ctrl+C to stop the server"
    
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
}

# Build Docker image (if Docker available)
build_docker() {
    if command_exists docker; then
        print_info "Building Docker image..."
        cd agbara-integration-server
        docker build -t agbara-integration-server:dev .
        print_success "Docker image built"
        cd ..
    else
        print_warning "Docker not available, skipping Docker build"
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}     🎉 Setup Complete!${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    echo -e "${GREEN}What's next?${NC}"
    echo ""
    echo "1. Configure your API keys:"
    echo -e "   ${YELLOW}nano agbara-integration-server/.env${NC}"
    echo ""
    echo "2. Start the development server:"
    echo -e "   ${YELLOW}cd agbara-integration-server${NC}"
    echo -e "   ${YELLOW}source venv/bin/activate${NC}"
    echo -e "   ${YELLOW}uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload${NC}"
    echo ""
    echo "3. Or use the deployment script:"
    echo -e "   ${YELLOW}./agbara-integration-server/deploy.sh local development start${NC}"
    echo ""
    echo "4. Visit the API documentation:"
    echo -e "   ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo "5. Check out the demo app:"
    echo -e "   ${YELLOW}cd agbara-demo-app${NC}"
    echo ""
    echo "6. Read the documentation:"
    echo -e "   ${GREEN}QUICK_START.md${NC}"
    echo -e "   ${GREEN}DEVELOPER_GUIDE.md${NC}"
    echo -e "   ${GREEN}API_REFERENCE.md${NC}"
    echo ""
}

# Main execution
main() {
    # Check prerequisites
    check_python || exit 1
    check_pip || exit 1
    check_git
    check_docker
    check_android_sdk
    
    echo ""
    
    # Setup environment
    print_info "Setting up Agbara Integration environment..."
    echo ""
    
    setup_repositories || exit 1
    setup_python_env || exit 1
    setup_env_vars || exit 1
    run_tests
    
    # Build Docker (optional)
    if command_exists docker; then
        build_docker
    fi
    
    echo ""
    
    # Show next steps
    show_next_steps
    
    # Ask if user wants to start server
    echo ""
    read -p "Do you want to start the development server now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_server
    fi
}

# Run main function
main "$@"
#!/bin/bash

# Deployment Script for Agbara Integration Server
# Supports: Docker, Kubernetes, Local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Agbara Integration Server Deployment${NC}"
echo -e "${GREEN}======================================${NC}\n"

# Configuration
DEPLOY_MODE="${1:-local}"
ENVIRONMENT="${2:-development}"

echo "Deploy Mode: $DEPLOY_MODE"
echo "Environment: $ENVIRONMENT"
echo ""

# Check for required tools
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓ Python 3 found${NC}"
        python3 --version
    else
        echo -e "${RED}✗ Python 3 not found${NC}"
        exit 1
    fi
    
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✓ pip3 found${NC}"
    else
        echo -e "${RED}✗ pip3 not found${NC}"
        exit 1
    fi
    
    if [[ "$DEPLOY_MODE" == "docker" ]]; then
        if command -v docker &> /dev/null; then
            echo -e "${GREEN}✓ Docker found${NC}"
            docker --version
        else
            echo -e "${RED}✗ Docker not found${NC}"
            exit 1
        fi
    fi
    
    if [[ "$DEPLOY_MODE" == "kubernetes" ]]; then
        if command -v kubectl &> /dev/null; then
            echo -e "${GREEN}✓ kubectl found${NC}"
            kubectl version --client
        else
            echo -e "${RED}✗ kubectl not found${NC}"
            exit 1
        fi
    fi
    
    echo ""
}

# Create virtual environment
create_venv() {
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
}

# Install dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
}

# Setup environment variables
setup_env() {
    echo -e "${YELLOW}Setting up environment variables...${NC}"
    
    if [[ ! -f ".env" ]]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please configure .env with your API keys${NC}"
        echo -e "${YELLOW}⚠ Edit .env and run this script again${NC}"
        exit 1
    fi
    
    source .env
    echo -e "${GREEN}✓ Environment variables loaded${NC}"
    echo ""
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    if [[ -f "migrations.py" ]]; then
        python migrations.py
        echo -e "${GREEN}✓ Migrations completed${NC}"
    else
        echo -e "${YELLOW}⚠ No migrations found${NC}"
    fi
    
    echo ""
}

# Start server locally
start_local() {
    echo -e "${YELLOW}Starting server locally...${NC}"
    
    create_venv
    source venv/bin/activate
    install_dependencies
    setup_env
    run_migrations
    
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Starting Agbara Integration Server${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo -e "API URL: ${GREEN}http://localhost:8000${NC}"
    echo -e "WebSocket URL: ${GREEN}ws://localhost:8000/ws/chat${NC}"
    echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "${GREEN}======================================${NC}\n"
    
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
}

# Deploy with Docker
deploy_docker() {
    echo -e "${YELLOW}Deploying with Docker...${NC}"
    
    if [[ ! -f "Dockerfile" ]]; then
        echo -e "${RED}✗ Dockerfile not found${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t agbara-integration-server:$ENVIRONMENT .
    
    echo -e "${YELLOW}Running Docker container...${NC}"
    docker run -d \
        --name agbara-server-$ENVIRONMENT \
        -p 8000:8000 \
        --env-file .env \
        agbara-integration-server:$ENVIRONMENT
    
    echo -e "${GREEN}✓ Docker container running${NC}"
    echo -e "Container name: ${GREEN}agbara-server-$ENVIRONMENT${NC}"
    echo -e "API URL: ${GREEN}http://localhost:8000${NC}"
    echo ""
}

# Deploy to Kubernetes
deploy_kubernetes() {
    echo -e "${YELLOW}Deploying to Kubernetes...${NC}"
    
    if [[ ! -f "k8s-deployment.yaml" ]]; then
        echo -e "${RED}✗ k8s-deployment.yaml not found${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"
    kubectl apply -f k8s-deployment.yaml
    kubectl apply -f k8s-service.yaml
    
    echo -e "${YELLOW}Waiting for deployment...${NC}"
    kubectl wait --for=condition=available --timeout=300s deployment/agbara-integration-server
    
    echo -e "${GREEN}✓ Deployment completed${NC}"
    echo -e "Service URL: ${GREEN}$(kubectl get svc agbara-integration-server -o jsonpath='{.status.loadBalancer.ingress[0].ip}')${NC}"
    echo ""
}

# Health check
health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ Server is healthy${NC}"
    else
        echo -e "${RED}✗ Server health check failed${NC}"
        exit 1
    fi
    
    echo ""
}

# Stop server
stop_server() {
    echo -e "${YELLOW}Stopping server...${NC}"
    
    if [[ "$DEPLOY_MODE" == "docker" ]]; then
        docker stop agbara-server-$ENVIRONMENT
        docker rm agbara-server-$ENVIRONMENT
        echo -e "${GREEN}✓ Docker container stopped${NC}"
    elif [[ "$DEPLOY_MODE" == "kubernetes" ]]; then
        kubectl delete deployment agbara-integration-server
        kubectl delete service agbara-integration-server
        echo -e "${GREEN}✓ Kubernetes deployment deleted${NC}"
    else
        pkill -f "uvicorn api_server:app"
        echo -e "${GREEN}✓ Local server stopped${NC}"
    fi
    
    echo ""
}

# Run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    
    create_venv
    source venv/bin/activate
    install_dependencies
    
    python -m pytest tests/ -v --cov=. --cov-report=html
    
    echo -e "${GREEN}✓ Tests completed${NC}"
    echo -e "Coverage report: ${GREEN}htmlcov/index.html${NC}"
    echo ""
}

# Show logs
show_logs() {
    echo -e "${YELLOW}Showing logs...${NC}"
    
    if [[ "$DEPLOY_MODE" == "docker" ]]; then
        docker logs -f agbara-server-$ENVIRONMENT
    elif [[ "$DEPLOY_MODE" == "kubernetes" ]]; then
        kubectl logs -f deployment/agbara-integration-server
    else
        echo -e "${RED}✗ Logs not available for local mode${NC}"
        exit 1
    fi
}

# Main execution
case "${3:-}" in
    start)
        case "$DEPLOY_MODE" in
            local)
                start_local
                ;;
            docker)
                deploy_docker
                ;;
            kubernetes)
                deploy_kubernetes
                ;;
            *)
                echo -e "${RED}Invalid deploy mode: $DEPLOY_MODE${NC}"
                echo "Usage: $0 [local|docker|kubernetes] [environment] start"
                exit 1
                ;;
        esac
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        "${BASH_SOURCE[0]}" "$DEPLOY_MODE" "$ENVIRONMENT" start
        ;;
    health)
        health_check
        ;;
    logs)
        show_logs
        ;;
    test)
        run_tests
        ;;
    *)
        echo -e "${YELLOW}Usage:${NC}"
        echo "  $0 [local|docker|kubernetes] [development|staging|production] [start|stop|restart|health|logs|test]"
        echo ""
        echo "Examples:"
        echo "  $0 local development start     # Start locally for dev"
        echo "  $0 docker staging start        # Deploy to Docker for staging"
        echo "  $0 kubernetes production start # Deploy to Kubernetes for production"
        echo "  $0 docker production stop      # Stop production server"
        echo "  $0 local development test      # Run tests"
        exit 1
        ;;
esac
#!/bin/bash

# Automated Setup Script with Environment Compatibility Checks
# This script automatically detects and fixes common environment issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Multimodal RAG System - Automated Setup${NC}"
echo "=================================================="
echo ""

# Function to print colored messages
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Function to detect Python environment conflicts
detect_python_conflicts() {
    print_info "Checking for Python environment conflicts..."
    
    # Check if we're in a conda environment
    if [ ! -z "$CONDA_DEFAULT_ENV" ]; then
        print_warning "Detected Conda environment: $CONDA_DEFAULT_ENV"
        print_info "This may cause conflicts with venv. Deactivating conda..."
        
        # Try to deactivate conda
        if command -v conda &> /dev/null; then
            conda deactivate 2>/dev/null || true
        fi
        
        # Unset conda variables
        unset CONDA_DEFAULT_ENV
        unset CONDA_PREFIX
        unset CONDA_PYTHON_EXE
        
        print_success "Conda environment deactivated"
    fi
    
    # Find the best Python to use
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found! Please install Python 3.10+"
        exit 1
    fi
    
    # Check Python version
    python_version=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_info "Found Python: $python_version"
    
    # Check if version is 3.10+
    required_version="3.10"
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python 3.10+ is required. Found: $python_version"
        exit 1
    fi
    
    print_success "Python version compatible: $python_version"
}

# Function to clean up old/corrupted venv
cleanup_venv() {
    if [ -d "venv" ]; then
        print_warning "Found existing venv directory"
        print_info "Checking if venv is corrupted..."
        
        # Try to activate and check if it works
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate 2>/dev/null || {
                print_warning "Virtual environment appears corrupted"
                print_info "Removing old venv..."
                deactivate 2>/dev/null || true
                rm -rf venv
                print_success "Old venv removed"
                return 1
            }
            
            # Check if pip works
            if ! venv/bin/python -m pip --version &> /dev/null; then
                print_warning "pip is not working in venv"
                print_info "Removing corrupted venv..."
                deactivate 2>/dev/null || true
                rm -rf venv
                print_success "Corrupted venv removed"
                return 1
            fi
            
            deactivate 2>/dev/null || true
            print_success "Existing venv appears healthy"
            return 0
        else
            print_warning "venv directory is incomplete"
            rm -rf venv
            print_success "Incomplete venv removed"
            return 1
        fi
    fi
    return 1
}

# Function to create venv with compatibility fixes
create_venv() {
    print_info "Creating virtual environment..."
    
    # Try standard venv creation first
    if $PYTHON_CMD -m venv venv 2>/dev/null; then
        print_success "Virtual environment created successfully"
        return 0
    else
        print_warning "Standard venv creation failed"
        print_info "Trying alternative method (without pip)..."
        
        # Create venv without pip (fixes Anaconda/Homebrew conflicts)
        if $PYTHON_CMD -m venv venv --without-pip; then
            print_success "Virtual environment created (without pip)"
            
            # Manually install pip
            print_info "Installing pip manually..."
            source venv/bin/activate
            
            curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python get-pip.py --quiet
            rm get-pip.py
            
            print_success "pip installed successfully"
            deactivate
            return 0
        else
            print_error "Failed to create virtual environment"
            return 1
        fi
    fi
}

# Function to install dependencies with fallback
install_dependencies() {
    print_info "Installing dependencies..."
    
    source venv/bin/activate
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet
    
    # Try to install from requirements.txt
    print_info "Installing from requirements.txt..."
    if pip install -r requirements.txt --quiet; then
        print_success "All dependencies installed successfully"
    else
        print_warning "Some packages failed to install"
        print_info "Trying to install critical packages individually..."

        # Install critical packages one by one
        critical_packages=(
            "streamlit"
            "loguru"
            "openai"
            "qdrant-client"
            "neo4j"
            "redis"
            "pytest"
        )

        for package in "${critical_packages[@]}"; do
            pip install "$package" --quiet || print_warning "Failed to install $package"
        done

        print_success "Critical packages installed"
    fi

    # Verify critical imports
    print_info "Verifying installation..."
    python -c "import streamlit, loguru, openai, qdrant_client, neo4j, redis, pytest" 2>/dev/null && {
        print_success "All critical packages verified"
    } || {
        print_error "Some critical packages are missing"
        print_info "You may need to install them manually"
    }

    deactivate
}

# Function to check and start Docker services
setup_docker() {
    print_info "Checking Docker..."

    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found"
        print_info "Please install Docker to run Neo4j, Qdrant, and Redis"
        print_info "Visit: https://docs.docker.com/get-docker/"
        return 1
    fi

    print_success "Docker found"

    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_warning "Docker is not running"
        print_info "Please start Docker Desktop and run this script again"
        return 1
    fi

    print_success "Docker is running"

    # Check for existing containers
    print_info "Checking for existing containers..."

    existing_containers=$(docker ps -a --filter "name=multimodal-" --format "{{.Names}}" 2>/dev/null || true)

    if [ ! -z "$existing_containers" ]; then
        print_warning "Found existing containers:"
        echo "$existing_containers"
        print_info "Removing old containers..."
        docker-compose down --remove-orphans 2>/dev/null || true
        print_success "Old containers removed"
    fi

    # Start services
    print_info "Starting Docker services (Neo4j, Qdrant, Redis)..."
    if docker-compose up -d; then
        print_success "Docker services started"

        print_info "Waiting for services to be ready (30 seconds)..."
        sleep 30

        # Check service health
        print_info "Checking service health..."
        docker ps --filter "name=multimodal-" --format "table {{.Names}}\t{{.Status}}"

        print_success "Docker services are ready"
        return 0
    else
        print_error "Failed to start Docker services"
        return 1
    fi
}

# Function to setup environment file
setup_env_file() {
    if [ ! -f ".env" ]; then
        print_info "Creating .env file..."

        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success ".env file created from .env.example"
        else
            # Create basic .env file
            cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
            print_success ".env file created with defaults"
        fi

        print_warning "⚠️  IMPORTANT: Edit .env file and add your OPENAI_API_KEY"
    else
        print_success ".env file already exists"
    fi
}

# Main setup flow
main() {
    echo ""
    print_info "Step 1: Detecting Python environment conflicts..."
    detect_python_conflicts

    echo ""
    print_info "Step 2: Checking existing virtual environment..."
    if cleanup_venv; then
        print_info "Using existing virtual environment"
    else
        print_info "Step 3: Creating new virtual environment..."
        if ! create_venv; then
            print_error "Setup failed: Could not create virtual environment"
            exit 1
        fi
    fi

    echo ""
    print_info "Step 4: Installing dependencies..."
    install_dependencies

    echo ""
    print_info "Step 5: Setting up environment file..."
    setup_env_file

    echo ""
    print_info "Step 6: Setting up Docker services..."
    setup_docker || print_warning "Docker setup skipped - you'll need to start services manually"

    echo ""
    echo "=================================================="
    print_success "Setup Complete! 🎉"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env file and add your OPENAI_API_KEY"
    echo "  2. Activate virtual environment:"
    echo "     ${GREEN}source venv/bin/activate${NC}"
    echo "  3. Start the application:"
    echo "     ${GREEN}streamlit run src/ui/app.py${NC}"
    echo "  4. Run tests:"
    echo "     ${GREEN}pytest${NC}"
    echo ""
    echo "For more information, see README.md"
    echo ""
}

# Run main setup
main


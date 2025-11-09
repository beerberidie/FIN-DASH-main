#!/bin/bash
# FIN-DASH Application Startup Script for Linux/Mac
# ==================================================
# This script starts both the backend and frontend servers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Cleanup function
cleanup() {
    echo ""
    print_warning "Shutting down servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        print_success "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        print_success "Frontend server stopped"
    fi
    
    echo ""
    print_success "FIN-DASH stopped successfully"
    echo ""
    exit 0
}

# Set up trap for Ctrl+C
trap cleanup SIGINT SIGTERM

print_header "FIN-DASH Application Startup"

# Check if Python is installed
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
print_success "Python $(python3 --version | cut -d' ' -f2) found"

# Check if Node.js is installed
print_info "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi
print_success "Node.js $(node --version) found"

# Setup backend virtual environment
print_header "Setting Up Backend"

if [ ! -d "backend/venv" ]; then
    print_info "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Install backend dependencies
print_info "Installing backend dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_error "Failed to install backend dependencies"
    exit 1
fi
cd ..
print_success "Backend dependencies installed"

# Setup frontend
print_header "Setting Up Frontend"

if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies (this may take a few minutes)..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install frontend dependencies"
        exit 1
    fi
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

# Start servers
print_header "Starting Servers"

# Start backend
print_info "Starting backend server..."
cd backend
source venv/bin/activate
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 2

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend server started (PID: $BACKEND_PID)"
else
    print_error "Backend server failed to start"
    cat backend.log
    exit 1
fi

# Start frontend
print_info "Starting frontend server..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 3

# Check if frontend started successfully
if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Frontend server started (PID: $FRONTEND_PID)"
else
    print_error "Frontend server failed to start"
    cat frontend.log
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Print success message
print_header "FIN-DASH is Running!"

print_success "Backend API: http://127.0.0.1:8777"
print_success "API Docs: http://127.0.0.1:8777/docs"
print_success "Frontend: http://localhost:5173"

echo ""
print_info "Press Ctrl+C to stop the servers"
echo ""
print_info "Logs are being written to:"
echo "  - backend.log"
echo "  - frontend.log"
echo ""

# Keep script running
while true; do
    # Check if processes are still running
    if ! ps -p $BACKEND_PID > /dev/null; then
        print_error "Backend server stopped unexpectedly"
        cat backend.log
        cleanup
    fi
    
    if ! ps -p $FRONTEND_PID > /dev/null; then
        print_error "Frontend server stopped unexpectedly"
        cat frontend.log
        cleanup
    fi
    
    sleep 1
done


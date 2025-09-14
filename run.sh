#!/bin/bash

# System Design Interview Practice - Run Script
# This script provides an easy way to start the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to stop servers
stop_servers() {
    print_status "Stopping servers..."
    pkill -f "python manage.py runserver" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    print_success "Servers stopped"
}

# Function to start backend
start_backend() {
    if port_in_use 8000; then
        print_warning "Port 8000 is already in use. Backend may already be running."
    else
        print_status "Starting Django backend server..."
        . venv/bin/activate && cd backend && python manage.py runserver 8000 > /dev/null 2>&1 &
        sleep 3
        print_success "Backend server started at http://localhost:8000"
    fi
}

# Function to start frontend
start_frontend() {
    if port_in_use 3000; then
        print_warning "Port 3000 is already in use. Frontend may already be running."
    else
        print_status "Starting React frontend server..."
        cd frontend && npm start > /dev/null 2>&1 &
        sleep 3
        print_success "Frontend server started at http://localhost:3000"
    fi
}

# Main script logic
case "${1:-start}" in
    "start"|"start-all")
        print_status "Starting System Design Interview Practice..."
        
        # Check prerequisites
        if ! command_exists python3; then
            print_error "Python 3 is not installed"
            exit 1
        fi
        
        if ! command_exists npm; then
            print_error "Node.js/npm is not installed"
            exit 1
        fi
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            print_warning "Virtual environment not found. Creating one..."
            python3 -m venv venv
            . venv/bin/activate && cd backend && pip install -r requirements.txt
        fi
        
        # Start servers
        start_backend
        start_frontend
        
        print_success "Application is running!"
        echo ""
        echo "Frontend: http://localhost:3000"
        echo "Backend:  http://localhost:8000"
        echo ""
        echo "Press Ctrl+C to stop all servers"
        
        # Wait for user to stop
        trap stop_servers EXIT
        wait
        ;;
    
    "stop")
        stop_servers
        ;;
    
    "backend")
        start_backend
        ;;
    
    "frontend")
        start_frontend
        ;;
    
    "install")
        print_status "Installing dependencies..."
        
        # Install backend dependencies
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        . venv/bin/activate && cd backend && pip install -r requirements.txt
        print_success "Backend dependencies installed"
        
        # Install frontend dependencies
        cd frontend && npm install
        print_success "Frontend dependencies installed"
        ;;
    
    "migrate")
        print_status "Running database migrations..."
        . venv/bin/activate && cd backend && python manage.py migrate
        print_success "Migrations completed"
        ;;
    
    *)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start, start-all  - Start both backend and frontend servers"
        echo "  stop              - Stop all running servers"
        echo "  backend           - Start only the backend server"
        echo "  frontend          - Start only the frontend server"
        echo "  install           - Install all dependencies"
        echo "  migrate           - Run database migrations"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start the application"
        echo "  $0 stop           # Stop all servers"
        echo "  $0 install        # Install dependencies"
        ;;
esac

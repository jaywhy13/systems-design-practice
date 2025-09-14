.PHONY: help install install-backend install-frontend start start-backend start-frontend start-all stop clean migrate

# Default target
help:
	@echo "System Design Interview Practice - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install          - Install all dependencies (backend + frontend)"
	@echo "  install-backend  - Install Python dependencies"
	@echo "  install-frontend - Install Node.js dependencies"
	@echo ""
	@echo "Development:"
	@echo "  start            - Start both backend and frontend servers"
	@echo "  start-backend    - Start Django backend server"
	@echo "  start-frontend   - Start React frontend server"
	@echo "  stop             - Stop all running servers"
	@echo ""
	@echo "Database:"
	@echo "  migrate          - Run Django migrations"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean            - Clean up temporary files"

# Installation commands
install: install-backend install-frontend

install-backend:
	@echo "Installing Python dependencies..."
	@python3 -m venv venv || true
	@. venv/bin/activate && cd backend && pip install -r requirements.txt
	@echo "Backend dependencies installed successfully!"

install-frontend:
	@echo "Installing Node.js dependencies..."
	@cd frontend && npm install
	@echo "Frontend dependencies installed successfully!"

# Development server commands
start: start-backend start-frontend

start-backend:
	@echo "Starting Django backend server..."
	@. venv/bin/activate && cd backend && python manage.py runserver 8000 

start-frontend:
	@echo "Starting React frontend server..."
	@cd frontend && npm start 
	
start-all:
	@echo "Starting both servers..."
	@make start-backend
	@sleep 2
	@make start-frontend
	@echo "Both servers are running!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"
	@echo "Press Ctrl+C to stop all servers"

# Stop servers
stop:
	@echo "Stopping all servers..."
	@pkill -f "python manage.py runserver" || true
	@pkill -f "react-scripts" || true
	@echo "All servers stopped"

# Database commands
migrate:
	@echo "Running Django migrations..."
	@. venv/bin/activate && cd backend && python manage.py migrate
	@echo "Migrations completed!"

# Cleanup
clean:
	@echo "Cleaning up temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".DS_Store" -delete
	@echo "Cleanup completed!"

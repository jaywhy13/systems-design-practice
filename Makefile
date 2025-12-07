.PHONY: help install install-backend install-frontend start start-backend start-frontend start-all start-all-background stop clean migrate

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
	@echo "  start-all-background - Start backend and frontend servers in the background"
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

start-backend:
	@echo "Starting Django backend server..."
	@. venv/bin/activate && cd backend && python manage.py runserver 8000 

start-frontend:
	@echo "Starting React frontend server..."
	@cd frontend && npm start 

# Database commands
migrate:
	@echo "Running Django migrations..."
	@. venv/bin/activate && cd backend && python manage.py migrate
	@echo "Migrations completed!"

start-all-background:
	@echo "Starting Django backend server in background..."
	@. venv/bin/activate && cd backend && nohup python manage.py runserver 8000 > backend.log 2>&1 &
	@echo "Starting React frontend server in background..."
	@cd frontend && nohup npm start > frontend.log 2>&1 &
	@echo "Both servers started in background."

stop:
	@echo "Stopping Django backend server..."
	@pkill -f "python manage.py runserver 8000" || echo "Backend server not running."
	@echo "Stopping React frontend server..."
	@pkill -f "npm start" || echo "Frontend server not running."
	@echo "All servers stopped."

# Cleanup
clean:
	@echo "Cleaning up temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".DS_Store" -delete
	@echo "Cleanup completed!"

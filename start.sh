#!/bin/bash

# Lumina AI Agents - Startup Script
# This script helps you get started with Lumina AI Agents

set -e

echo "🚀 Lumina AI Agents - Startup Script"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
    echo ""
fi

# Function to start with Docker
start_docker() {
    echo "🐳 Starting with Docker Compose..."
    echo ""

    if ! command -v docker-compose &> /dev/null; then
        echo "❌ docker-compose not found. Please install Docker and Docker Compose."
        exit 1
    fi

    echo "Building and starting services..."
    docker-compose up --build -d

    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 Service URLs:"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Frontend: http://localhost:3000"
    echo "   - PostgreSQL: localhost:5432"
    echo "   - Redis: localhost:6379"
    echo "   - Qdrant: http://localhost:6333"
    echo ""
    echo "📝 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
}

# Function to start locally
start_local() {
    echo "💻 Starting locally..."
    echo ""

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.12+."
        exit 1
    fi

    # Check Node
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js 20+."
        exit 1
    fi

    echo "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..

    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..

    echo ""
    echo "✅ Dependencies installed!"
    echo ""
    echo "⚠️  Make sure PostgreSQL, Redis, and Qdrant are running locally."
    echo ""
    echo "To start the backend:"
    echo "   cd backend && uvicorn app.main:app --reload"
    echo ""
    echo "To start the frontend:"
    echo "   cd frontend && npm run dev"
}

# Main menu
echo "Choose startup mode:"
echo "1) Docker (recommended)"
echo "2) Local development"
echo "3) Exit"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        start_docker
        ;;
    2)
        start_local
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

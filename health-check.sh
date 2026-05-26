#!/bin/bash

# Lumina AI Agents - Health Check Script
# Checks if all services are running and healthy

set -e

echo "🏥 Lumina AI Agents - Health Check"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in Docker
if command -v docker-compose &> /dev/null; then
    echo "📦 Checking Docker services..."
    echo ""

    # Check PostgreSQL
    if docker-compose ps postgres | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} PostgreSQL: Running"
    else
        echo -e "${RED}✗${NC} PostgreSQL: Not running"
    fi

    # Check Redis
    if docker-compose ps redis | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} Redis: Running"
    else
        echo -e "${RED}✗${NC} Redis: Not running"
    fi

    # Check Qdrant
    if docker-compose ps qdrant | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} Qdrant: Running"
    else
        echo -e "${RED}✗${NC} Qdrant: Not running"
    fi

    # Check Backend
    if docker-compose ps backend | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} Backend: Running"
    else
        echo -e "${RED}✗${NC} Backend: Not running"
    fi

    # Check Frontend
    if docker-compose ps frontend | grep -q "Up"; then
        echo -e "${GREEN}✓${NC} Frontend: Running"
    else
        echo -e "${RED}✗${NC} Frontend: Not running"
    fi

    echo ""
fi

# Check API endpoints
echo "🌐 Checking API endpoints..."
echo ""

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend API: http://localhost:8000 (healthy)"
else
    echo -e "${RED}✗${NC} Backend API: http://localhost:8000 (not responding)"
fi

# Check API docs
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API Docs: http://localhost:8000/docs (accessible)"
else
    echo -e "${YELLOW}⚠${NC} API Docs: http://localhost:8000/docs (not accessible)"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend: http://localhost:3000 (accessible)"
else
    echo -e "${RED}✗${NC} Frontend: http://localhost:3000 (not responding)"
fi

echo ""
echo "=================================="
echo "Health check complete!"
echo ""
echo "📊 Quick Links:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"
echo ""

#!/bin/bash
# Build script for Docker images

set -e

echo "Building Docker images..."

# Build backend image
echo "Building backend image..."
docker build -t todo-backend:latest ./backend

# Build frontend image
echo "Building frontend image..."
docker build -t todo-frontend:latest ./frontend

echo "Docker images built successfully!"
echo ""
echo "Available images:"
docker images | grep -E "todo-backend|todo-frontend"
echo ""
echo "To run the application:"
echo "  docker-compose up -d"
echo ""
echo "To stop the application:"
echo "  docker-compose down"

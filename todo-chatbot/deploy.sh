#!/bin/bash

# Todo Chatbot Kubernetes Deployment Script
# This script automates the deployment of the Todo Chatbot application to Minikube

set -e

echo "========================================"
echo "Todo Chatbot - Minikube Deployment"
echo "========================================"

# Check if minikube is running
echo ""
echo "Checking Minikube status..."
if ! minikube status > /dev/null 2>&1; then
    echo "❌ Minikube is not running. Please start Minikube first:"
    echo "   minikube start"
    exit 1
fi
echo "✓ Minikube is running"

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "✓ Minikube IP: $MINIKUBE_IP"

# Switch to Minikube's Docker environment
echo ""
echo "Switching to Minikube's Docker environment..."
eval $(minikube docker-env)
echo "✓ Using Minikube's Docker daemon"

# Check if images exist
echo ""
echo "Checking Docker images..."
if ! docker images | grep -q "phase-iv-backend"; then
    echo "⚠ Backend image not found in Minikube. Building..."
    cd ../backend
    docker build -t phase-iv-backend:latest .
    cd ../todo-chatbot
    echo "✓ Backend image built"
else
    echo "✓ Backend image exists"
fi

if ! docker images | grep -q "phase-iv-frontend"; then
    echo "⚠ Frontend image not found in Minikube. Building..."
    cd ../frontend
    docker build -t phase-iv-frontend:latest .
    cd ../todo-chatbot
    echo "✓ Frontend image built"
else
    echo "✓ Frontend image exists"
fi

# Update values.yaml with Minikube IP
echo ""
echo "Updating configuration with Minikube IP..."
sed -i.bak "s|NEXT_PUBLIC_API_URL:.*|NEXT_PUBLIC_API_URL: \"http://${MINIKUBE_IP}:30800\"|" values.yaml
sed -i.bak "s|BETTER_AUTH_URL:.*|BETTER_AUTH_URL: \"http://${MINIKUBE_IP}:30300\"|" values.yaml
echo "✓ Configuration updated"

# Check if Helm release exists
echo ""
if helm list | grep -q "todo-chatbot"; then
    echo "Upgrading existing Helm release..."
    helm upgrade todo-chatbot . --wait
    echo "✓ Helm chart upgraded"
else
    echo "Installing Helm chart..."
    helm install todo-chatbot . --wait
    echo "✓ Helm chart installed"
fi

# Wait for pods to be ready
echo ""
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-chatbot --timeout=300s

# Display deployment status
echo ""
echo "========================================"
echo "Deployment Status"
echo "========================================"
kubectl get pods
echo ""
kubectl get services

# Display access URLs
echo ""
echo "========================================"
echo "Application URLs"
echo "========================================"
echo "Frontend:  http://${MINIKUBE_IP}:30300"
echo "Backend:   http://${MINIKUBE_IP}:30800"
echo "API Docs:  http://${MINIKUBE_IP}:30800/docs"
echo ""
echo "========================================"
echo "✓ Deployment completed successfully!"
echo "========================================"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/todo-chatbot-backend"
echo "  kubectl logs -f deployment/todo-chatbot-frontend"
echo "  kubectl logs -f deployment/todo-chatbot-postgres"
echo ""
echo "To open services in browser:"
echo "  minikube service todo-chatbot-frontend"
echo "  minikube service todo-chatbot-backend"
echo ""
echo "To uninstall:"
echo "  helm uninstall todo-chatbot"
echo ""

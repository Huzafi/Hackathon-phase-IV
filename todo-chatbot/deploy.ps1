# Todo Chatbot Kubernetes Deployment Script (PowerShell)
# This script automates the deployment of the Todo Chatbot application to Minikube

$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host "Todo Chatbot - Minikube Deployment"
Write-Host "========================================"

# Check if minikube is running
Write-Host ""
Write-Host "Checking Minikube status..."
try {
    $minikubeStatus = minikube status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Minikube not running"
    }
    Write-Host "✓ Minikube is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Minikube is not running. Please start Minikube first:" -ForegroundColor Red
    Write-Host "   minikube start"
    exit 1
}

# Get Minikube IP
$MINIKUBE_IP = minikube ip
Write-Host "✓ Minikube IP: $MINIKUBE_IP" -ForegroundColor Green

# Switch to Minikube's Docker environment
Write-Host ""
Write-Host "Switching to Minikube's Docker environment..."
& minikube docker-env --shell powershell | Invoke-Expression
Write-Host "✓ Using Minikube's Docker daemon" -ForegroundColor Green

# Check if images exist
Write-Host ""
Write-Host "Checking Docker images..."
$backendImage = docker images | Select-String "phase-iv-backend"
if (-not $backendImage) {
    Write-Host "⚠ Backend image not found in Minikube. Building..." -ForegroundColor Yellow
    Set-Location ..\backend
    docker build -t phase-iv-backend:latest .
    Set-Location ..\todo-chatbot
    Write-Host "✓ Backend image built" -ForegroundColor Green
} else {
    Write-Host "✓ Backend image exists" -ForegroundColor Green
}

$frontendImage = docker images | Select-String "phase-iv-frontend"
if (-not $frontendImage) {
    Write-Host "⚠ Frontend image not found in Minikube. Building..." -ForegroundColor Yellow
    Set-Location ..\frontend
    docker build -t phase-iv-frontend:latest .
    Set-Location ..\todo-chatbot
    Write-Host "✓ Frontend image built" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend image exists" -ForegroundColor Green
}

# Update values.yaml with Minikube IP
Write-Host ""
Write-Host "Updating configuration with Minikube IP..."
$valuesContent = Get-Content values.yaml -Raw
$valuesContent = $valuesContent -replace 'NEXT_PUBLIC_API_URL:.*', "NEXT_PUBLIC_API_URL: `"http://$MINIKUBE_IP:30800`""
$valuesContent = $valuesContent -replace 'BETTER_AUTH_URL:.*', "BETTER_AUTH_URL: `"http://$MINIKUBE_IP:30300`""
$valuesContent | Set-Content values.yaml
Write-Host "✓ Configuration updated" -ForegroundColor Green

# Check if Helm release exists
Write-Host ""
$helmList = helm list 2>&1 | Select-String "todo-chatbot"
if ($helmList) {
    Write-Host "Upgrading existing Helm release..."
    helm upgrade todo-chatbot . --wait
    Write-Host "✓ Helm chart upgraded" -ForegroundColor Green
} else {
    Write-Host "Installing Helm chart..."
    helm install todo-chatbot . --wait
    Write-Host "✓ Helm chart installed" -ForegroundColor Green
}

# Wait for pods to be ready
Write-Host ""
Write-Host "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-chatbot --timeout=300s

# Display deployment status
Write-Host ""
Write-Host "========================================"
Write-Host "Deployment Status"
Write-Host "========================================"
kubectl get pods
Write-Host ""
kubectl get services

# Display access URLs
Write-Host ""
Write-Host "========================================"
Write-Host "Application URLs"
Write-Host "========================================"
Write-Host "Frontend:  http://${MINIKUBE_IP}:30300" -ForegroundColor Cyan
Write-Host "Backend:   http://${MINIKUBE_IP}:30800" -ForegroundColor Cyan
Write-Host "API Docs:  http://${MINIKUBE_IP}:30800/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================"
Write-Host "✓ Deployment completed successfully!" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "To view logs:"
Write-Host "  kubectl logs -f deployment/todo-chatbot-backend"
Write-Host "  kubectl logs -f deployment/todo-chatbot-frontend"
Write-Host "  kubectl logs -f deployment/todo-chatbot-postgres"
Write-Host ""
Write-Host "To open services in browser:"
Write-Host "  minikube service todo-chatbot-frontend"
Write-Host "  minikube service todo-chatbot-backend"
Write-Host ""
Write-Host "To uninstall:"
Write-Host "  helm uninstall todo-chatbot"
Write-Host ""

# Todo Chatbot - Kubernetes Deployment Guide

This guide will help you deploy the Todo Chatbot application to Minikube.

## Prerequisites

1. **Minikube** is running
2. **kubectl** is installed and configured
3. **Helm 3.x** is installed
4. Docker images are built:
   - `phase-iv-backend:latest`
   - `phase-iv-frontend:latest`

## Step 1: Verify Minikube is Running

```bash
minikube status
```

## Step 2: Load Docker Images to Minikube

Since you're using local Docker images, you need to load them into Minikube:

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Verify images are available
docker images | grep phase-iv
```

If images are not in Minikube's Docker environment, rebuild them:

```bash
# Navigate to backend directory
cd backend
docker build -t phase-iv-backend:latest .

# Navigate to frontend directory
cd ../frontend
docker build -t phase-iv-frontend:latest .
```

## Step 3: Update values.yaml (if needed)

Edit `values.yaml` to customize:

```yaml
backend:
  env:
    OPENAI_API_KEY: "your-openai-api-key-here"  # Add your OpenAI API key
    JWT_SECRET: "your-custom-secret-key-min-32-chars"

frontend:
  env:
    NEXT_PUBLIC_API_URL: "http://<MINIKUBE_IP>:30800"  # Update with actual Minikube IP
    BETTER_AUTH_URL: "http://<MINIKUBE_IP>:30300"
```

Get Minikube IP:
```bash
minikube ip
```

## Step 4: Install the Helm Chart

From the `phase-IV` directory:

```bash
# Install the chart
helm install todo-chatbot ./todo-chatbot

# Or upgrade if already installed
helm upgrade --install todo-chatbot ./todo-chatbot
```

## Step 5: Verify Deployment

Check all pods are running:

```bash
kubectl get pods
kubectl get services
kubectl get pvc
```

Expected output:
```
NAME                                       READY   STATUS    RESTARTS   AGE
todo-chatbot-backend-xxxxxxxxx-xxxxx       1/1     Running   0          2m
todo-chatbot-frontend-xxxxxxxxx-xxxxx      1/1     Running   0          2m
todo-chatbot-postgres-xxxxxxxxx-xxxxx      1/1     Running   0          2m
```

## Step 6: Access the Application

### Get Service URLs

```bash
# Get Minikube IP
minikube ip

# Get NodePort services
kubectl get svc
```

Access the application:
- **Frontend**: `http://<MINIKUBE_IP>:30300`
- **Backend API**: `http://<MINIKUBE_IP>:30800`
- **API Docs**: `http://<MINIKUBE_IP>:30800/docs`

### Alternative: Use Minikube Service Command

```bash
# Open frontend in browser
minikube service todo-chatbot-frontend

# Open backend in browser
minikube service todo-chatbot-backend
```

## Step 7: Check Logs

```bash
# Backend logs
kubectl logs -f deployment/todo-chatbot-backend

# Frontend logs
kubectl logs -f deployment/todo-chatbot-frontend

# Postgres logs
kubectl logs -f deployment/todo-chatbot-postgres
```

## Troubleshooting

### Pods not starting

Check pod status and events:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### ImagePullBackOff Error

This means Kubernetes can't find the Docker image. Make sure:
1. Images are built in Minikube's Docker environment
2. `imagePullPolicy` is set to `IfNotPresent` or `Never`

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# List images
docker images
```

### Database Connection Issues

Check if postgres is ready:
```bash
kubectl get pods
kubectl logs deployment/todo-chatbot-postgres
```

### Backend can't connect to Database

Verify the DATABASE_URL in backend deployment:
```bash
kubectl describe deployment todo-chatbot-backend | grep DATABASE_URL
```

Should be: `postgresql://todouser:todopassword@todo-chatbot-postgres:5432/tododb?sslmode=disable`

## Uninstall

```bash
helm uninstall todo-chatbot

# Delete PVC if needed
kubectl delete pvc todo-chatbot-postgres-pvc
```

## Clean Up

```bash
# Delete all resources
helm uninstall todo-chatbot
kubectl delete pvc --all

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Configuration Updates

To update configuration after installation:

```bash
# Edit values.yaml, then upgrade
helm upgrade todo-chatbot ./todo-chatbot

# Or use --set flag
helm upgrade todo-chatbot ./todo-chatbot \
  --set backend.env.OPENAI_API_KEY="new-key"
```

## Scaling

Scale deployments:

```bash
# Scale backend
kubectl scale deployment todo-chatbot-backend --replicas=3

# Scale frontend
kubectl scale deployment todo-chatbot-frontend --replicas=2
```

## Port Forwarding (Alternative Access Method)

```bash
# Forward backend port
kubectl port-forward svc/todo-chatbot-backend 8000:8000

# Forward frontend port
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Forward postgres port
kubectl port-forward svc/todo-chatbot-postgres 5432:5432
```

Access at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Health Checks

All services have health checks configured:

```bash
# Check backend health
curl http://<MINIKUBE_IP>:30800/

# Check frontend health
curl http://<MINIKUBE_IP>:30300/
```

## Persistent Storage

PostgreSQL data is persisted using PersistentVolumeClaim:
- Storage Class: `standard` (Minikube default)
- Size: `1Gi`

To verify:
```bash
kubectl get pvc
kubectl describe pvc todo-chatbot-postgres-pvc
```

# Todo Chatbot - Quick Command Reference

## Deployment Commands

### Initial Setup
```bash
# Start Minikube
minikube start

# Get Minikube IP
minikube ip

# Use Minikube Docker
eval $(minikube docker-env)
```

### Build Images (in Minikube Docker)
```bash
# Backend
cd backend
docker build -t phase-iv-backend:latest .

# Frontend
cd frontend
docker build -t phase-iv-frontend:latest .
```

### Deploy with Helm
```bash
# Install
helm install todo-chatbot ./todo-chatbot

# Upgrade
helm upgrade todo-chatbot ./todo-chatbot

# Upgrade with values
helm upgrade todo-chatbot ./todo-chatbot \
  --set backend.env.OPENAI_API_KEY="sk-your-key"

# Uninstall
helm uninstall todo-chatbot
```

## Monitoring Commands

### Check Status
```bash
# All resources
kubectl get all

# Pods only
kubectl get pods

# Services
kubectl get svc

# Deployments
kubectl get deployments

# PVC
kubectl get pvc
```

### View Logs
```bash
# Backend logs (follow)
kubectl logs -f deployment/todo-chatbot-backend

# Frontend logs (follow)
kubectl logs -f deployment/todo-chatbot-frontend

# Postgres logs (follow)
kubectl logs -f deployment/todo-chatbot-postgres

# Last 100 lines
kubectl logs --tail=100 deployment/todo-chatbot-backend

# Specific pod
kubectl logs <pod-name>
```

### Describe Resources
```bash
# Describe pod
kubectl describe pod <pod-name>

# Describe deployment
kubectl describe deployment todo-chatbot-backend

# Describe service
kubectl describe svc todo-chatbot-backend

# Describe PVC
kubectl describe pvc todo-chatbot-postgres-pvc
```

## Access Commands

### Service Access
```bash
# Open frontend in browser
minikube service todo-chatbot-frontend

# Open backend in browser
minikube service todo-chatbot-backend

# List all services with URLs
minikube service list
```

### Port Forwarding
```bash
# Frontend (localhost:3000)
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Backend (localhost:8000)
kubectl port-forward svc/todo-chatbot-backend 8000:8000

# Postgres (localhost:5432)
kubectl port-forward svc/todo-chatbot-postgres 5432:5432
```

### Direct URLs
```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Access URLs
echo "Frontend: http://$MINIKUBE_IP:30300"
echo "Backend: http://$MINIKUBE_IP:30800"
echo "API Docs: http://$MINIKUBE_IP:30800/docs"
```

## Debugging Commands

### Execute Commands in Pod
```bash
# Bash into backend pod
kubectl exec -it deployment/todo-chatbot-backend -- /bin/bash

# Bash into frontend pod
kubectl exec -it deployment/todo-chatbot-frontend -- /bin/sh

# Access PostgreSQL
kubectl exec -it deployment/todo-chatbot-postgres -- psql -U todouser -d tododb
```

### Database Commands
```bash
# List tables
kubectl exec -it deployment/todo-chatbot-postgres -- \
  psql -U todouser -d tododb -c "\dt"

# Check database connection
kubectl exec -it deployment/todo-chatbot-postgres -- \
  psql -U todouser -d tododb -c "SELECT version();"

# Query todos
kubectl exec -it deployment/todo-chatbot-postgres -- \
  psql -U todouser -d tododb -c "SELECT * FROM todos LIMIT 10;"
```

### Check Events
```bash
# All events
kubectl get events --sort-by='.lastTimestamp'

# Specific namespace events
kubectl get events -n default

# Watch events
kubectl get events --watch
```

## Scaling Commands

### Manual Scaling
```bash
# Scale backend to 3 replicas
kubectl scale deployment todo-chatbot-backend --replicas=3

# Scale frontend to 2 replicas
kubectl scale deployment todo-chatbot-frontend --replicas=2

# Check replica status
kubectl get deployment
```

### Auto-scaling (if enabled)
```bash
# Create HPA
kubectl autoscale deployment todo-chatbot-backend \
  --cpu-percent=80 \
  --min=1 \
  --max=5

# Check HPA status
kubectl get hpa
```

## Configuration Commands

### ConfigMap and Secrets
```bash
# View ConfigMap
kubectl get configmap todo-chatbot-config -o yaml

# View Secret (base64 encoded)
kubectl get secret todo-chatbot-secret -o yaml

# Decode secret
kubectl get secret todo-chatbot-secret -o jsonpath='{.data.JWT_SECRET}' | base64 --decode
```

### Update Configuration
```bash
# Edit values and upgrade
helm upgrade todo-chatbot ./todo-chatbot

# Or use --set
helm upgrade todo-chatbot ./todo-chatbot \
  --set backend.env.OPENAI_MODEL="gpt-4-turbo"
```

### Restart Deployments
```bash
# Restart backend
kubectl rollout restart deployment/todo-chatbot-backend

# Restart frontend
kubectl rollout restart deployment/todo-chatbot-frontend

# Check rollout status
kubectl rollout status deployment/todo-chatbot-backend
```

## Helm Commands

### Chart Management
```bash
# List releases
helm list

# Show values
helm get values todo-chatbot

# Show manifest
helm get manifest todo-chatbot

# Chart info
helm status todo-chatbot

# Chart history
helm history todo-chatbot
```

### Testing
```bash
# Dry run
helm install todo-chatbot ./todo-chatbot --dry-run --debug

# Lint chart
helm lint ./todo-chatbot

# Template rendering
helm template todo-chatbot ./todo-chatbot
```

## Cleanup Commands

### Partial Cleanup
```bash
# Delete specific deployment
kubectl delete deployment todo-chatbot-backend

# Delete specific service
kubectl delete svc todo-chatbot-backend

# Delete PVC
kubectl delete pvc todo-chatbot-postgres-pvc
```

### Full Cleanup
```bash
# Uninstall Helm release
helm uninstall todo-chatbot

# Delete namespace (if using custom namespace)
kubectl delete namespace <namespace>

# Clean up PVCs
kubectl delete pvc --all

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Performance Commands

### Resource Usage
```bash
# Top pods (CPU/Memory)
kubectl top pods

# Top nodes
kubectl top nodes

# Specific pod metrics
kubectl top pod <pod-name>
```

### Network Testing
```bash
# Test backend from another pod
kubectl run curl --image=curlimages/curl -it --rm -- \
  curl http://todo-chatbot-backend:8000

# Test database connection
kubectl run psql --image=postgres:16-alpine -it --rm -- \
  psql -h todo-chatbot-postgres -U todouser -d tododb
```

## Backup Commands

### Database Backup
```bash
# Dump database
kubectl exec deployment/todo-chatbot-postgres -- \
  pg_dump -U todouser tododb > backup.sql

# Restore database
kubectl exec -i deployment/todo-chatbot-postgres -- \
  psql -U todouser tododb < backup.sql
```

### Export Resources
```bash
# Export deployment YAML
kubectl get deployment todo-chatbot-backend -o yaml > backend-deployment.yaml

# Export all resources
kubectl get all -o yaml > all-resources.yaml
```

## Minikube Commands

### Cluster Management
```bash
# Start with specific resources
minikube start --cpus=4 --memory=8192

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# SSH into Minikube
minikube ssh

# Dashboard
minikube dashboard
```

### Docker Environment
```bash
# Use Minikube Docker (Linux/Mac)
eval $(minikube docker-env)

# Use Minikube Docker (Windows PowerShell)
& minikube docker-env --shell powershell | Invoke-Expression

# List images in Minikube
docker images

# Build image in Minikube
docker build -t myimage:latest .
```

### Add-ons
```bash
# List add-ons
minikube addons list

# Enable metrics-server
minikube addons enable metrics-server

# Enable ingress
minikube addons enable ingress
```

## Quick Troubleshooting

```bash
# Pod stuck in pending
kubectl describe pod <pod-name>

# ImagePullBackOff
kubectl describe pod <pod-name>
eval $(minikube docker-env)
docker images

# CrashLoopBackOff
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Service not accessible
kubectl get svc
minikube service list
kubectl describe svc <service-name>

# Database connection failed
kubectl logs deployment/todo-chatbot-backend
kubectl exec -it deployment/todo-chatbot-postgres -- psql -U todouser -d tododb
```

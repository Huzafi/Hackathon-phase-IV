# Kubernetes Deployment Summary

## What Was Updated

Your Helm chart has been completely configured for deploying the Todo Chatbot application to Minikube with the following architecture:

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Minikube Cluster                 │
│                                                     │
│  ┌───────────────┐   ┌──────────────┐            │
│  │   Frontend    │   │   Backend    │            │
│  │   (Next.js)   │──▶│   (FastAPI)  │            │
│  │ NodePort:30300│   │NodePort:30800│            │
│  └───────────────┘   └───────┬──────┘            │
│                               │                    │
│                               ▼                    │
│                      ┌────────────────┐           │
│                      │   PostgreSQL   │           │
│                      │  ClusterIP:5432│           │
│                      │   + PVC (1Gi)  │           │
│                      └────────────────┘           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Files Created/Updated

### Core Configuration
- ✅ `Chart.yaml` - Updated with app version 1.0.0
- ✅ `values.yaml` - Complete configuration for all 3 services
- ✅ `values-local.yaml` - Local development overrides

### Deployment Templates
- ✅ `templates/postgres-deployment.yaml` - PostgreSQL StatefulSet
- ✅ `templates/postgres-service.yaml` - PostgreSQL ClusterIP service
- ✅ `templates/postgres-pvc.yaml` - Persistent Volume Claim (1Gi)
- ✅ `templates/backend-deployment.yaml` - Backend API deployment
- ✅ `templates/backend-service.yaml` - Backend NodePort service (30800)
- ✅ `templates/frontend-deployment.yaml` - Frontend deployment
- ✅ `templates/frontend-service.yaml` - Frontend NodePort service (30300)

### Supporting Resources
- ✅ `templates/configmap.yaml` - Non-sensitive configuration
- ✅ `templates/secret.yaml` - Sensitive data (passwords, keys)
- ✅ `templates/serviceaccount.yaml` - Service account (reused)

### Documentation
- ✅ `README.md` - Complete Helm chart documentation
- ✅ `DEPLOYMENT.md` - Step-by-step deployment guide
- ✅ `COMMANDS.md` - Quick command reference

### Automation Scripts
- ✅ `deploy.sh` - Bash deployment script (Linux/Mac)
- ✅ `deploy.ps1` - PowerShell deployment script (Windows)

## Key Configuration Details

### PostgreSQL (Database)
- **Image**: `postgres:16-alpine`
- **Service Type**: ClusterIP (internal only)
- **Port**: 5432
- **Credentials**:
  - User: `todouser`
  - Password: `todopassword`
  - Database: `tododb`
- **Storage**: 1Gi PersistentVolumeClaim
- **Resources**: 250m CPU / 256Mi RAM (requests)

### Backend API
- **Image**: `phase-iv-backend:latest`
- **Service Type**: NodePort
- **Ports**: 8000 (internal), 30800 (external)
- **Environment Variables**:
  - `DATABASE_URL`: Connection to postgres service
  - `JWT_SECRET`: Authentication secret
  - `OPENAI_API_KEY`: AI agent API key
  - `OPENAI_MODEL`: gpt-4
- **Health Checks**: HTTP GET on `/` endpoint
- **Resources**: 500m CPU / 512Mi RAM (requests)

### Frontend
- **Image**: `phase-iv-frontend:latest`
- **Service Type**: NodePort
- **Ports**: 3000 (internal), 30300 (external)
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL`: Backend API endpoint
  - `BETTER_AUTH_SECRET`: Authentication secret
  - `JWT_SECRET`: Token validation
- **Health Checks**: HTTP GET on `/` endpoint
- **Resources**: 500m CPU / 512Mi RAM (requests)

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

**Windows:**
```powershell
cd G:\Hackathon-2\phase-IV\todo-chatbot
.\deploy.ps1
```

**Linux/Mac:**
```bash
cd G:\Hackathon-2\phase-IV\todo-chatbot
chmod +x deploy.sh
./deploy.sh
```

This script will:
1. Check Minikube status
2. Switch to Minikube's Docker environment
3. Build images if needed
4. Update configuration with Minikube IP
5. Install/upgrade Helm chart
6. Display access URLs

### Method 2: Manual Deployment

```bash
# 1. Ensure Minikube is running
minikube start

# 2. Switch to Minikube's Docker environment
eval $(minikube docker-env)  # Linux/Mac
# OR
& minikube docker-env --shell powershell | Invoke-Expression  # Windows

# 3. Verify images are available
docker images | grep phase-iv

# 4. Get Minikube IP and update values-local.yaml
minikube ip

# 5. Install with Helm
helm install todo-chatbot ./todo-chatbot -f values-local.yaml
```

## Access the Application

After deployment, get the Minikube IP:
```bash
minikube ip
```

Then access:
- **Frontend**: `http://<MINIKUBE_IP>:30300`
- **Backend API**: `http://<MINIKUBE_IP>:30800`
- **API Documentation**: `http://<MINIKUBE_IP>:30800/docs`

Or use Minikube services:
```bash
minikube service todo-chatbot-frontend  # Opens browser
minikube service todo-chatbot-backend
```

## Important Configuration Updates Needed

Before deploying, update `values-local.yaml` with:

1. **OpenAI API Key** (required for AI agent):
   ```yaml
   backend:
     env:
       OPENAI_API_KEY: "sk-your-actual-api-key-here"
   ```

2. **Minikube IP** (after getting from `minikube ip`):
   ```yaml
   frontend:
     env:
       NEXT_PUBLIC_API_URL: "http://192.168.49.2:30800"
       BETTER_AUTH_URL: "http://192.168.49.2:30300"
   ```

3. **JWT Secret** (optional, for production):
   ```yaml
   backend:
     env:
       JWT_SECRET: "your-secure-random-32-character-secret"
   ```

## Verification Commands

```bash
# Check all resources
kubectl get all

# Check pods status
kubectl get pods

# Check services
kubectl get svc

# View backend logs
kubectl logs -f deployment/todo-chatbot-backend

# View frontend logs
kubectl logs -f deployment/todo-chatbot-frontend

# Check database
kubectl exec -it deployment/todo-chatbot-postgres -- psql -U todouser -d tododb
```

## Common Operations

### Update Configuration
```bash
# Edit values-local.yaml, then:
helm upgrade todo-chatbot ./todo-chatbot -f values-local.yaml
```

### Scale Services
```bash
kubectl scale deployment todo-chatbot-backend --replicas=3
kubectl scale deployment todo-chatbot-frontend --replicas=2
```

### Restart Services
```bash
kubectl rollout restart deployment/todo-chatbot-backend
kubectl rollout restart deployment/todo-chatbot-frontend
```

### View Logs
```bash
kubectl logs -f deployment/todo-chatbot-backend --tail=100
kubectl logs -f deployment/todo-chatbot-frontend --tail=100
```

### Uninstall
```bash
helm uninstall todo-chatbot
kubectl delete pvc todo-chatbot-postgres-pvc  # If you want to delete data
```

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### ImagePullBackOff
Ensure images are in Minikube's Docker:
```bash
eval $(minikube docker-env)
docker images | grep phase-iv
```

### Database Connection Failed
Check if PostgreSQL is ready:
```bash
kubectl logs deployment/todo-chatbot-postgres
kubectl get pods
```

### Backend Health Check Failing
Check backend logs:
```bash
kubectl logs deployment/todo-chatbot-backend
```

Common issues:
- Database not ready (wait 30-60 seconds)
- Missing OPENAI_API_KEY
- Incorrect DATABASE_URL

## Next Steps

1. **Start Minikube** (if not running):
   ```bash
   minikube start
   ```

2. **Update Configuration**:
   - Edit `values-local.yaml`
   - Add your OpenAI API key
   - Update Minikube IP addresses

3. **Deploy**:
   ```bash
   # Windows
   .\deploy.ps1

   # Linux/Mac
   ./deploy.sh
   ```

4. **Access Application**:
   - Open browser to `http://<MINIKUBE_IP>:30300`
   - Test the API at `http://<MINIKUBE_IP>:30800/docs`

5. **Monitor**:
   ```bash
   kubectl get pods --watch
   ```

## Resources

- **Chart Documentation**: See `README.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **Command Reference**: See `COMMANDS.md`
- **Local Values**: Edit `values-local.yaml`

## Architecture Benefits

✅ **Scalable**: Can scale each service independently
✅ **Resilient**: Health checks and automatic restarts
✅ **Persistent**: Database data survives pod restarts
✅ **Configurable**: Easy to customize via values files
✅ **Secure**: Secrets separated from configuration
✅ **Production-Ready**: Can be adapted for cloud deployment

## Production Considerations

For production deployment (not Minikube), consider:

- [ ] Use managed database (Cloud SQL, RDS, etc.)
- [ ] Change service types to LoadBalancer or use Ingress
- [ ] Enable TLS/SSL certificates
- [ ] Use external secrets management (Vault, AWS Secrets Manager)
- [ ] Enable autoscaling (HPA)
- [ ] Configure resource limits properly
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure backup strategies
- [ ] Use production-grade image tags (not `latest`)
- [ ] Enable network policies
- [ ] Configure proper RBAC

Your Helm chart is ready for local Minikube deployment! 🚀

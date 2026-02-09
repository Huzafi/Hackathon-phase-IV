# Todo Chatbot Helm Chart

A Helm chart for deploying the Todo Chatbot application with AI Agent capabilities to Kubernetes (Minikube).

## Components

This chart deploys three main components:

1. **PostgreSQL Database** - Persistent data storage
2. **Backend API** - FastAPI application with AI Agent
3. **Frontend** - Next.js web application

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Minikube (for local deployment)
- Docker images built:
  - `phase-iv-backend:latest`
  - `phase-iv-frontend:latest`

## Quick Start

### 1. Automated Deployment (Recommended)

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Linux/macOS (Bash):**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 2. Manual Deployment

```bash
# Ensure you're using Minikube's Docker environment
eval $(minikube docker-env)

# Get Minikube IP
minikube ip

# Update values.yaml with your Minikube IP and OpenAI API key

# Install the chart
helm install todo-chatbot .

# Or upgrade if already installed
helm upgrade --install todo-chatbot .
```

## Configuration

The following table lists the configurable parameters and their default values.

### PostgreSQL Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgres.enabled` | Enable PostgreSQL deployment | `true` |
| `postgres.image.repository` | PostgreSQL image repository | `postgres` |
| `postgres.image.tag` | PostgreSQL image tag | `16-alpine` |
| `postgres.service.port` | PostgreSQL service port | `5432` |
| `postgres.env.POSTGRES_USER` | PostgreSQL username | `todouser` |
| `postgres.env.POSTGRES_PASSWORD` | PostgreSQL password | `todopassword` |
| `postgres.env.POSTGRES_DB` | PostgreSQL database name | `tododb` |
| `postgres.persistence.enabled` | Enable persistent storage | `true` |
| `postgres.persistence.size` | PVC size | `1Gi` |
| `postgres.resources.limits.cpu` | CPU limit | `500m` |
| `postgres.resources.limits.memory` | Memory limit | `512Mi` |

### Backend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.image.repository` | Backend image repository | `phase-iv-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.service.type` | Service type | `NodePort` |
| `backend.service.port` | Backend service port | `8000` |
| `backend.service.nodePort` | NodePort | `30800` |
| `backend.env.DATABASE_URL` | Database connection string | See values.yaml |
| `backend.env.JWT_SECRET` | JWT secret key | `your-secret-key-here-min-32-characters` |
| `backend.env.OPENAI_API_KEY` | OpenAI API key | `""` (empty) |
| `backend.env.OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `backend.resources.limits.cpu` | CPU limit | `1000m` |
| `backend.resources.limits.memory` | Memory limit | `1Gi` |

### Frontend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.image.repository` | Frontend image repository | `phase-iv-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.type` | Service type | `NodePort` |
| `frontend.service.port` | Frontend service port | `3000` |
| `frontend.service.nodePort` | NodePort | `30300` |
| `frontend.env.NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:30800` |
| `frontend.env.BETTER_AUTH_SECRET` | Better Auth secret | See values.yaml |
| `frontend.resources.limits.cpu` | CPU limit | `1000m` |
| `frontend.resources.limits.memory` | Memory limit | `1Gi` |

## Customization

### Update Configuration

Edit `values.yaml` and update with your settings:

```yaml
backend:
  env:
    OPENAI_API_KEY: "sk-your-api-key-here"
    JWT_SECRET: "your-custom-secret-min-32-chars"
```

### Apply Changes

```bash
helm upgrade todo-chatbot .
```

### Use Command Line Parameters

```bash
helm upgrade todo-chatbot . \
  --set backend.env.OPENAI_API_KEY="sk-your-key" \
  --set backend.replicaCount=2
```

## Accessing the Application

After deployment, access the application using Minikube IP and NodePorts:

```bash
# Get Minikube IP
minikube ip

# Access URLs (replace <IP> with Minikube IP)
# Frontend: http://<IP>:30300
# Backend: http://<IP>:30800
# API Docs: http://<IP>:30800/docs
```

Or use Minikube service command:

```bash
minikube service todo-chatbot-frontend  # Opens frontend
minikube service todo-chatbot-backend   # Opens backend
```

## Monitoring

### Check Deployment Status

```bash
kubectl get pods
kubectl get services
kubectl get pvc
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/todo-chatbot-backend

# Frontend logs
kubectl logs -f deployment/todo-chatbot-frontend

# Postgres logs
kubectl logs -f deployment/todo-chatbot-postgres
```

### Describe Resources

```bash
kubectl describe deployment todo-chatbot-backend
kubectl describe service todo-chatbot-backend
kubectl describe pod <pod-name>
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment todo-chatbot-backend --replicas=3

# Scale frontend
kubectl scale deployment todo-chatbot-frontend --replicas=2
```

### Helm Scaling

```bash
helm upgrade todo-chatbot . \
  --set backend.replicaCount=3 \
  --set frontend.replicaCount=2
```

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### ImagePullBackOff

Make sure images are available in Minikube's Docker environment:

```bash
eval $(minikube docker-env)
docker images | grep phase-iv
```

### Database Connection Issues

Check if PostgreSQL is ready:

```bash
kubectl logs deployment/todo-chatbot-postgres
kubectl exec -it deployment/todo-chatbot-postgres -- psql -U todouser -d tododb -c "\dt"
```

## Uninstallation

```bash
# Uninstall the chart
helm uninstall todo-chatbot

# Delete PVC (if needed)
kubectl delete pvc todo-chatbot-postgres-pvc
```

## Development

### Lint Chart

```bash
helm lint .
```

### Test Template Rendering

```bash
helm template todo-chatbot .
```

### Dry Run

```bash
helm install todo-chatbot . --dry-run --debug
```

## Support

For issues and questions:
1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Review pod logs: `kubectl logs <pod-name>`
3. Check pod events: `kubectl describe pod <pod-name>`

## License

See project root for license information.

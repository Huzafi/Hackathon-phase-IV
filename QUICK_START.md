# Quick Start Guide - Running Docker Images

## Built Images Summary

✅ **Backend Image**: `todo-backend:latest`
- Size: 937MB (231MB compressed)
- Port: 8000
- Base: Python 3.11-slim
- Includes: FastAPI, PostgreSQL client, OpenAI Swarm

✅ **Frontend Image**: `todo-frontend:latest`
- Size: 407MB (96.7MB compressed)
- Port: 3000
- Base: Node 20-alpine
- Includes: Next.js 15, React 19, Tailwind CSS

---

## Running Individual Containers

### 1. Run Backend Container

```bash
docker run -d \
  --name todo-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/database" \
  -e JWT_SECRET="your-secret-key-min-32-characters" \
  -e OPENAI_API_KEY="sk-proj-your-key" \
  -e OPENAI_MODEL="gpt-4" \
  todo-backend:latest
```

**Required Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens (min 32 chars)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-4)

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/

### 2. Run Frontend Container

```bash
docker run -d \
  --name todo-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -e BETTER_AUTH_SECRET="your-auth-secret" \
  -e JWT_SECRET="your-secret-key-min-32-characters" \
  todo-frontend:latest
```

**Required Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `BETTER_AUTH_SECRET`: Better Auth secret key
- `JWT_SECRET`: Same as backend JWT secret

**Access:**
- Frontend: http://localhost:3000

---

## Complete Setup with PostgreSQL

### Option 1: Using Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL + Backend + Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Option 2: Manual Setup

**Step 1: Start PostgreSQL**
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopassword \
  -e POSTGRES_DB=tododb \
  -p 5432:5432 \
  postgres:16-alpine
```

**Step 2: Start Backend**
```bash
docker run -d \
  --name todo-backend \
  --link postgres:postgres \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://todouser:todopassword@postgres:5432/tododb" \
  -e JWT_SECRET="your-secret-key-here-min-32-characters" \
  -e OPENAI_API_KEY="sk-proj-your-openai-key" \
  -e OPENAI_MODEL="gpt-4" \
  todo-backend:latest
```

**Step 3: Start Frontend**
```bash
docker run -d \
  --name todo-frontend \
  --link todo-backend:backend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -e BETTER_AUTH_SECRET="Kf9sP3xR7L2Qm8ZB6D0NwA1E5JH4CYaV" \
  -e JWT_SECRET="your-secret-key-here-min-32-characters" \
  todo-frontend:latest
```

---

## Useful Docker Commands

### View Running Containers
```bash
docker ps
```

### View All Containers (including stopped)
```bash
docker ps -a
```

### View Container Logs
```bash
# Backend logs
docker logs -f todo-backend

# Frontend logs
docker logs -f todo-frontend
```

### Stop Containers
```bash
docker stop todo-backend todo-frontend
```

### Remove Containers
```bash
docker rm todo-backend todo-frontend
```

### Restart Containers
```bash
docker restart todo-backend
docker restart todo-frontend
```

### Execute Commands Inside Container
```bash
# Backend shell
docker exec -it todo-backend /bin/bash

# Frontend shell
docker exec -it todo-frontend /bin/sh
```

### View Container Resource Usage
```bash
docker stats todo-backend todo-frontend
```

---

## Testing the Images

### Test Backend Health
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Todo Backend API",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### Test Frontend
Open browser: http://localhost:3000

---

## Troubleshooting

### Backend won't start
1. Check if PostgreSQL is running and accessible
2. Verify DATABASE_URL is correct
3. Check logs: `docker logs todo-backend`

### Frontend won't connect to backend
1. Verify backend is running: `docker ps`
2. Check NEXT_PUBLIC_API_URL matches backend URL
3. Check logs: `docker logs todo-frontend`

### Port already in use
```bash
# Find process using port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process or use different port
docker run -p 8001:8000 ...  # Map to different host port
```

### Clear everything and start fresh
```bash
# Stop and remove all containers
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Remove images
docker rmi todo-backend:latest todo-frontend:latest

# Rebuild
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

---

## Production Deployment

### Push to Docker Hub
```bash
# Tag images
docker tag todo-backend:latest yourusername/todo-backend:latest
docker tag todo-frontend:latest yourusername/todo-frontend:latest

# Login to Docker Hub
docker login

# Push images
docker push yourusername/todo-backend:latest
docker push yourusername/todo-frontend:latest
```

### Pull and Run on Server
```bash
# Pull images
docker pull yourusername/todo-backend:latest
docker pull yourusername/todo-frontend:latest

# Run with production settings
docker run -d \
  --name todo-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e JWT_SECRET="$JWT_SECRET" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  yourusername/todo-backend:latest
```

---

## Environment Variables Reference

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/database
JWT_SECRET=your-secret-key-here-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
OPENAI_API_KEY=sk-proj-your-openai-api-key
OPENAI_MODEL=gpt-4
AGENT_TIMEOUT=30
CONTEXT_WINDOW_SIZE=20
```

### Frontend (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-auth-secret-here
BETTER_AUTH_URL=http://localhost:3000
JWT_SECRET=your-secret-key-here-min-32-characters
JWT_ALGORITHM=HS256
```

---

## Health Checks

Both images include health checks:

**Backend:**
- Endpoint: `http://localhost:8000/`
- Interval: 30s
- Timeout: 10s
- Retries: 3

**Frontend:**
- Endpoint: `http://localhost:3000/`
- Interval: 30s
- Timeout: 10s
- Retries: 3

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' todo-backend
docker inspect --format='{{.State.Health.Status}}' todo-frontend
```

---

## Next Steps

1. **Test locally**: Run containers and verify functionality
2. **Configure environment**: Update .env files with production values
3. **Set up CI/CD**: Automate image building and deployment
4. **Monitor**: Set up logging and monitoring solutions
5. **Scale**: Use Kubernetes or Docker Swarm for orchestration
6. **Secure**: Implement SSL/TLS, secrets management, and security scanning

---

## Support

For issues or questions:
- Check logs: `docker logs -f <container-name>`
- Verify environment variables
- Review DOCKER_GUIDE.md for detailed documentation
- Check Docker Desktop is running

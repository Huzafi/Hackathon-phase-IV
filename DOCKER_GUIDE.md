# Docker Deployment Guide

This guide explains how to build and run the Todo application using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed (included with Docker Desktop)
- At least 4GB of available RAM
- Ports 3000, 8000, and 5432 available

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.docker .env
```

Edit `.env` and set:
- `JWT_SECRET`: A secure random string (min 32 characters)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-4)

### 2. Build Docker Images

**On Windows:**
```bash
build-images.bat
```

**On Linux/Mac:**
```bash
chmod +x build-images.sh
./build-images.sh
```

**Or manually:**
```bash
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

### 3. Start the Application

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend application on port 3000

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Docker Commands

### View Running Containers
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stop the Application
```bash
docker-compose down
```

### Stop and Remove Volumes (Delete Database)
```bash
docker-compose down -v
```

### Restart a Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild and Restart
```bash
docker-compose up -d --build
```

## Architecture

The Docker setup includes three services:

### 1. PostgreSQL Database (`postgres`)
- Image: `postgres:16-alpine`
- Port: 5432
- Volume: `postgres_data` for data persistence
- Health check enabled

### 2. Backend API (`backend`)
- Built from `./backend/Dockerfile`
- Port: 8000
- Depends on PostgreSQL
- Auto-restarts on failure

### 3. Frontend Application (`frontend`)
- Built from `./frontend/Dockerfile`
- Port: 3000
- Depends on Backend
- Multi-stage build for optimization

## Troubleshooting

### Port Already in Use
If you get port conflicts, stop the conflicting service or change ports in `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change host port
```

### Database Connection Issues
Check if PostgreSQL is healthy:
```bash
docker-compose ps
docker-compose logs postgres
```

### Backend Not Starting
Check backend logs:
```bash
docker-compose logs backend
```

Common issues:
- Missing environment variables
- Database not ready (wait for health check)
- Invalid OpenAI API key

### Frontend Build Errors
Ensure Next.js standalone output is enabled in `next.config.ts`:
```typescript
output: 'standalone'
```

### Clear Everything and Start Fresh
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

## Production Considerations

For production deployment:

1. **Update CORS settings** in `backend/src/main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Use secrets management** instead of `.env` file

3. **Enable SSL/TLS** with a reverse proxy (nginx, traefik)

4. **Set resource limits** in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```

5. **Use production database** instead of containerized PostgreSQL

6. **Enable monitoring** and logging solutions

7. **Regular backups** of PostgreSQL data volume

## Development Workflow

### Hot Reload Development
For development with hot reload, use the local development setup instead:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Testing Changes
After making code changes:

```bash
# Rebuild specific service
docker-compose up -d --build backend

# Or rebuild all
docker-compose up -d --build
```

## Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` command
- **Backend**: HTTP GET to `/`
- **Frontend**: HTTP GET to root

View health status:
```bash
docker-compose ps
```

## Data Persistence

Database data is stored in a Docker volume:
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect phase-iv_postgres_data

# Backup volume
docker run --rm -v phase-iv_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## Network

All services communicate through the `todo-network` bridge network:
- Services can reach each other by service name
- Backend connects to `postgres:5432`
- Frontend connects to `backend:8000`

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Ensure all ports are available
4. Check Docker Desktop is running
5. Review this guide's troubleshooting section

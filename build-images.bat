@echo off
REM Build script for Docker images (Windows)

echo Building Docker images...

REM Build backend image
echo Building backend image...
docker build -t todo-backend:latest ./backend
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build backend image
    exit /b 1
)

REM Build frontend image
echo Building frontend image...
docker build -t todo-frontend:latest ./frontend
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build frontend image
    exit /b 1
)

echo.
echo Docker images built successfully!
echo.
echo Available images:
docker images | findstr "todo-backend todo-frontend"
echo.
echo To run the application:
echo   docker-compose up -d
echo.
echo To stop the application:
echo   docker-compose down

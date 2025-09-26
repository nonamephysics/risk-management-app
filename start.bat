@echo off
REM Start script for Risk App (Windows)

echo Starting Risk App...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Build and start containers
echo Building and starting containers...
docker-compose up --build

echo Application should be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
pause
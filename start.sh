#!/bin/bash

# Start script for Risk App

echo "Starting Risk App..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start containers
echo "Building and starting containers..."
docker-compose up --build

echo "Application should be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
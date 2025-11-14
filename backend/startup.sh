#!/bin/bash

# Azure App Service startup script for Python app
echo "Starting Azure App Service startup script..."

# Install dependencies if requirements.txt exists
if [ -f "/home/site/wwwroot/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install --no-cache-dir -r /home/site/wwwroot/requirements.txt
fi

# Start the application with gunicorn
echo "Starting application with gunicorn..."
cd /home/site/wwwroot
gunicorn --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 main:app
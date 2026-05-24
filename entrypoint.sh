#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting services..."
# In a real multi-service container, you might use a process manager like supervisor
# For this scaffold, we launch the API
uvicorn api.main:app --host 0.0.0.0 --port 8000

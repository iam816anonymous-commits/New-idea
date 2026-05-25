#!/bin/bash
set -e

# Run migrations
PYTHONPATH=. alembic upgrade head

# If arguments are provided, execute them (useful for running streamlit or other commands)
if [ $# -gt 0 ]; then
  exec "$@"
else
  # Default to starting the API
  PYTHONPATH=. uvicorn proppulse_os.lead_engine.main:app --host 0.0.0.0 --port 8000
fi

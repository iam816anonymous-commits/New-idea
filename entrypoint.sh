#!/bin/bash
set -e

# Run migrations
PYTHONPATH=. alembic upgrade head

# Start lead engine (API)
PYTHONPATH=. uvicorn proppulse_os.lead_engine.main:app --host 0.0.0.0 --port 8000

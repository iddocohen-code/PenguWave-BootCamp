#!/usr/bin/env bash
# Start the PenguWave backend on the port the frontend/API contract expects (3001).
set -euo pipefail
cd "$(dirname "$0")"
exec uvicorn app.main:app --host 127.0.0.1 --port 3001 --reload

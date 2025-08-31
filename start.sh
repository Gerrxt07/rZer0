#!/bin/bash
set -e

# Production configuration
VENV_DIR="venv"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-4}"
RUNTIME_THREADS="${RUNTIME_THREADS:-4}"
APP_MODULE="app.main:app"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting rZer0 FastAPI Application (Production Mode)...${NC}"

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${YELLOW}Using Python $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Start the application with granian in production mode
echo -e "${GREEN}Starting FastAPI application with Granian ASGI server (Production)...${NC}"
echo -e "${YELLOW}Server will be available at: http://$HOST:$PORT${NC}"
echo -e "${YELLOW}Workers: $WORKERS, Runtime Threads: $RUNTIME_THREADS${NC}"

# Start the server using granian with ASGI interface (production settings)
exec granian \
    --interface asgi \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --runtime-threads $RUNTIME_THREADS \
    --loop rloop \
    --access-log \
    --backlog 2048 \
    --runtime-mode mt \
    --task-impl rust \
    --reload \
    $APP_MODULE

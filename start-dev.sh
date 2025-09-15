#!/bin/bash
# rZer0 Development Startup Script
# This script starts the application in development mode with hot reload

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to load environment variables from .env files
load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        echo -e "${BLUE}Loading environment variables from $env_file${NC}"
        set -a  # automatically export all variables
        source <(grep -E '^[A-Z_][A-Z0-9_]*=' "$env_file" | sed 's/^/export /')
        set +a
        return 0
    fi
    return 1
}

echo -e "${GREEN}Starting rZer0 FastAPI Application (Development Mode)...${NC}"

# Set development environment
export ENVIRONMENT=development

# Load development-specific .env file first, then fallback to .env
if ! load_env_file ".env.development"; then
    if ! load_env_file ".env"; then
        echo -e "${YELLOW}Warning: No .env file found. Using default development settings.${NC}"
    fi
fi

# Set development configuration with environment variables or defaults
VENV_DIR="${VENV_DIR:-venv}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
APP_MODULE="${APP_MODULE:-app.main:app}"

echo -e "${BLUE}Development Configuration:${NC}"
echo -e "  ${YELLOW}Host: $HOST${NC}"
echo -e "  ${YELLOW}Port: $PORT${NC}"
echo -e "  ${YELLOW}App Module: $APP_MODULE${NC}"

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
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install --upgrade pip || echo "pip upgrade failed - continuing"
pip install -r requirements.txt

# Start Dragonfly cache service if docker-compose is available
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    echo -e "${BLUE}Starting Dragonfly cache service...${NC}"
    cd docker && docker compose up dragonfly -d && cd .. || echo -e "${YELLOW}Warning: Could not start Dragonfly service${NC}"
fi

# Start the application with granian in development mode (with reload)
echo -e "${GREEN}Starting FastAPI application with Granian ASGI server (Development with reload)...${NC}"
echo -e "${YELLOW}Server will be available at: http://$HOST:$PORT${NC}"
echo -e "${YELLOW}API documentation: http://$HOST:$PORT/docs${NC}"

# Start the server using granian with ASGI interface (development settings)
exec granian \
    --interface asgi \
    --host "$HOST" \
    --port "$PORT" \
    --workers 1 \
    --runtime-threads 1 \
    --loop rloop \
    --reload \
    --access-log \
    "$APP_MODULE"

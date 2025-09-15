#!/bin/bash
set -e

# Enhanced Production Startup Script with .env support
# This script loads environment variables from .env files and starts the rZer0 application

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
        # Source the .env file, handling comments and empty lines
        set -a  # automatically export all variables
        source <(grep -E '^[A-Z_][A-Z0-9_]*=' "$env_file" | sed 's/^/export /')
        set +a
        return 0
    fi
    return 1
}

# Function to validate required environment variables
validate_environment() {
    local environment="${ENVIRONMENT:-production}"
    echo -e "${BLUE}Validating environment: $environment${NC}"
    
    # Check environment-specific required variables
    case "$environment" in
        "production"|"staging")
            if [ -z "$SECRET_KEY" ]; then
                echo -e "${RED}Error: SECRET_KEY is required for $environment environment${NC}"
                echo -e "${YELLOW}Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"${NC}"
                exit 1
            fi
            ;;
    esac
    
    echo -e "${GREEN}Environment validation passed${NC}"
}

echo -e "${GREEN}Starting rZer0 FastAPI Application (Production Mode)...${NC}"

# Load environment configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"

# Load environment-specific .env file first, then fallback to .env
if ! load_env_file ".env.$ENVIRONMENT"; then
    if ! load_env_file ".env"; then
        echo -e "${YELLOW}Warning: No .env file found. Using system environment variables.${NC}"
    fi
fi

# Set configuration with environment variables or defaults
VENV_DIR="${VENV_DIR:-venv}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-2}"
RUNTIME_THREADS="${RUNTIME_THREADS:-1}"
BACKLOG="${BACKLOG:-2048}"
APP_MODULE="${APP_MODULE:-app.main:app}"

# Validate environment configuration
validate_environment

echo -e "${BLUE}Configuration:${NC}"
echo -e "  ${YELLOW}Host: $HOST${NC}"
echo -e "  ${YELLOW}Port: $PORT${NC}"
echo -e "  ${YELLOW}Workers: $WORKERS${NC}"
echo -e "  ${YELLOW}Runtime Threads: $RUNTIME_THREADS${NC}"
echo -e "  ${YELLOW}Backlog: $BACKLOG${NC}"
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

# Start the server using granian with ASGI interface (production settings)
exec granian \
    --interface asgi \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --runtime-threads "$RUNTIME_THREADS" \
    --loop rloop \
    --access-log \
    --backlog "$BACKLOG" \
    "$APP_MODULE"

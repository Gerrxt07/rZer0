# rZer0 Project - GitHub Copilot Coding Agent Instructions

**ALWAYS follow these instructions first and fallback to additional search and context gathering only if the information here is incomplete or found to be in error.**

## Architecture Overview

rZer0 is a modern, high-performance web application built with Python FastAPI backend and HTMX-driven frontend, designed for clean code and excellent developer experience. The application runs on Debian 12 servers using Granian ASGI server with worker processes.

## Quick Start Commands

### Environment Setup (CRITICAL - Run these first)

Run these commands in the repository root directory:

```bash
# Create and activate virtual environment (~3 seconds)
python3 -m venv venv
source venv/bin/activate

# Install dependencies (~15 seconds)
# Note: pip upgrade may fail due to network timeouts - skip if it fails
pip install --upgrade pip || echo "pip upgrade failed - continuing with installation"
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env
```

**NEVER CANCEL**: Dependency installation takes ~15 seconds. Set timeout to 120+ seconds.
**NETWORK TIMEOUT WARNING**: If pip install fails with "Read timed out" errors, this indicates network connectivity issues. The commands are correct but the environment has restricted internet access.

### Alternative Setup for Restricted Networks

If pip install fails due to network timeouts:

```bash
# For environments with pre-installed dependencies or offline package sources
python3 -m venv venv
source venv/bin/activate
cp .env.example .env

# Verify basic imports work (should succeed if deps are pre-installed system-wide)
python -c "import fastapi, granian; print('Dependencies available')"
```

### Development Mode

Run the application in development mode with auto-reload:

```bash
# Start Dragonfly cache service (~4 seconds for first pull)
cd docker && docker compose up dragonfly -d && cd ..

# Start FastAPI application with reload
source venv/bin/activate
granian --interface asgi --host 127.0.0.1 --port 8000 --workers 1 --loop rloop --reload app.main:app
```

**NEVER CANCEL**: Dragonfly Docker pull takes ~4 seconds on first run. Set timeout to 300+ seconds for Docker operations.

Application will be available at: http://127.0.0.1:8000

### Production Mode

Use the production start script:

```bash
./start.sh
```

**WARNING**: The start.sh script may fail in environments with network restrictions (pip install timeout issues). Use the manual development commands above as a workaround.

**System Package Alternative**: If pip install fails consistently, install system packages:
```bash
# For Ubuntu/Debian systems
sudo apt-get update
sudo apt-get install python3-fastapi python3-uvicorn python3-granian
```

## Validation Commands

### API Endpoint Testing

Always test these endpoints after making changes:

```bash
# Root endpoint
curl -s http://127.0.0.1:8000/ | jq .

# Health check endpoint  
curl -s http://127.0.0.1:8000/health | jq .

# API documentation
curl -s http://127.0.0.1:8000/docs | grep -o '<title>.*</title>'

# OpenAPI schema
curl -s http://127.0.0.1:8000/openapi.json | jq '.info'
```

Expected responses:
- `/`: `{"message": "Hello World!", "status": "running"}`
- `/health`: `{"status": "online", "date": "DD:MM:YYYY", "time": "HH:MM:SS"}`
- `/docs`: Returns Scalar API Reference HTML page
- `/openapi.json`: Returns OpenAPI 3.1.0 specification

### Load Testing

Test application performance using Locust:

```bash
# Install locust if not already installed
source venv/bin/activate
pip install locust

# Run 30-second load test (10 users, 2 ramp-up rate)
locust -f locust.py --headless -u 10 -r 2 -t 30s
```

**NEVER CANCEL**: Load test runs for exactly 30 seconds. Set timeout to 120+ seconds.

Expected result: 0 failures, ~3-4 req/s aggregate throughput.

## Key Project Structure

```
├── app/                        # Main application code
│   ├── main.py                # FastAPI app entry point
│   └── modules/
│       ├── config.py          # Environment configuration
│       ├── endpoints/         # API endpoints
│       │   ├── root.py        # Root endpoint (/)
│       │   ├── health.py      # Health check endpoint
│       │   └── docs.py        # API documentation
│       └── logging/           # Logging module (empty)
├── docker/
│   └── docker-compose.yml    # Dragonfly cache service
├── static/                    # Static assets (icons)
├── requirements.txt          # Python dependencies
├── start.sh                  # Production startup script
├── locust.py                 # Load testing configuration
└── .env.example              # Environment template
```

## Development Guidelines

### Code Quality Standards
- **Clean Codebase** is a core principle - prioritize readability and maintainability
- Use async/await patterns throughout Python code with `asyncio` and `rloop`
- All endpoints return JSONResponse for consistency
- Follow existing code structure in `app/modules/endpoints/`

### Application Architecture
- **Backend**: FastAPI with Granian ASGI server and rloop event loop
- **Cache**: Dragonfly (Redis-compatible) for sessions and caching
- **Frontend**: HTMX + Alpine.js + TailwindCSS (built with Bun when needed)
- **Load Testing**: Locust for performance validation
- **Documentation**: Scalar API Reference (replaces Swagger UI)

### Common Development Tasks

#### Adding New API Endpoints
1. Create new file in `app/modules/endpoints/`
2. Follow pattern from existing endpoints (health.py, root.py)
3. Import and register router in `app/modules/endpoints/__init__.py`
4. Add router to `app/main.py`
5. Test with curl and verify in `/docs` endpoint

#### Configuration Changes
- Modify `app/modules/config.py` for new environment variables
- Update `.env.example` with new variables
- Configuration loads from `.env` file automatically

### Docker Services

Dragonfly (Redis-compatible cache):
```bash
# Start service
cd docker && docker compose up dragonfly -d

# Stop service  
cd docker && docker compose down

# View logs
cd docker && docker compose logs dragonfly
```

### Installation Notes

**Bun Installation (for frontend assets):**
```bash
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc
bun --version
```

**Docker Requirements:**
- Docker version 28.0.4+ 
- Docker Compose v2.38.2+

### Common Issues and Solutions

1. **Network timeouts during pip install**: This indicates restricted internet access in the environment. Commands are correct but environment has connectivity limitations.
2. **Start script fails with pip timeout**: Use manual development commands instead
3. **Port 8000 already in use**: Kill existing processes with `pkill -f granian` or use different port
4. **Dragonfly connection issues**: Ensure Docker service is running with `docker compose ps`
5. **Import errors**: Ensure virtual environment is activated and dependencies installed

### Performance Expectations

- Virtual environment creation: ~3 seconds
- Dependency installation: ~15 seconds
- Dragonfly first-time setup: ~4 seconds  
- Application startup: ~2 seconds
- Load test (30s): 0 failures expected, ~3-4 req/s throughput

**NEVER CANCEL** any of these operations. Always wait for completion and set appropriate timeouts (60+ seconds for builds, 300+ seconds for Docker operations).

### Validation Workflow

After making any changes, always:

1. Test application imports: `python -c "import app.main; print('OK')"`
2. Start Dragonfly: `cd docker && docker compose up dragonfly -d`
3. Start application: `granian --interface asgi --host 127.0.0.1 --port 8000 --workers 1 --loop rloop app.main:app`
4. Test all endpoints with curl commands above
5. Run load test to ensure performance is maintained
6. Check application logs for any errors

This ensures your changes integrate properly with the existing architecture and maintain expected performance characteristics.

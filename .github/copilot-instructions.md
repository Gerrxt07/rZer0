# rZer0 Project - AI Coding Agent Instructions

## Architecture Overview

This is a modern, high-performance web application built with Python FastAPI backend and HTMX-driven frontend, designed for clean code and excellent developer experience.

### Tech Stack Summary
- **Backend**: FastAPI with Granian ASGI server, async-first approach
- **Database**: PostgreSQL (primary) + Dragonfly (Redis-compatible cache)
- **Frontend**: HTMX + Alpine.js for interactivity, styled with TailwindCSS + DaisyUI
- **Build Tools**: Bun for frontend asset compilation
- **Infrastructure**: Debian 12, Nginx reverse proxy, Docker containers
- **Monitoring**: Prometheus + Grafana stack

## Development Guidelines

### Code Quality Standards
- **Clean Codebase** is a core principle - prioritize readability and maintainability
- Follow established **Coding Guidelines**
- Comprehensive **Documentation** is required for all components
- Use async/await patterns throughout Python code with `asyncio` and `uvloop`

### Key Libraries & Patterns
- **Backend**: Use `pydantic` for data validation, `loguru` for logging, `dramatiq` for background tasks, and `httpx` for making HTTP requests, and `asyncio` for asynchronous programming.
- **Database**: `psqlpy` + `SQLAlchemy` for ORM, `Alembic` for migrations, `zangy` for Dragonfly cache operations
- **Frontend**: Prefer HTMX for dynamic interactions, Alpine.js for client-side state, Lucide for consistent iconography, and Motion One for animations
- **Styling**: TailwindCSS utility classes with DaisyUI components, SASS for custom styles

### Development Workflow
- Python environment should have auto-import completions enabled (see `.vscode/settings.json`)
- Frontend assets built with Bun (faster than npm/yarn)

## Project Structure Expectations

Since this is an early-stage project, expect to create:
- `app/` directory for Python FastAPI application
- `static/` or `assets/` for frontend resources
- `templates/` for HTML templates (likely Jinja2)
- `migrations/` for Alembic database migrations

Multiple FastAPI Apps can be created within the `app/` directory, each with its own subdirectory. Using something like app.mount().


## Integration Points

- **Database Layer**: PostgreSQL for persistence, Dragonfly for caching and sessions
- **Task Queue**: Dramatiq for background job processing
- **Reverse Proxy**: Nginx configuration for FastAPI upstream
- **Monitoring**: Prometheus metrics collection from FastAPI and infrastructure
- **Frontend-Backend**: HTMX endpoints should return HTML fragments, not JSON APIs

## Deployment Context

- **Target Environment**: Debian 12 server
- **Process Management**: Granian ASGI server with worker processes
- **HTTP Layer**: Nginx handles static files, proxies dynamic requests to FastAPI
- **Observability**: Full monitoring stack with Prometheus metrics and Grafana dashboards

When implementing features, consider the async nature of the stack and ensure all database operations use proper connection pooling and async patterns.

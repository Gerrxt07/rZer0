# rZer0 Project - AI Coding Agent Instructions

## Architecture Overview

This is a modern, high-performance web application built with Python FastAPI backend and HTMX-driven frontend, designed for clean code and excellent developer experience.

## Development Guidelines

### Code Quality Standards
- **Clean Codebase** is a core principle - prioritize readability and maintainability
- Follow established **Coding Guidelines**
- Comprehensive **Documentation** is required for all components
- Use async/await patterns throughout Python code with `asyncio` and `uvloop`

### Development Workflow
- Python environment should have auto-import completions enabled (see `.vscode/settings.json`)
- Frontend assets built with Bun (faster than npm/yarn)

## Integration Points

- **Database Layer**: PostgreSQL for persistence, Dragonfly for caching and sessions
- **Task Queue**: Dramatiq for background job processing

## Deployment Context

- **Target Environment**: Debian 12 server
- **Process Management**: Granian ASGI server with worker processes

When implementing features, consider the async nature of the stack and ensure all database operations use proper connection pooling and async patterns.

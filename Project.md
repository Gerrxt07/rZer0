# General

- Hosted on Debian 12 Server.
- Using Nginx as a reverse proxy.
- Python is the primary code language.
- Clean Codebase, Coding Guidelines and Documentation are key.

## Backend Stack

- FastAPI /w Granian ASGI/Workers
- Python Libraries: Asyncio, httpx, uvloop, pydantic, dramatiq, loguru

## Database Layer

- PostgreSQL (Storage)
                - Libraries: psqlpy, SQLAlchemy, Alembic

- Dragonfly (Cache)
                - Libraries: Zangy

## Client Layer

- Html, CSS, Javascript
                - Libraries: Htmx, Alpine.js, Lucide (Icons), Motion One (Motion.js)
- Bun
                - Libraries: TailwindCSS, DaisyUI, SASS

## Other Services

- Posthog for analytics
- Maybe Clerk for user / authentication

# General

- Hosted on Debian 12 Server.
- Python is the primary code language.
- Clean Codebase, Coding Guidelines and Documentation are key.
- Fully beeing async and multiprocessing

## Backend Stack

- FastAPI /w Granian ASGI/Workers - Using emmett's "renoir" as replacement for Jinja
- Planned Python Libraries: Asyncio, httpx, rloop, pydantic, arq, loguru

## Database Layer

- PostgreSQL (Storage via Docker)
                - Libraries: psqlpy, SQLAlchemy, Alembic

- Dragonfly (Cache via Docker)
                - Libraries: Zangy

## Client Layer

- Html, CSS, Javascript
                - Libraries: Htmx, Alpine.js, Lucide (Icons), Motion One (Motion.js)
- Bun
                - Libraries: TailwindCSS, DaisyUI, SASS

## Other Services

- Posthog for analytics
- Maybe Clerk for user / authentication

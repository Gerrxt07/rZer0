# Plan

- Config: Add support for variables via .env / python-dotenv. Code should be simple and understandable.
- Health Endpoint Rewrite: Adding date & time information to the response.
- Logging: Add detailed logging via loguru & colorama. Adding the Code to app/modules/logging/log.py. Code should be simple and understandable.
- CORS & Middleware: Adding CORS Rules and a Middleware. Adding the Code to app/modules/security/middleware.py.  Code should be simple and understandable.
- Security Headers: Add security headers with starlette or fastapi middleware. Adding the Code to app/modules/security/headers.py. Code should be simple and understandable.

- Rate Limiting: Add Rate limiting with dragonflydb (redis fork, fully compatible) and the Zangy library. Use the BLUB principe. Adding the Code to app/modules/security/ratelimit.py. Code should be simple and understandable.

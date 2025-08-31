# Plan

- Config: Add support for variables via .env / python-dotenv. Code should be simple and understandable.
- Health Endpoint Rewrite: Adding date & time information to the response.
- Logging: Add detailed logging via loguru & colorama. Adding the Code to app/modules/logging/log.py. Code should be simple and understandable.
- CORS & Middleware: Adding CORS Rules and a Middleware. Adding the Code to app/modules/security/middleware.py.  Code should be simple and understandable.
- Security Headers: Add security headers with starlette or fastapi middleware. Adding the Code to app/modules/security/headers.py. Code should be simple and understandable.

- Rate Limiting: Add IP-based Rate limiting with dragonflydb (redis fork, fully compatible) and the Zangy library. Use the fastapi-limiter library with a sliding/floating window. Adding the Code to app/modules/security/ratelimit.py. Get the IP via X-Forwarded-For / CF-Connecting-IP (We using Cloudflare as Proxy and Safeline WAF). Send 429 Code to the user when hitting the limit. Code should be simple and understandable.

- Fully rewrite for using multiprocessing. Also JSON serialization using ORJSONResponse as the default response class in FastAPI because it’s often the easiest 1.5–2x bump on JSON endpoints.

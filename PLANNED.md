# Plan

- Rate Limiting: Add IP-based Rate limiting with dragonflydb (redis fork, fully compatible) and the Zangy library. Use the fastapi-limiter library with a sliding/floating window. Adding the Code to app/modules/security/ratelimit.py. Get the IP via X-Forwarded-For / CF-Connecting-IP (We using Cloudflare as Proxy and Safeline WAF). Send 429 Code to the user when hitting the limit. Code should be simple and understandable.

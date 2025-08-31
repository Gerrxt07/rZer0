"""
Configuration module for rZer0 application.

This module handles loading environment variables from .env file
and provides configuration with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv


class Config:
    """Configuration class that loads environment variables with defaults."""
    
    def __init__(self):
        """Initialize configuration by loading .env file."""
        # Load .env file from the project root
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        
        # Application Configuration
        self.APP_NAME: str = os.getenv('APP_NAME', 'rZer0')
        self.APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
        self.APP_DESCRIPTION: str = os.getenv(
            'APP_DESCRIPTION', 
            'A simple FastAPI application running with rloop and granian.'
        )
        
        self.DOCS_URL: Optional[str] = os.getenv('DOCS_URL', None)
        self.REDOC_URL: Optional[str] = os.getenv('REDOC_URL', None)
        self.OPENAPI_URL: str = os.getenv('OPENAPI_URL', '/openapi.json')
        
        # Database Configuration (for future use)
        self.DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL')
        
        # Redis/Dragonfly Configuration (for future use)
        self.REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        # Security Configuration
        self.SECRET_KEY: Optional[str] = os.getenv('SECRET_KEY')
        
        # CORS Configuration
        self.CORS_ALLOW_ORIGINS: Optional[str] = os.getenv('CORS_ALLOW_ORIGINS')
        self.CORS_ALLOW_CREDENTIALS: bool = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
        self.CORS_ALLOW_METHODS: str = os.getenv('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS,HEAD,PATCH')
        self.CORS_ALLOW_HEADERS: str = os.getenv('CORS_ALLOW_HEADERS', '*')
        
        # Security Headers Configuration
        self.SECURITY_HSTS_MAX_AGE: int = int(os.getenv('SECURITY_HSTS_MAX_AGE', '31536000'))
        self.SECURITY_HSTS_INCLUDE_SUBDOMAINS: bool = os.getenv('SECURITY_HSTS_INCLUDE_SUBDOMAINS', 'true').lower() == 'true'
        self.SECURITY_HSTS_PRELOAD: bool = os.getenv('SECURITY_HSTS_PRELOAD', 'true').lower() == 'true'
        self.SECURITY_FRAME_OPTIONS: str = os.getenv('SECURITY_FRAME_OPTIONS', 'DENY')
        self.SECURITY_CSP_POLICY: Optional[str] = os.getenv('SECURITY_CSP_POLICY')
        
        # Multiprocessing Configuration
        self.WORKERS: int = int(os.getenv('WORKERS', '4'))
        self.RUNTIME_THREADS: int = int(os.getenv('RUNTIME_THREADS', '4'))
        
    def get_cors_origins(self) -> List[str]:
        """Get CORS allowed origins as a list."""
        if self.CORS_ALLOW_ORIGINS:
            return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(',')]
        return []
    
    def get_cors_methods(self) -> List[str]:
        """Get CORS allowed methods as a list."""
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(',')]
    
    def get_cors_headers(self) -> List[str]:
        """Get CORS allowed headers as a list."""
        if self.CORS_ALLOW_HEADERS == '*':
            return ['*']
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(',')]

# Create a global config instance
config = Config()
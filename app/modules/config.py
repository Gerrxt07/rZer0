"""
Configuration module for rZer0 application.

This module handles loading environment variables from .env file
and provides configuration with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional

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
        
        # Multiprocessing Configuration
        self.WORKERS: int = int(os.getenv('WORKERS', '4'))
        self.RUNTIME_THREADS: int = int(os.getenv('RUNTIME_THREADS', '4'))

# Create a global config instance
config = Config()
"""
Configuration module for rZer0 application.

This module handles loading environment variables from .env file
with validation, type safety, and environment-specific configurations.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Union, Literal
from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class Config(BaseSettings):
    """Configuration class that loads environment variables with validation and defaults."""
    
    # Environment Configuration
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment (development, staging, production)"
    )
    
    # Application Configuration
    APP_NAME: str = Field(
        default="rZer0",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    APP_DESCRIPTION: str = Field(
        default="A simple FastAPI application running with rloop and granian.",
        description="Application description"
    )
    
    # API Documentation Configuration
    DOCS_URL: Optional[str] = Field(
        default=None,
        description="Swagger UI documentation URL (set to None to disable)"
    )
    REDOC_URL: Optional[str] = Field(
        default=None,
        description="ReDoc documentation URL (set to None to disable)"
    )
    OPENAPI_URL: str = Field(
        default="/openapi.json",
        description="OpenAPI schema URL"
    )
    
    # Database Configuration
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Database connection URL (PostgreSQL/MySQL/SQLite)"
    )
    
    # Redis/Dragonfly Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis/Dragonfly connection URL"
    )
    
    # Security Configuration
    SECRET_KEY: Optional[str] = Field(
        default=None,
        description="Secret key for JWT tokens and encryption (required for production)"
    )
    
    # CORS Configuration
    CORS_ALLOW_ORIGINS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    CORS_ALLOW_METHODS: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS,HEAD,PATCH",
        description="Allowed HTTP methods for CORS"
    )
    CORS_ALLOW_HEADERS: str = Field(
        default="*",
        description="Allowed headers for CORS"
    )
    
    # Security Headers Configuration
    SECURITY_HSTS_MAX_AGE: int = Field(
        default=31536000,
        description="HSTS max age in seconds (1 year default)"
    )
    SECURITY_HSTS_INCLUDE_SUBDOMAINS: bool = Field(
        default=True,
        description="Include subdomains in HSTS policy"
    )
    SECURITY_HSTS_PRELOAD: bool = Field(
        default=True,
        description="Enable HSTS preload"
    )
    SECURITY_FRAME_OPTIONS: str = Field(
        default="DENY",
        description="X-Frame-Options header value"
    )
    SECURITY_CSP_POLICY: Optional[str] = Field(
        default=None,
        description="Content Security Policy header value"
    )
    
    # Server Configuration
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    PORT: int = Field(
        default=8000,
        description="Server port number",
        ge=1,
        le=65535
    )
    WORKERS: int = Field(
        default=4,
        description="Number of worker processes",
        ge=1,
        le=32
    )
    RUNTIME_THREADS: int = Field(
        default=4,
        description="Number of runtime threads per worker",
        ge=1,
        le=16
    )
    BACKLOG: int = Field(
        default=2048,
        description="Socket backlog size",
        ge=128,
        le=8192
    )
    
    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="DEBUG",
        description="Logging level"
    )
    LOG_DIR: str = Field(
        default="logs",
        description="Directory for log files"
    )
    LOG_FILE_MAX_SIZE: int = Field(
        default=10,
        description="Maximum size per log file in MB",
        ge=1,
        le=1000
    )
    LOG_FILE_RETENTION: int = Field(
        default=7,
        description="Log file retention period in days",
        ge=1,
        le=365
    )
    LOG_ERROR_FILE_MAX_SIZE: int = Field(
        default=5,
        description="Maximum size per error log file in MB",
        ge=1,
        le=1000
    )
    LOG_ERROR_FILE_RETENTION: int = Field(
        default=30,
        description="Error log file retention period in days",
        ge=1,
        le=365
    )
    LOG_ENABLE_CONSOLE: bool = Field(
        default=True,
        description="Enable console logging"
    )
    LOG_ENABLE_FILE: bool = Field(
        default=True,
        description="Enable file logging"
    )
    
    # Async Logging Configuration
    LOG_ASYNC_ENABLED: bool = Field(
        default=True,
        description="Enable asynchronous logging for better performance"
    )
    LOG_ASYNC_FALLBACK: bool = Field(
        default=True,
        description="Fallback to synchronous logging if async queue is full"
    )
    LOG_ASYNC_QUEUE_SIZE: int = Field(
        default=1000,
        description="Maximum number of queued log messages",
        ge=100,
        le=10000
    )
    LOG_ASYNC_SHUTDOWN_TIMEOUT: float = Field(
        default=2.0,
        description="Timeout for graceful shutdown of async logging thread",
        ge=0.1,
        le=30.0
    )
    
    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        """Initialize configuration by loading environment-specific .env file."""
        # Load environment-specific .env file before calling super().__init__
        self._load_environment_files()
        super().__init__(**kwargs)
    
    def _load_environment_files(self):
        """Load environment-specific .env files."""
        project_root = Path(__file__).parent.parent.parent
        env_name = os.getenv('ENVIRONMENT', 'development')
        
        # Load environment-specific .env file first, then fallback to .env
        env_files = [
            project_root / f'.env.{env_name}',
            project_root / '.env'
        ]
        
        for env_file in env_files:
            if env_file.exists():
                load_dotenv(env_file, override=False)  # Don't override already set variables
                break
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format if provided."""
        if v and not v.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            raise ValueError('DATABASE_URL must start with postgresql://, mysql://, or sqlite:///')
        return v
    
    @field_validator('REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('REDIS_URL must start with redis:// or rediss://')
        return v
    
    @model_validator(mode='after')
    def validate_environment_requirements(self):
        """Validate that required environment variables are set based on environment."""
        if self.ENVIRONMENT in ['production', 'staging'] and not self.SECRET_KEY:
            raise ValueError(f'SECRET_KEY is required for {self.ENVIRONMENT} environment')
        return self
    
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
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == 'production'
    
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT == 'staging'


def create_config() -> Config:
    """Create and validate configuration instance with proper error handling."""
    try:
        return Config()
    except ValidationError as e:
        print(f"Configuration validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected configuration error: {e}", file=sys.stderr)
        sys.exit(1)


# Create a global config instance
config = create_config()
#!/usr/bin/env python3
"""
Environment validation utility for rZer0 application.

This script validates the environment configuration and checks for
missing or invalid environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

try:
    from app.modules.config import Config, create_config
    from pydantic import ValidationError
except ImportError as e:
    print(f"Error importing configuration: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)


def check_environment_files() -> Dict[str, bool]:
    """Check which environment files exist."""
    project_root = Path(__file__).parent
    env_files = {
        ".env": project_root / ".env",
        ".env.development": project_root / ".env.development", 
        ".env.staging": project_root / ".env.staging",
        ".env.production": project_root / ".env.production",
        ".env.example": project_root / ".env.example"
    }
    
    return {name: path.exists() for name, path in env_files.items()}


def validate_environment(environment: str = None) -> tuple[bool, List[str]]:
    """Validate environment configuration."""
    if environment:
        os.environ["ENVIRONMENT"] = environment
    
    errors = []
    
    try:
        config = create_config()
        print(f"✅ Configuration loaded successfully for environment: {config.ENVIRONMENT}")
        
        # Additional validations
        if config.is_production() or config.is_staging():
            if not config.SECRET_KEY:
                errors.append("SECRET_KEY is required for production/staging")
        
        if config.DATABASE_URL:
            if not config.DATABASE_URL.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
                errors.append("DATABASE_URL has invalid format")
        
        if not config.REDIS_URL.startswith(('redis://', 'rediss://')):
            errors.append("REDIS_URL has invalid format")
        
        # Check server configuration
        if not (1 <= config.PORT <= 65535):
            errors.append(f"PORT must be between 1 and 65535, got {config.PORT}")
        
        if not (1 <= config.WORKERS <= 32):
            errors.append(f"WORKERS must be between 1 and 32, got {config.WORKERS}")
        
        return len(errors) == 0, errors
        
    except ValidationError as e:
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            message = error["msg"]
            errors.append(f"{field}: {message}")
        
        return False, errors
    
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        return False, errors


def generate_secret_key() -> str:
    """Generate a secure secret key."""
    import secrets
    return secrets.token_urlsafe(32)


def main():
    """Main validation function."""
    print("🔍 rZer0 Environment Validation Utility")
    print("=" * 50)
    
    # Check environment files
    print("\n📁 Environment Files:")
    env_files = check_environment_files()
    for name, exists in env_files.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {name}")
    
    if not any(env_files[key] for key in [".env", ".env.development", ".env.staging", ".env.production"]):
        print("\n⚠️  Warning: No environment files found!")
        print("   Copy .env.example to .env and configure it for your environment.")
    
    # Validate each environment
    environments = ["development", "staging", "production"]
    
    for env in environments:
        print(f"\n🔧 Validating {env} environment:")
        print("-" * 30)
        
        is_valid, errors = validate_environment(env)
        
        if is_valid:
            print(f"✅ {env.capitalize()} environment is valid")
        else:
            print(f"❌ {env.capitalize()} environment has errors:")
            for error in errors:
                print(f"   - {error}")
    
    # Generate secret key if needed
    if not os.getenv("SECRET_KEY"):
        print(f"\n🔑 Generated SECRET_KEY for you:")
        print(f"   {generate_secret_key()}")
        print("   Add this to your .env file: SECRET_KEY=<generated_key>")
    
    print("\n✨ Validation complete!")


if __name__ == "__main__":
    main()

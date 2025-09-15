# Environment Configuration Renewal - rZer0

This document describes the comprehensive renewal of environment variable management in the rZer0 codebase.

## 🎯 Overview

The environment variable system has been completely modernized with:
- **Type safety** using Pydantic validation
- **Environment-specific configurations** (development, staging, production)
- **Comprehensive validation** and error handling
- **Enhanced shell scripts** with .env support
- **Centralized configuration** management

## 🔧 Key Improvements

### 1. Type-Safe Configuration System
- Replaced manual `os.getenv()` calls with Pydantic `BaseSettings`
- Added field validation with constraints and descriptions
- Implemented required variable validation based on environment
- Added proper error handling with clear error messages

### 2. Environment-Specific Configurations
- **`.env.development`** - Development settings with debug logging and relaxed security
- **`.env.staging`** - Staging settings with moderate security and detailed logging
- **`.env.production`** - Production settings with strict security and optimized performance

### 3. Enhanced Shell Scripts
- **`start.sh`** - Production startup script with .env support and validation
- **`start-dev.sh`** - Development startup script with hot reload and debug features
- Both scripts now load environment-specific .env files automatically

### 4. Validation and Utilities
- **`validate-env.py`** - Environment validation utility
- Checks for missing required variables
- Validates configuration format and constraints
- Generates secure secret keys

## 📁 File Structure

```
├── .env.example          # Comprehensive configuration template
├── .env.development      # Development environment settings
├── .env.staging         # Staging environment settings  
├── .env.production      # Production environment settings
├── start.sh             # Enhanced production startup script
├── start-dev.sh         # New development startup script
├── validate-env.py      # Environment validation utility
├── requirements.txt     # Updated with pydantic dependency
└── app/modules/config.py # Completely rewritten with Pydantic
```

## 🚀 Quick Start

### 1. Setup Environment Configuration

Choose your environment and copy the appropriate template:

```bash
# For development
cp .env.development .env

# For staging  
cp .env.staging .env

# For production
cp .env.production .env

# Or start from template
cp .env.example .env
```

### 2. Configure Required Variables

For **production** and **staging** environments, you MUST set:

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to your .env file
SECRET_KEY=your-generated-secret-key-here
```

### 3. Validate Configuration

Run the validation utility to check your configuration:

```bash
python validate-env.py
```

### 4. Start the Application

**Development mode** (with hot reload):
```bash
./start-dev.sh
```

**Production mode**:
```bash
./start.sh
```

## 🔒 Security Features

### Environment-Based Validation
- **Development**: No required variables, relaxed settings
- **Staging**: Requires `SECRET_KEY`, moderate security headers
- **Production**: Requires `SECRET_KEY`, strict security headers

### Automatic Security Headers
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options
- Content Security Policy (configurable)
- CORS policy (environment-specific)

## 📊 Configuration Categories

### Application Settings
- `APP_NAME` - Application name
- `APP_VERSION` - Version string
- `APP_DESCRIPTION` - Application description
- `ENVIRONMENT` - Environment type (development/staging/production)

### API Documentation
- `DOCS_URL` - Swagger UI URL (disabled in production)
- `REDOC_URL` - ReDoc URL (disabled in production)
- `OPENAPI_URL` - OpenAPI schema URL

### Database & Cache
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis/Dragonfly connection URL

### Security
- `SECRET_KEY` - JWT/encryption secret (required for staging/production)
- `CORS_*` - CORS policy configuration
- `SECURITY_*` - Security headers configuration

### Server Configuration
- `HOST` - Server bind address
- `PORT` - Server port
- `WORKERS` - Number of worker processes
- `RUNTIME_THREADS` - Threads per worker
- `BACKLOG` - Socket backlog size

### Logging
- `LOG_LEVEL` - Logging verbosity
- `LOG_DIR` - Log file directory
- `LOG_*` - Comprehensive logging configuration
- `LOG_ASYNC_*` - Async logging for performance

## 🔄 Migration Guide

### From Old System
The old system used direct `os.getenv()` calls. The new system:

1. **Centralizes** all configuration in `config.py`
2. **Validates** types and constraints automatically
3. **Supports** environment-specific settings
4. **Provides** clear error messages for misconfigurations

### Breaking Changes
- Configuration now uses Pydantic validation
- Some environment variables have new validation constraints
- Shell scripts now require .env files for full functionality

### Backwards Compatibility
- Old environment variables still work as fallbacks
- System environment variables override .env files
- Graceful degradation when .env files are missing

## 🧪 Testing Your Configuration

### 1. Validate Environment
```bash
python validate-env.py
```

### 2. Test Each Environment
```bash
# Test development
ENVIRONMENT=development python validate-env.py

# Test staging
ENVIRONMENT=staging python validate-env.py

# Test production  
ENVIRONMENT=production python validate-env.py
```

### 3. Test Application Startup
```bash
# Development
./start-dev.sh

# Production
./start.sh
```

### 4. Verify API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# API docs (if enabled)
curl http://localhost:8000/docs
```

## 🐛 Troubleshooting

### Common Issues

**Configuration Validation Error**
- Check the error message from `validate-env.py`
- Ensure required variables are set for your environment
- Verify environment variable formats (URLs, ports, etc.)

**Missing .env File**
- Copy from `.env.example` or environment-specific template
- Shell scripts will warn but continue with system environment variables

**Permission Denied on Scripts**
- Make scripts executable: `chmod +x start.sh start-dev.sh validate-env.py`

**Port Already in Use**
- Change `PORT` in your .env file
- Kill existing processes: `pkill -f granian`

### Debug Mode
Set `LOG_LEVEL=DEBUG` in your .env file for detailed logging.

## 🎉 Benefits

### For Developers
- **Type safety** prevents configuration errors
- **Environment-specific** settings eliminate manual switching
- **Clear documentation** in configuration fields
- **Hot reload** in development mode

### For Operations
- **Validation** catches deployment issues early
- **Security** enforced by environment-specific settings
- **Monitoring** with comprehensive logging options
- **Performance** with optimized production settings

### For Security
- **Required secrets** validation for production
- **Environment isolation** prevents accidental exposure
- **Security headers** automatically configured
- **CORS policies** enforced per environment

## 📚 Additional Resources

- **Pydantic Documentation**: https://pydantic-docs.helpmanual.io/
- **FastAPI Configuration**: https://fastapi.tiangolo.com/advanced/settings/
- **Environment Variables Best Practices**: https://12factor.net/config

---

*This renewal provides a robust, type-safe, and environment-aware configuration system that scales from development to production while maintaining security and performance.*

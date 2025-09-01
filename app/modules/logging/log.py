"""
Advanced logging module for rZer0 using loguru and colorama.

This module provides a comprehensive yet simple logging system that supports:
- Colored console output using colorama
- Structured logging with loguru
- File logging with automatic rotation
- Different log levels with appropriate colors
- Easy integration with existing and future code

Usage:
    from app.modules.logging import logger
    
    logger.info("Application started")
    logger.error("Something went wrong")
    logger.debug("Debug information")
"""

import sys
import os
from pathlib import Path
from loguru import logger as loguru_logger
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def get_config():
    """Get configuration values for logging."""
    try:
        from ..config import config
        return config
    except ImportError:
        # Fallback to environment variables if config is not available
        from dotenv import load_dotenv
        load_dotenv()
        return None


class LoggingSetup:
    """Centralized logging setup for the rZer0 application."""
    
    def __init__(self):
        self.logger = loguru_logger
        self.config = get_config()
        self._setup_logging()
    
    def _get_config_value(self, key: str, default):
        """Get configuration value from config object or environment."""
        if self.config and hasattr(self.config, key):
            return getattr(self.config, key)
        return os.getenv(key, default)
    
    def _setup_logging(self):
        """Configure loguru with console and file handlers."""
        # Remove default handler
        self.logger.remove()
        
        # Get configuration values
        log_level = self._get_config_value('LOG_LEVEL', 'DEBUG')
        log_dir = Path(self._get_config_value('LOG_DIR', 'logs'))
        enable_console = str(self._get_config_value('LOG_ENABLE_CONSOLE', 'true')).lower() == 'true'
        enable_file = str(self._get_config_value('LOG_ENABLE_FILE', 'true')).lower() == 'true'
        
        log_file_max_size = self._get_config_value('LOG_FILE_MAX_SIZE', '10 MB')
        log_file_retention = self._get_config_value('LOG_FILE_RETENTION', '7 days')
        log_error_file_max_size = self._get_config_value('LOG_ERROR_FILE_MAX_SIZE', '5 MB')
        log_error_file_retention = self._get_config_value('LOG_ERROR_FILE_RETENTION', '30 days')
        
        # Create log directory
        if enable_file:
            log_dir.mkdir(exist_ok=True)
        
        # Console handler with colors - using loguru's built-in formatting
        if enable_console:
            console_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
            
            self.logger.add(
                sys.stderr,
                format=console_format,
                level=log_level,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )
        
        # File handlers
        if enable_file:
            file_format = (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}"
            )
            
            # File handler for all logs with rotation
            self.logger.add(
                log_dir / "rzero.log",
                format=file_format,
                level=log_level,
                rotation=log_file_max_size,
                retention=log_file_retention,
                compression="zip",
                backtrace=True,
                diagnose=True,
                encoding="utf-8"
            )
            
            # Separate error log file
            self.logger.add(
                log_dir / "rzero_errors.log",
                format=file_format,
                level="ERROR",
                rotation=log_error_file_max_size,
                retention=log_error_file_retention,
                compression="zip",
                backtrace=True,
                diagnose=True,
                encoding="utf-8"
            )
    
    def get_logger(self):
        """Get the configured logger instance."""
        return self.logger


# Initialize logging setup
_logging_setup = LoggingSetup()
logger = _logging_setup.get_logger()


def get_logger(name: str = None):
    """
    Get a logger instance optionally bound to a specific name.
    
    Args:
        name: Optional name to bind to the logger (e.g., module name)
    
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_function_call(func_name: str, args: tuple = None, kwargs: dict = None):
    """
    Helper function to log function calls with arguments.
    
    Args:
        func_name: Name of the function being called
        args: Positional arguments
        kwargs: Keyword arguments
    """
    arg_str = ""
    if args:
        arg_str += f"args={args}"
    if kwargs:
        if arg_str:
            arg_str += ", "
        arg_str += f"kwargs={kwargs}"
    
    if arg_str:
        logger.debug(f"Calling {func_name}({arg_str})")
    else:
        logger.debug(f"Calling {func_name}()")


def log_function_result(func_name: str, result=None, execution_time: float = None):
    """
    Helper function to log function results and execution time.
    
    Args:
        func_name: Name of the function
        result: Return value of the function
        execution_time: Execution time in seconds
    """
    msg = f"Finished {func_name}"
    if execution_time is not None:
        msg += f" (took {execution_time:.3f}s)"
    if result is not None:
        msg += f" -> {result}"
    
    logger.debug(msg)


# Example usage and testing functions
def test_logging():
    """Test function to demonstrate logging capabilities."""
    logger.trace("This is a trace message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.success("This is a success message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test structured logging
    logger.info("User action", user_id=123, action="login", ip="192.168.1.1")
    
    # Test function logging helpers
    log_function_call("test_function", args=("arg1", "arg2"), kwargs={"key": "value"})
    log_function_result("test_function", result="success", execution_time=0.123)


if __name__ == "__main__":
    # Test the logging system
    test_logging()
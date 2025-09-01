"""
Logging module for rZer0 application.

This module provides advanced logging capabilities using loguru and colorama.
Import the logger from this module to use throughout the application.

Usage:
    from app.modules.logging import logger
    
    logger.info("Application started")
    logger.error("Something went wrong", error_code=500)
    logger.debug("Debug information")
"""

from .log import logger, get_logger, get_sync_logger, log_function_call, log_function_result, stop_async_logging

__all__ = [
    "logger",
    "get_logger", 
    "get_sync_logger",
    "log_function_call",
    "log_function_result",
    "stop_async_logging"
]
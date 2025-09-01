"""
Advanced asynchronous logging module for rZer0 using loguru and colorama.

This module provides a comprehensive yet simple logging system that supports:
- Colored console output using colorama
- Structured logging with loguru
- File logging with automatic rotation
- Different log levels with appropriate colors
- **Asynchronous/threaded logging** for zero performance impact
- Easy integration with existing and future code

Features:
- Background thread processing for all log operations
- Non-blocking log calls using thread-safe queues
- Graceful fallback to synchronous logging if async fails
- Configurable queue size and timeout settings
- Proper shutdown handling for thread cleanup

Usage:
    from app.modules.logging import logger
    
    logger.info("Application started")  # Non-blocking, queued
    logger.error("Something went wrong")  # Non-blocking, queued
    logger.debug("Debug information")  # Non-blocking, queued
"""

import sys
import os
import threading
import queue
import time
import atexit
from pathlib import Path
from typing import Any, Dict, Optional, Callable
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


class AsyncLogProcessor:
    """Background thread processor for asynchronous logging."""
    
    def __init__(self, queue_size: int = 1000):
        self.queue = queue.Queue(maxsize=queue_size)
        self.shutdown_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.is_running = False
    
    def start(self):
        """Start the background logging thread."""
        if self.is_running:
            return
            
        self.thread = threading.Thread(target=self._process_logs, daemon=True)
        self.thread.start()
        self.is_running = True
        
        # Register cleanup on exit
        atexit.register(self.stop)
    
    def stop(self, timeout: float = 2.0):
        """Stop the background logging thread gracefully."""
        if not self.is_running:
            return
            
        self.shutdown_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
        self.is_running = False
    
    def put_log(self, log_func: Callable, message: str, *args, **kwargs) -> bool:
        """
        Queue a log message for background processing.
        
        Args:
            log_func: The loguru logger function to call (e.g., logger.info)
            message: Log message
            *args, **kwargs: Additional arguments for the log function
            
        Returns:
            bool: True if queued successfully, False if queue is full
        """
        try:
            log_entry = {
                'func': log_func,
                'message': message,
                'args': args,
                'kwargs': kwargs,
                'timestamp': time.time()
            }
            self.queue.put_nowait(log_entry)
            return True
        except queue.Full:
            return False
    
    def _process_logs(self):
        """Background thread worker that processes queued log messages."""
        while not self.shutdown_event.is_set():
            try:
                # Wait for log entries with timeout to check shutdown event
                log_entry = self.queue.get(timeout=0.1)
                
                # Process the log entry
                func = log_entry['func']
                message = log_entry['message']
                args = log_entry['args']
                kwargs = log_entry['kwargs']
                
                # Call the actual logging function
                func(message, *args, **kwargs)
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                # In case of logging errors, write to stderr as fallback
                print(f"Async logging error: {e}", file=sys.stderr)


class AsyncLoggerWrapper:
    """Wrapper that provides async logging interface compatible with loguru."""
    
    def __init__(self, processor: AsyncLogProcessor, sync_logger, fallback_to_sync: bool = True):
        self.processor = processor
        self.sync_logger = sync_logger
        self.fallback_to_sync = fallback_to_sync
    
    def _async_log(self, level: str, message: str, *args, **kwargs):
        """Internal method to handle async logging with fallback."""
        log_func = getattr(self.sync_logger, level.lower())
        
        # Try to queue the log message
        if self.processor.is_running and self.processor.put_log(log_func, message, *args, **kwargs):
            return
        
        # Fallback to synchronous logging if async fails or is disabled
        if self.fallback_to_sync:
            log_func(message, *args, **kwargs)
    
    def trace(self, message: str, *args, **kwargs):
        """Log trace level message."""
        self._async_log('trace', message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug level message."""
        self._async_log('debug', message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info level message."""
        self._async_log('info', message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs):
        """Log success level message."""
        self._async_log('success', message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning level message."""
        self._async_log('warning', message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error level message."""
        self._async_log('error', message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical level message."""
        self._async_log('critical', message, *args, **kwargs)
    
    def bind(self, **kwargs):
        """Bind additional context to logger."""
        bound_sync_logger = self.sync_logger.bind(**kwargs)
        return AsyncLoggerWrapper(self.processor, bound_sync_logger, self.fallback_to_sync)
    
    def opt(self, **kwargs):
        """Configure logger options."""
        opted_sync_logger = self.sync_logger.opt(**kwargs)
        return AsyncLoggerWrapper(self.processor, opted_sync_logger, self.fallback_to_sync)


class LoggingSetup:
    """Centralized logging setup for the rZer0 application with async support."""
    
    def __init__(self):
        self.sync_logger = loguru_logger
        self.config = get_config()
        
        # Get async configuration
        self.async_enabled = str(self._get_config_value('LOG_ASYNC_ENABLED', 'true')).lower() == 'true'
        self.fallback_to_sync = str(self._get_config_value('LOG_ASYNC_FALLBACK', 'true')).lower() == 'true'
        queue_size = int(self._get_config_value('LOG_ASYNC_QUEUE_SIZE', '1000'))
        
        # Initialize async processor with configured queue size
        self.async_processor = AsyncLogProcessor(queue_size)
        
        self._setup_logging()
        
        # Start async processor if enabled
        if self.async_enabled:
            self.async_processor.start()
        
        # Create async logger wrapper
        self.logger = AsyncLoggerWrapper(
            self.async_processor, 
            self.sync_logger, 
            self.fallback_to_sync
        )
    
    def _get_config_value(self, key: str, default):
        """Get configuration value from config object or environment."""
        if self.config and hasattr(self.config, key):
            return getattr(self.config, key)
        return os.getenv(key, default)
    
    def _setup_logging(self):
        """Configure loguru with console and file handlers."""
        # Remove default handler
        self.sync_logger.remove()
        
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
            
            self.sync_logger.add(
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
            self.sync_logger.add(
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
            self.sync_logger.add(
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
        """Get the configured logger instance (async wrapper)."""
        return self.logger
    
    def get_sync_logger(self):
        """Get the underlying synchronous loguru logger."""
        return self.sync_logger
    
    def stop_async_logging(self, timeout: float = 2.0):
        """Stop the async logging processor gracefully."""
        if self.async_enabled:
            self.async_processor.stop(timeout)


# Initialize logging setup
_logging_setup = LoggingSetup()
logger = _logging_setup.get_logger()


def get_logger(name: str = None):
    """
    Get a logger instance optionally bound to a specific name.
    
    Args:
        name: Optional name to bind to the logger (e.g., module name)
    
    Returns:
        AsyncLoggerWrapper instance
    """
    if name:
        return logger.bind(name=name)
    return logger


def get_sync_logger(name: str = None):
    """
    Get a synchronous logger instance (for cases where async is not suitable).
    
    Args:
        name: Optional name to bind to the logger
        
    Returns:
        Loguru logger instance
    """
    sync_logger = _logging_setup.get_sync_logger()
    if name:
        return sync_logger.bind(name=name)
    return sync_logger


def stop_async_logging(timeout: float = 2.0):
    """
    Stop the async logging system gracefully.
    
    Args:
        timeout: Maximum time to wait for thread shutdown
    """
    _logging_setup.stop_async_logging(timeout)


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
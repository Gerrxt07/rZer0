#!/usr/bin/env python3
"""
Example script demonstrating rZer0 logging capabilities.

This script shows how to use the logging system across different parts
of an application with various log levels and structured logging.
"""

import asyncio
import time
from app.modules.logging import logger, log_function_call, log_function_result


def example_sync_function(name: str, value: int):
    """Example synchronous function with logging."""
    log_function_call("example_sync_function", args=(name, value))
    
    start_time = time.time()
    
    logger.debug(f"Processing {name} with value {value}")
    
    # Simulate some work
    time.sleep(0.1)
    
    result = value * 2
    logger.info(f"Processed {name}", input_value=value, result=result)
    
    execution_time = time.time() - start_time
    log_function_result("example_sync_function", result=result, execution_time=execution_time)
    
    return result


async def example_async_function(items: list):
    """Example asynchronous function with logging."""
    log_function_call("example_async_function", args=(items,))
    
    start_time = time.time()
    
    logger.debug(f"Processing {len(items)} items asynchronously")
    
    results = []
    for i, item in enumerate(items):
        logger.trace(f"Processing item {i}: {item}")
        # Simulate async work
        await asyncio.sleep(0.01)
        result = item.upper() if isinstance(item, str) else str(item)
        results.append(result)
    
    logger.success(f"Successfully processed all items", count=len(results))
    
    execution_time = time.time() - start_time
    log_function_result("example_async_function", result=len(results), execution_time=execution_time)
    
    return results


def example_error_handling():
    """Example of error handling with logging."""
    logger.info("Demonstrating error handling")
    
    try:
        # Intentional error for demonstration
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Division by zero error occurred", error=str(e), function="example_error_handling")
        return None
    except Exception as e:
        logger.critical(f"Unexpected error occurred", error=str(e), error_type=type(e).__name__)
        return None


def demonstrate_log_levels():
    """Demonstrate different log levels."""
    logger.info("=== Log Levels Demonstration ===")
    
    logger.trace("TRACE: Very detailed debugging information")
    logger.debug("DEBUG: Detailed debugging information")
    logger.info("INFO: General information about program execution")
    logger.success("SUCCESS: Successful operation completed")
    logger.warning("WARNING: Something unexpected happened")
    logger.error("ERROR: An error occurred but the program continues")
    logger.critical("CRITICAL: A serious error occurred")


def demonstrate_structured_logging():
    """Demonstrate structured logging with additional context."""
    logger.info("=== Structured Logging Demonstration ===")
    
    # Log with additional structured data
    logger.info("User login attempt", 
                user_id=12345, 
                username="john_doe", 
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                timestamp=time.time())
    
    logger.warning("Rate limit warning",
                   endpoint="/api/users",
                   method="GET",
                   rate_limit=100,
                   current_requests=95,
                   remaining=5)
    
    logger.error("Database connection failed",
                 database="postgresql",
                 host="localhost",
                 port=5432,
                 timeout=5.0,
                 retry_count=3)


async def main():
    """Main function demonstrating various logging scenarios."""
    logger.info("Starting rZer0 logging demonstration")
    
    # Basic log levels
    demonstrate_log_levels()
    
    # Structured logging
    demonstrate_structured_logging()
    
    # Function call logging
    logger.info("=== Function Call Logging ===")
    sync_result = example_sync_function("test_item", 42)
    
    # Async function logging
    logger.info("=== Async Function Logging ===")
    async_result = await example_async_function(["hello", "world", 123, "python"])
    
    # Error handling
    logger.info("=== Error Handling Logging ===")
    error_result = example_error_handling()
    
    logger.success("rZer0 logging demonstration completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
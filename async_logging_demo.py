#!/usr/bin/env python3
"""
Comprehensive demonstration of the new asynchronous logging system.

This script shows:
1. Performance comparison between sync and async logging
2. Async logging capabilities with different log levels
3. Queue handling and fallback mechanisms
4. Thread safety and concurrent logging
5. Proper shutdown handling

Usage:
    python async_logging_demo.py
"""

import asyncio
import concurrent.futures
import time
import threading
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.logging import get_logger, get_sync_logger, stop_async_logging
from app.modules.config import config

def performance_benchmark():
    """Benchmark async vs sync logging performance."""
    print("\n" + "="*60)
    print("🚀 ASYNC LOGGING PERFORMANCE BENCHMARK")
    print("="*60)
    
    # Get both logger types
    async_logger = get_logger("perf_test_async")
    sync_logger = get_sync_logger("perf_test_sync")
    
    num_logs = 1000
    message = "Performance test message with some metadata"
    
    print(f"Testing {num_logs} log messages...")
    
    # Benchmark synchronous logging
    print("\n📊 Testing SYNCHRONOUS logging...")
    sync_start = time.perf_counter()
    
    for i in range(num_logs):
        sync_logger.info(f"{message} #{i}", iteration=i, test_type="sync")
    
    sync_end = time.perf_counter()
    sync_duration = sync_end - sync_start
    
    print(f"   ⏱️  Sync logging took: {sync_duration:.4f} seconds")
    print(f"   📈 Throughput: {num_logs / sync_duration:.1f} logs/second")
    
    # Small delay to let async queue process
    time.sleep(0.1)
    
    # Benchmark asynchronous logging
    print("\n📊 Testing ASYNCHRONOUS logging...")
    async_start = time.perf_counter()
    
    for i in range(num_logs):
        async_logger.info(f"{message} #{i}", iteration=i, test_type="async")
    
    async_end = time.perf_counter()
    async_duration = async_end - async_start
    
    print(f"   ⏱️  Async logging took: {async_duration:.4f} seconds")
    print(f"   📈 Throughput: {num_logs / async_duration:.1f} logs/second")
    
    # Calculate improvement
    improvement = ((sync_duration - async_duration) / sync_duration) * 100
    speedup = sync_duration / async_duration
    
    print(f"\n🎯 RESULTS:")
    print(f"   ⚡ Performance improvement: {improvement:.1f}%")
    print(f"   🚀 Speedup factor: {speedup:.2f}x")
    
    if improvement > 0:
        print(f"   ✅ Async logging is {improvement:.1f}% faster!")
    else:
        print(f"   ⚠️  Async logging overhead: {abs(improvement):.1f}%")
    
    # Allow time for async processing to complete
    print(f"\n⏳ Waiting for async queue to process...")
    time.sleep(2)
    
    return {
        'sync_duration': sync_duration,
        'async_duration': async_duration,
        'improvement': improvement,
        'speedup': speedup
    }


def demonstrate_log_levels():
    """Demonstrate all log levels with async logging."""
    print("\n" + "="*60)
    print("📝 ASYNC LOG LEVELS DEMONSTRATION")
    print("="*60)
    
    logger = get_logger("demo")
    
    print("Testing all log levels (these are queued and processed asynchronously):")
    
    logger.trace("🔍 TRACE: Very detailed diagnostic information")
    logger.debug("🐛 DEBUG: Detailed information for debugging")
    logger.info("ℹ️  INFO: General information about application flow")
    logger.success("✅ SUCCESS: Operation completed successfully")
    logger.warning("⚠️  WARNING: Something unexpected happened")
    logger.error("❌ ERROR: An error occurred but app can continue")
    logger.critical("💀 CRITICAL: Serious error that might stop the app")
    
    # Structured logging example
    logger.info("🌐 API Request", 
                method="POST", 
                endpoint="/api/users", 
                user_id=12345,
                ip_address="192.168.1.100",
                response_time=0.045)
    
    print("\n✨ All log messages have been queued for asynchronous processing!")
    print("Check the console and log files to see the colored output.")


def demonstrate_concurrent_logging():
    """Demonstrate thread-safe concurrent logging."""
    print("\n" + "="*60)
    print("🔄 CONCURRENT LOGGING DEMONSTRATION")
    print("="*60)
    
    logger = get_logger("concurrent_test")
    
    def worker_thread(worker_id: int, num_messages: int):
        """Worker thread that generates log messages."""
        thread_logger = get_logger(f"worker_{worker_id}")
        
        for i in range(num_messages):
            thread_logger.info(f"Worker {worker_id} message {i+1}", 
                              worker_id=worker_id, 
                              message_num=i+1,
                              thread_id=threading.get_ident())
            
            # Small delay to simulate work
            time.sleep(0.01)
        
        thread_logger.success(f"Worker {worker_id} completed {num_messages} messages")
    
    num_workers = 5
    messages_per_worker = 10
    total_messages = num_workers * messages_per_worker
    
    print(f"Starting {num_workers} concurrent threads...")
    print(f"Each thread will log {messages_per_worker} messages ({total_messages} total)")
    
    start_time = time.perf_counter()
    
    # Start worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for worker_id in range(num_workers):
            future = executor.submit(worker_thread, worker_id, messages_per_worker)
            futures.append(future)
        
        # Wait for all workers to complete
        concurrent.futures.wait(futures)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    logger.success(f"Concurrent logging test completed", 
                   duration=f"{duration:.3f}s",
                   total_messages=total_messages,
                   throughput=f"{total_messages / duration:.1f} msgs/sec")
    
    print(f"\n✅ All {num_workers} threads completed in {duration:.3f} seconds")
    print(f"📈 Throughput: {total_messages / duration:.1f} messages/second")


async def demonstrate_async_context():
    """Demonstrate logging in async context."""
    print("\n" + "="*60)
    print("🔄 ASYNC CONTEXT DEMONSTRATION")
    print("="*60)
    
    logger = get_logger("async_context")
    
    async def async_operation(operation_id: int, delay: float):
        """Simulate an async operation with logging."""
        logger.info(f"Starting async operation {operation_id}", 
                    operation_id=operation_id, 
                    expected_delay=delay)
        
        await asyncio.sleep(delay)
        
        logger.success(f"Completed async operation {operation_id}",
                       operation_id=operation_id,
                       actual_delay=delay)
        
        return f"result_{operation_id}"
    
    # Run multiple async operations concurrently
    operations = [
        async_operation(1, 0.1),
        async_operation(2, 0.2),
        async_operation(3, 0.15),
        async_operation(4, 0.05),
        async_operation(5, 0.3)
    ]
    
    print("Starting 5 concurrent async operations...")
    start_time = time.perf_counter()
    
    results = await asyncio.gather(*operations)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    logger.info("All async operations completed", 
                results=results, 
                total_duration=f"{duration:.3f}s")
    
    print(f"✅ All async operations completed in {duration:.3f} seconds")


def main():
    """Main demonstration function."""
    print("🎯 rZer0 Asynchronous Logging System Demo")
    print("=========================================")
    print("\nThis demo showcases the new async logging capabilities:")
    print("• Zero-performance-impact logging with background threads")
    print("• Thread-safe concurrent logging")
    print("• Graceful fallback to synchronous logging")
    print("• Configurable queue sizes and timeouts")
    print("• Proper shutdown handling")
    
    # Show configuration
    print(f"\n🔧 Current Configuration:")
    print(f"   Async Enabled: {config.LOG_ASYNC_ENABLED}")
    print(f"   Queue Size: {config.LOG_ASYNC_QUEUE_SIZE}")
    print(f"   Fallback Enabled: {config.LOG_ASYNC_FALLBACK}")
    print(f"   Log Level: {config.LOG_LEVEL}")
    print(f"   Log Directory: {config.LOG_DIR}")
    
    try:
        # Performance benchmark
        perf_results = performance_benchmark()
        
        # Demonstrate log levels
        demonstrate_log_levels()
        
        # Demonstrate concurrent logging
        demonstrate_concurrent_logging()
        
        # Demonstrate async context
        asyncio.run(demonstrate_async_context())
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRATION COMPLETED")
        print("="*60)
        print(f"Performance improvement: {perf_results['improvement']:.1f}%")
        print(f"Speedup factor: {perf_results['speedup']:.2f}x")
        print("\nCheck the following for logs:")
        print(f"• Console output (with colors)")
        print(f"• {config.LOG_DIR}/rzero.log (all logs)")
        print(f"• {config.LOG_DIR}/rzero_errors.log (errors only)")
        
        # Wait a bit for async processing
        print(f"\n⏳ Allowing time for async queue to finish processing...")
        time.sleep(3)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
    finally:
        # Ensure proper cleanup
        print("\n🔧 Stopping async logging system...")
        stop_async_logging(timeout=5.0)
        print("✅ Cleanup completed")


if __name__ == "__main__":
    main()
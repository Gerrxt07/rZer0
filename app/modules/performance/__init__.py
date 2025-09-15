"""
Performance optimization modules for rZer0.
"""

from .compression import setup_compression_middleware
from .caching import CacheManager, cache_response
from .monitoring import setup_performance_monitoring

__all__ = [
    'setup_compression_middleware',
    'CacheManager', 
    'cache_response',
    'setup_performance_monitoring'
]

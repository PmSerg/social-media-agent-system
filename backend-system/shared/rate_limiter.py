"""
Rate Limiter - Configuration and utilities for API rate limiting
"""

import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis.asyncio as redis
from typing import Optional, Callable, Dict, Any
import asyncio
from functools import wraps

from config import settings

logger = logging.getLogger(__name__)

# Global limiter instance
_limiter: Optional[Limiter] = None
_redis_client: Optional[redis.Redis] = None


async def init_redis_client():
    """Initialize Redis client for rate limiting storage."""
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await _redis_client.ping()
            logger.info("Redis client initialized for rate limiting")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory rate limiting: {e}")
            _redis_client = None
    
    return _redis_client


def get_rate_limiter() -> Limiter:
    """
    Get or create rate limiter instance.
    
    Returns:
        Limiter instance configured with Redis or in-memory storage
    """
    global _limiter
    
    if _limiter is None:
        # Use Redis if available, otherwise in-memory
        storage = _redis_client if _redis_client else None
        
        _limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.rate_limit_default],
            storage=storage,
            headers_enabled=True,  # Add rate limit headers to responses
            strategy="fixed-window"  # Simple fixed window strategy
        )
        
        logger.info(f"Rate limiter initialized with {'Redis' if storage else 'in-memory'} storage")
    
    return _limiter


def create_custom_limiter(
    key_func: Callable,
    rate_limit: str = "10 per minute"
) -> Limiter:
    """
    Create a custom rate limiter with specific configuration.
    
    Args:
        key_func: Function to extract key from request
        rate_limit: Rate limit string (e.g., "10 per minute")
        
    Returns:
        Configured Limiter instance
    """
    storage = _redis_client if _redis_client else None
    
    return Limiter(
        key_func=key_func,
        default_limits=[rate_limit],
        storage=storage,
        headers_enabled=True
    )


def get_user_key(request) -> str:
    """Extract user identifier from request for user-based rate limiting."""
    # Try to get user ID from various sources
    
    # Check authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Use token prefix as key (in production, decode and get user ID)
        return f"user:{auth_header[7:20]}"
    
    # Check for API key
    api_key = request.headers.get("X-API-Key", "")
    if api_key:
        return f"api:{api_key[:20]}"
    
    # Fall back to IP address
    return get_remote_address(request)


def get_command_key(request) -> str:
    """Extract command from request for command-specific rate limiting."""
    # Try to get command from request body
    try:
        if hasattr(request, "json") and request.json:
            command = request.json.get("command", "")
            if command:
                return f"cmd:{command}"
    except:
        pass
    
    # Fall back to endpoint
    return f"endpoint:{request.url.path}"


# Rate limiting decorators for async functions

def rate_limit_async(calls: int = 10, period: int = 60):
    """
    Decorator to rate limit async functions.
    
    Args:
        calls: Number of allowed calls
        period: Time period in seconds
    """
    def decorator(func):
        call_times = []
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = asyncio.get_event_loop().time()
            
            # Remove old calls outside the time window
            nonlocal call_times
            call_times = [t for t in call_times if now - t < period]
            
            # Check rate limit
            if len(call_times) >= calls:
                wait_time = period - (now - call_times[0])
                logger.warning(
                    f"Rate limit exceeded for {func.__name__}, "
                    f"waiting {wait_time:.2f}s"
                )
                await asyncio.sleep(wait_time)
                # Retry after waiting
                call_times = [t for t in call_times if now - t < period]
            
            # Record this call
            call_times.append(now)
            
            # Execute function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# Custom rate limiters for specific use cases

def get_openai_limiter() -> Limiter:
    """Get rate limiter for OpenAI API calls."""
    return create_custom_limiter(
        key_func=lambda: "openai",  # Global key for all OpenAI calls
        rate_limit="50 per minute"  # Adjust based on your tier
    )


def get_notion_limiter() -> Limiter:
    """Get rate limiter for Notion API calls."""
    return create_custom_limiter(
        key_func=lambda: "notion",  # Global key for all Notion calls
        rate_limit="3 per second"  # Notion's rate limit
    )


def get_serp_limiter() -> Limiter:
    """Get rate limiter for SerpAPI calls."""
    return create_custom_limiter(
        key_func=lambda: "serpapi",  # Global key for all SerpAPI calls
        rate_limit="100 per month"  # Free tier limit
    )


# Utility functions

async def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """
    Check if an action is within rate limit.
    
    Args:
        key: Unique key for the rate limit
        limit: Maximum number of requests
        window: Time window in seconds
        
    Returns:
        True if within limit, False otherwise
    """
    if not _redis_client:
        # Simple in-memory check (not distributed)
        return True
    
    try:
        # Use Redis INCR with expiration
        pipe = _redis_client.pipeline()
        pipe.incr(f"rate:{key}")
        pipe.expire(f"rate:{key}", window)
        results = await pipe.execute()
        
        count = results[0]
        return count <= limit
        
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Allow on error


async def get_rate_limit_status(key: str) -> Dict[str, Any]:
    """
    Get current rate limit status for a key.
    
    Args:
        key: Rate limit key
        
    Returns:
        Dictionary with current count and TTL
    """
    if not _redis_client:
        return {"count": 0, "ttl": 0, "available": True}
    
    try:
        pipe = _redis_client.pipeline()
        pipe.get(f"rate:{key}")
        pipe.ttl(f"rate:{key}")
        results = await pipe.execute()
        
        count = int(results[0] or 0)
        ttl = results[1] if results[1] > 0 else 0
        
        return {
            "count": count,
            "ttl": ttl,
            "available": count < 100  # Default limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get rate limit status: {e}")
        return {"count": 0, "ttl": 0, "available": True}


# Export functions
__all__ = [
    "init_redis_client",
    "get_rate_limiter",
    "create_custom_limiter",
    "get_user_key",
    "get_command_key",
    "rate_limit_async",
    "get_openai_limiter",
    "get_notion_limiter",
    "get_serp_limiter",
    "check_rate_limit",
    "get_rate_limit_status"
]
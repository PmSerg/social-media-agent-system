"""
OpenAI Client - Singleton client with retry logic and token tracking
"""

import logging
from typing import Optional
from openai import AsyncOpenAI
import asyncio
from functools import wraps
import time

from config import settings

logger = logging.getLogger(__name__)

# Singleton instance
_openai_client: Optional[AsyncOpenAI] = None
_token_usage = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "requests": 0
}


def get_openai_client() -> AsyncOpenAI:
    """
    Get or create singleton OpenAI client.
    
    Returns:
        AsyncOpenAI client instance
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=30.0,
            max_retries=3
        )
        logger.info("OpenAI client initialized")
    
    return _openai_client


def track_token_usage(func):
    """Decorator to track token usage from OpenAI responses."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        
        # Track usage if response has usage data
        if hasattr(result, 'usage'):
            global _token_usage
            _token_usage["prompt_tokens"] += result.usage.prompt_tokens
            _token_usage["completion_tokens"] += result.usage.completion_tokens
            _token_usage["total_tokens"] += result.usage.total_tokens
            _token_usage["requests"] += 1
            
            # Log every 10 requests
            if _token_usage["requests"] % 10 == 0:
                logger.info(
                    f"Token usage - Total: {_token_usage['total_tokens']:,}, "
                    f"Requests: {_token_usage['requests']}"
                )
        
        return result
    
    return wrapper


def get_token_usage() -> dict:
    """Get current token usage statistics."""
    return _token_usage.copy()


def reset_token_usage():
    """Reset token usage counters."""
    global _token_usage
    _token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "requests": 0
    }
    logger.info("Token usage counters reset")


async def create_chat_completion_with_retry(
    messages: list,
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
):
    """
    Create chat completion with exponential backoff retry.
    
    Args:
        messages: List of message dictionaries
        model: Model to use
        temperature: Temperature setting
        max_tokens: Maximum tokens to generate
        **kwargs: Additional parameters for OpenAI API
        
    Returns:
        Chat completion response
    """
    client = get_openai_client()
    
    # Apply token tracking decorator
    @track_token_usage
    async def _create():
        return await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    # Retry logic with exponential backoff
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            return await _create()
            
        except Exception as e:
            error_type = type(e).__name__
            
            # Don't retry on certain errors
            if "AuthenticationError" in error_type:
                logger.error("OpenAI authentication error - check API key")
                raise
            
            if "InvalidRequestError" in error_type:
                logger.error(f"Invalid request to OpenAI: {e}")
                raise
            
            # Retry on rate limit and other errors
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    f"OpenAI request failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"OpenAI request failed after {max_retries} attempts: {e}")
                raise


# Convenience function for non-async contexts
def get_sync_client():
    """
    Get a synchronous OpenAI client for non-async contexts.
    
    Note: Prefer async client when possible.
    """
    from openai import OpenAI
    return OpenAI(api_key=settings.openai_api_key)


# Export functions
__all__ = [
    "get_openai_client",
    "get_token_usage",
    "reset_token_usage",
    "create_chat_completion_with_retry",
    "track_token_usage",
    "get_sync_client"
]
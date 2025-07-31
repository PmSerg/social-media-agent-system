"""
Error Handler - Common error handling utilities with retry logic
"""

import logging
import asyncio
from typing import TypeVar, Callable, Optional, Union, Type, Tuple
from functools import wraps
import time
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryableError(Exception):
    """Base class for errors that should trigger a retry."""
    pass


class NonRetryableError(Exception):
    """Base class for errors that should not trigger a retry."""
    pass


class RateLimitError(RetryableError):
    """Error for rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class APIConnectionError(RetryableError):
    """Error for API connection issues."""
    pass


class ValidationError(NonRetryableError):
    """Error for validation failures."""
    pass


class AuthenticationError(NonRetryableError):
    """Error for authentication failures."""
    pass


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (RetryableError, ConnectionError, TimeoutError),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator to add retry logic to async functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        retryable_exceptions: Tuple of exceptions that trigger retry
        on_retry: Optional callback called on each retry with (exception, attempt)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    # Try to execute the function
                    return await func(*args, **kwargs)
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    # Check if this is the last attempt
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Special handling for rate limit errors
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = max(delay, e.retry_after)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
                    
                except NonRetryableError as e:
                    # Don't retry these errors
                    logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                    raise
                    
                except Exception as e:
                    # Unexpected error - don't retry
                    logger.error(f"{func.__name__} failed with unexpected error: {e}", exc_info=True)
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    
    return decorator


def handle_api_error(error: Exception) -> Tuple[bool, Optional[float]]:
    """
    Determine if an API error is retryable and how long to wait.
    
    Args:
        error: The exception that occurred
        
    Returns:
        Tuple of (is_retryable, retry_delay)
    """
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    # Rate limit errors
    if "rate limit" in error_str or "429" in error_str:
        # Try to extract retry-after from error message
        retry_after = None
        if "retry after" in error_str:
            try:
                # Extract number from string like "retry after 60 seconds"
                import re
                match = re.search(r'retry after (\d+)', error_str)
                if match:
                    retry_after = int(match.group(1))
            except:
                pass
        
        return True, retry_after or 60
    
    # Connection errors
    if any(term in error_str for term in ["connection", "timeout", "network", "refused"]):
        return True, 5
    
    # Temporary server errors
    if any(code in error_str for code in ["500", "502", "503", "504"]):
        return True, 10
    
    # Authentication errors - don't retry
    if any(term in error_str for term in ["authentication", "unauthorized", "401", "403"]):
        return False, None
    
    # Validation errors - don't retry
    if any(term in error_str for term in ["validation", "invalid", "400"]):
        return False, None
    
    # Default: don't retry unknown errors
    return False, None


class ErrorContext:
    """Context manager for error handling with logging."""
    
    def __init__(
        self,
        operation: str,
        reraise: bool = True,
        default_return: Optional[T] = None,
        log_level: int = logging.ERROR
    ):
        self.operation = operation
        self.reraise = reraise
        self.default_return = default_return
        self.log_level = log_level
        self.start_time = None
        
    async def __aenter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting {self.operation}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.debug(f"Completed {self.operation} in {duration:.2f}s")
            return False
        
        # Log the error
        logger.log(
            self.log_level,
            f"Error in {self.operation} after {duration:.2f}s: {exc_val}",
            exc_info=True
        )
        
        # Handle the error
        if not self.reraise:
            return True  # Suppress the exception
        
        # Check if it's retryable
        is_retryable, _ = handle_api_error(exc_val)
        
        if is_retryable:
            # Convert to RetryableError for consistent handling
            raise RetryableError(f"{self.operation} failed: {exc_val}") from exc_val
        
        return False  # Re-raise the original exception


async def safe_api_call(
    func: Callable,
    *args,
    operation: str = "API call",
    default_return: Optional[T] = None,
    **kwargs
) -> Union[T, None]:
    """
    Safely execute an API call with error handling.
    
    Args:
        func: Async function to call
        *args: Positional arguments for func
        operation: Description of the operation for logging
        default_return: Value to return on error
        **kwargs: Keyword arguments for func
        
    Returns:
        Function result or default_return on error
    """
    async with ErrorContext(operation, reraise=False, default_return=default_return):
        try:
            return await func(*args, **kwargs)
        except Exception:
            return default_return


def create_error_response(
    error: Exception,
    operation: str = "Operation",
    request_id: Optional[str] = None
) -> dict:
    """
    Create a standardized error response.
    
    Args:
        error: The exception that occurred
        operation: Description of what was being attempted
        request_id: Optional request ID for tracking
        
    Returns:
        Dictionary with error details
    """
    is_retryable, retry_after = handle_api_error(error)
    
    response = {
        "error": str(error),
        "error_type": type(error).__name__,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "retryable": is_retryable
    }
    
    if request_id:
        response["request_id"] = request_id
    
    if retry_after:
        response["retry_after"] = retry_after
    
    return response


# Export all utilities
__all__ = [
    "RetryableError",
    "NonRetryableError",
    "RateLimitError",
    "APIConnectionError",
    "ValidationError",
    "AuthenticationError",
    "with_retry",
    "handle_api_error",
    "ErrorContext",
    "safe_api_call",
    "create_error_response"
]
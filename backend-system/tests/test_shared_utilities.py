"""
Unit Tests for Shared Utilities
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime

from shared.openai_client import (
    get_openai_client,
    get_token_usage,
    reset_token_usage,
    create_chat_completion_with_retry
)
from shared.notion_client import (
    get_notion_client,
    create_task_page,
    update_task_status,
    query_tasks
)
from shared.rate_limiter import (
    get_rate_limiter,
    check_rate_limit,
    rate_limit_async
)
from shared.error_handler import (
    RetryableError,
    NonRetryableError,
    with_retry,
    handle_api_error,
    ErrorContext
)


class TestOpenAIClient:
    """Test suite for OpenAI client utilities."""
    
    def test_singleton_client(self):
        """Test OpenAI client singleton pattern."""
        client1 = get_openai_client()
        client2 = get_openai_client()
        assert client1 is client2
    
    def test_token_usage_tracking(self):
        """Test token usage tracking."""
        # Reset counters
        reset_token_usage()
        
        # Get initial usage
        usage = get_token_usage()
        assert usage["total_tokens"] == 0
        assert usage["requests"] == 0
    
    @pytest.mark.asyncio
    async def test_chat_completion_retry(self, mock_openai_client):
        """Test chat completion with retry logic."""
        # Test successful completion
        result = await create_chat_completion_with_retry(
            messages=[{"role": "user", "content": "Test"}],
            model="gpt-4"
        )
        
        assert result is not None
        mock_openai_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_chat_completion_retry_on_error(self, mock_openai_client):
        """Test retry logic on API errors."""
        # Mock intermittent failure
        mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=[Exception("Temporary error"), MagicMock()]
        )
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            # Should retry and succeed
            result = await create_chat_completion_with_retry(
                messages=[{"role": "user", "content": "Test"}]
            )
            
            assert mock_openai_client.chat.completions.create.call_count == 2


class TestNotionClient:
    """Test suite for Notion client utilities."""
    
    def test_singleton_client(self):
        """Test Notion client singleton pattern."""
        client1 = get_notion_client()
        client2 = get_notion_client()
        assert client1 is client2
    
    @pytest.mark.asyncio
    async def test_create_task_page(self, mock_notion_client):
        """Test creating a task page."""
        # Execute
        page_id = await create_task_page(
            title="Test Task",
            status="Waiting",
            command="/test-command",
            description="Test description"
        )
        
        # Verify
        assert page_id == "test-page-id"
        mock_notion_client.pages.create.assert_called_once()
        
        # Check properties were set correctly
        call_args = mock_notion_client.pages.create.call_args
        properties = call_args[1]["properties"]
        assert properties["Name"]["title"][0]["text"]["content"] == "Test Task"
        assert properties["Status"]["select"]["name"] == "Waiting"
    
    @pytest.mark.asyncio
    async def test_update_task_status(self, mock_notion_client):
        """Test updating task status."""
        await update_task_status("test-page-id", "Complete")
        
        mock_notion_client.pages.update.assert_called_once()
        call_args = mock_notion_client.pages.update.call_args
        assert call_args[1]["properties"]["Status"]["select"]["name"] == "Complete"
    
    @pytest.mark.asyncio
    async def test_query_tasks(self, mock_notion_client):
        """Test querying tasks from database."""
        # Execute
        tasks = await query_tasks(
            filter_dict={"property": "Status", "select": {"equals": "Waiting"}}
        )
        
        # Verify
        assert len(tasks) == 1
        assert tasks[0]["id"] == "test-page-1"
        mock_notion_client.databases.query.assert_called_once()


class TestRateLimiter:
    """Test suite for rate limiter utilities."""
    
    def test_get_rate_limiter(self):
        """Test rate limiter creation."""
        limiter = get_rate_limiter()
        assert limiter is not None
        assert hasattr(limiter, "default_limits")
    
    @pytest.mark.asyncio
    async def test_check_rate_limit(self, mock_redis_client):
        """Test rate limit checking."""
        with patch("backend-system.shared.rate_limiter._redis_client", mock_redis_client):
            # First check should pass
            result = await check_rate_limit("test-key", 10, 60)
            assert result is True
            
            # Simulate exceeding limit
            mock_redis_client.pipeline().execute = AsyncMock(
                return_value=[11, 30]  # 11 requests, 30s TTL
            )
            result = await check_rate_limit("test-key", 10, 60)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator(self):
        """Test rate limiting decorator."""
        call_count = 0
        
        @rate_limit_async(calls=2, period=1)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # First two calls should work
        assert await test_function() == 1
        assert await test_function() == 2
        
        # Third call should be delayed
        start = asyncio.get_event_loop().time()
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await test_function()
            mock_sleep.assert_called_once()


class TestErrorHandler:
    """Test suite for error handling utilities."""
    
    def test_error_classification(self):
        """Test error type classification."""
        # Retryable errors
        is_retryable, delay = handle_api_error(Exception("rate limit exceeded"))
        assert is_retryable is True
        assert delay is not None
        
        # Non-retryable errors
        is_retryable, delay = handle_api_error(Exception("authentication failed"))
        assert is_retryable is False
        assert delay is None
    
    @pytest.mark.asyncio
    async def test_retry_decorator_success(self):
        """Test retry decorator with eventual success."""
        attempt_count = 0
        
        @with_retry(max_attempts=3)
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise RetryableError("Temporary failure")
            return "success"
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await flaky_function()
            assert result == "success"
            assert attempt_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_decorator_max_attempts(self):
        """Test retry decorator reaching max attempts."""
        @with_retry(max_attempts=2)
        async def always_fails():
            raise RetryableError("Always fails")
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(RetryableError):
                await always_fails()
    
    @pytest.mark.asyncio
    async def test_retry_decorator_non_retryable(self):
        """Test retry decorator with non-retryable error."""
        @with_retry()
        async def auth_error():
            raise NonRetryableError("Authentication failed")
        
        # Should not retry non-retryable errors
        with pytest.raises(NonRetryableError):
            await auth_error()
    
    @pytest.mark.asyncio
    async def test_error_context_success(self):
        """Test error context manager with successful operation."""
        async with ErrorContext("test operation") as ctx:
            result = "success"
        
        # No exception should be raised
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_error_context_with_error(self):
        """Test error context manager with error."""
        with pytest.raises(Exception):
            async with ErrorContext("test operation", reraise=True):
                raise Exception("Test error")
    
    @pytest.mark.asyncio
    async def test_error_context_suppress(self):
        """Test error context manager suppressing errors."""
        async with ErrorContext("test operation", reraise=False):
            raise Exception("This should be suppressed")
        
        # Should complete without raising
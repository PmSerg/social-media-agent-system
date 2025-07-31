"""
Pytest Configuration - Shared fixtures and test utilities
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch
import os
from datetime import datetime

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["NOTION_TOKEN"] = "test-token"
os.environ["NOTION_DATABASE_ID"] = "test-db-id"
os.environ["SERPAPI_KEY"] = "test-serp-key"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch("backend-system.shared.openai_client.get_openai_client") as mock:
        client = AsyncMock()
        
        # Mock chat completion
        completion_mock = MagicMock()
        completion_mock.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        completion_mock.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
        
        client.chat.completions.create = AsyncMock(return_value=completion_mock)
        mock.return_value = client
        
        yield client


@pytest.fixture
def mock_notion_client():
    """Mock Notion client."""
    with patch("backend-system.shared.notion_client.get_notion_client") as mock:
        client = AsyncMock()
        
        # Mock page creation
        client.pages.create = AsyncMock(return_value={
            "id": "test-page-id",
            "created_time": datetime.now().isoformat()
        })
        
        # Mock page update
        client.pages.update = AsyncMock(return_value={
            "id": "test-page-id",
            "last_edited_time": datetime.now().isoformat()
        })
        
        # Mock database query
        client.databases.query = AsyncMock(return_value={
            "results": [
                {
                    "id": "test-page-1",
                    "properties": {
                        "Status": {"select": {"name": "Waiting"}}
                    }
                }
            ]
        })
        
        mock.return_value = client
        yield client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    with patch("redis.asyncio.from_url") as mock:
        client = AsyncMock()
        client.ping = AsyncMock(return_value=True)
        client.get = AsyncMock(return_value=None)
        client.set = AsyncMock(return_value=True)
        client.incr = AsyncMock(return_value=1)
        client.expire = AsyncMock(return_value=True)
        client.pipeline = MagicMock(return_value=client)
        client.execute = AsyncMock(return_value=[1, 60])
        
        mock.return_value = client
        yield client


@pytest.fixture
def mock_webhook():
    """Mock webhook requests."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        client.post = AsyncMock(return_value=MagicMock(status_code=200))
        mock.return_value = client
        yield client


@pytest.fixture
def sample_task_data() -> Dict[str, Any]:
    """Sample Notion task data."""
    return {
        "id": "test-task-id",
        "properties": {
            "Name": {"title": [{"text": {"content": "Test Task"}}]},
            "Status": {"select": {"name": "Waiting"}},
            "Command Used": {"rich_text": [{"text": {"content": "/create-content-post"}}]},
            "Parameters": {"rich_text": [{"text": {"content": '{"topic": "AI Testing"}'}}]},
            "Webhook URL": {"url": "https://test.webhook.site/123"}
        }
    }


@pytest.fixture
def sample_research_data() -> Dict[str, Any]:
    """Sample research data."""
    return {
        "summary": "AI testing is crucial for ensuring reliable AI systems",
        "key_findings": [
            "Unit testing for AI models is essential",
            "Integration testing validates system behavior",
            "Performance testing ensures scalability"
        ],
        "sources": [
            {"title": "AI Testing Best Practices", "url": "https://example.com/1"},
            {"title": "Testing ML Systems", "url": "https://example.com/2"}
        ],
        "trends": ["Automated testing", "Continuous integration for AI"]
    }


@pytest.fixture
def sample_content_data() -> Dict[str, Any]:
    """Sample generated content data."""
    return {
        "content": "🚀 AI Testing is revolutionizing software quality! Key insights:\n\n"
                  "✅ Unit tests for models\n"
                  "✅ Integration validation\n"
                  "✅ Performance at scale\n\n"
                  "#AITesting #QualityAssurance #TechInnovation",
        "hashtags": ["AITesting", "QualityAssurance", "TechInnovation"],
        "character_count": 180,
        "platform": "Twitter",
        "alternatives": []
    }


@pytest.fixture
async def test_app():
    """Create test FastAPI app."""
    from main import app
    
    # Override dependencies if needed
    yield app


# Utility functions for tests

def assert_webhook_called(mock_webhook: AsyncMock, event_type: str):
    """Assert webhook was called with specific event type."""
    calls = mock_webhook.post.call_args_list
    for call in calls:
        if "event" in call.kwargs.get("json", {}):
            if call.kwargs["json"]["event"] == event_type:
                return True
    raise AssertionError(f"Webhook not called with event type: {event_type}")


def create_mock_response(content: str, usage_tokens: int = 100):
    """Create mock OpenAI response."""
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    response.usage = MagicMock(
        prompt_tokens=usage_tokens,
        completion_tokens=50,
        total_tokens=usage_tokens + 50
    )
    return response
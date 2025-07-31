"""
Unit Tests for TaskMonitor Agent
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime

from agents.task_monitor import TaskMonitor


class TestTaskMonitor:
    """Test suite for TaskMonitor agent."""
    
    @pytest.fixture
    def task_monitor(self, mock_openai_client, mock_notion_client):
        """Create TaskMonitor instance with mocked dependencies."""
        monitor = TaskMonitor(
            notion_client=mock_notion_client,
            research_agent=AsyncMock(),
            copywriter_agent=AsyncMock()
        )
        return monitor
    
    @pytest.mark.asyncio
    async def test_monitor_new_tasks(self, task_monitor, sample_task_data):
        """Test monitoring and processing new tasks."""
        # Setup
        task_monitor.notion_client.databases.query = AsyncMock(
            return_value={"results": [sample_task_data]}
        )
        
        # Execute
        await task_monitor.monitor_new_tasks()
        
        # Verify
        task_monitor.notion_client.databases.query.assert_called_once()
        assert task_monitor.research_agent.execute.called
        assert task_monitor.copywriter_agent.execute.called
    
    @pytest.mark.asyncio
    async def test_instant_execution_success(
        self, 
        task_monitor, 
        sample_task_data,
        sample_research_data,
        sample_content_data,
        mock_webhook
    ):
        """Test successful instant execution workflow."""
        # Setup
        task_monitor.research_agent.execute = AsyncMock(
            return_value=sample_research_data
        )
        task_monitor.copywriter_agent.execute = AsyncMock(
            return_value=sample_content_data
        )
        
        # Mock webhook
        with patch("httpx.AsyncClient", return_value=mock_webhook):
            # Execute
            await task_monitor.instant_execution(
                sample_task_data,
                "/create-content-post"
            )
        
        # Verify workflow steps
        assert task_monitor.research_agent.execute.called
        assert task_monitor.copywriter_agent.execute.called
        
        # Verify Notion updates
        update_calls = task_monitor.notion_client.pages.update.call_args_list
        assert len(update_calls) >= 2  # Status updates
        
        # Verify final status is Complete
        final_call = update_calls[-1]
        assert "Complete" in str(final_call)
    
    @pytest.mark.asyncio
    async def test_instant_execution_with_error(
        self,
        task_monitor,
        sample_task_data,
        mock_webhook
    ):
        """Test instant execution with error handling."""
        # Setup - Research fails
        task_monitor.research_agent.execute = AsyncMock(
            side_effect=Exception("Research API error")
        )
        
        # Execute
        with patch("httpx.AsyncClient", return_value=mock_webhook):
            await task_monitor.instant_execution(
                sample_task_data,
                "/create-content-post"
            )
        
        # Verify error handling
        update_calls = task_monitor.notion_client.pages.update.call_args_list
        assert any("Error" in str(call) for call in update_calls)
        
        # Verify webhook error notification
        webhook_calls = mock_webhook.post.call_args_list
        assert any("error" in str(call).lower() for call in webhook_calls)
    
    @pytest.mark.asyncio
    async def test_load_command_workflow(self, task_monitor):
        """Test loading command workflow from markdown."""
        # Mock file reading
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value="""
# Test Workflow
## Workflow Steps
### Step 1: Research
**Agent**: ResearchAgent
### Step 2: Generate
**Agent**: CopywriterAgent
            """):
                # Execute
                workflow = await task_monitor._load_command_workflow(
                    "/create-content-post"
                )
                
                # Verify
                assert workflow is not None
                assert "Step 1" in workflow
                assert "Step 2" in workflow
    
    @pytest.mark.asyncio
    async def test_parse_command_parameters(self, task_monitor):
        """Test parsing command parameters."""
        # Test valid JSON
        params = task_monitor._parse_command_parameters(
            '{"topic": "AI", "platform": "Twitter"}'
        )
        assert params["topic"] == "AI"
        assert params["platform"] == "Twitter"
        
        # Test key-value format
        params = task_monitor._parse_command_parameters(
            'topic:"Machine Learning" platform:LinkedIn'
        )
        assert params["topic"] == "Machine Learning"
        assert params["platform"] == "LinkedIn"
        
        # Test invalid format
        params = task_monitor._parse_command_parameters("invalid")
        assert params == {}
    
    @pytest.mark.asyncio
    async def test_send_webhook_notification(self, task_monitor, mock_webhook):
        """Test webhook notification sending."""
        # Setup
        webhook_url = "https://test.webhook.site/123"
        
        with patch("httpx.AsyncClient", return_value=mock_webhook):
            # Execute
            await task_monitor._send_webhook_notification(
                webhook_url,
                "test_event",
                {"key": "value"}
            )
        
        # Verify
        mock_webhook.post.assert_called_once()
        call_args = mock_webhook.post.call_args
        assert call_args[0][0] == webhook_url
        assert call_args[1]["json"]["event"] == "test_event"
        assert call_args[1]["json"]["data"]["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_scheduled_execution(self, task_monitor, sample_task_data):
        """Test scheduled task execution."""
        # Add scheduled time to task
        sample_task_data["properties"]["Scheduled Time"] = {
            "date": {"start": datetime.now().isoformat()}
        }
        
        # Setup
        task_monitor.notion_client.databases.query = AsyncMock(
            return_value={"results": [sample_task_data]}
        )
        
        # Execute
        await task_monitor.check_scheduled_tasks()
        
        # Verify task was picked up
        task_monitor.notion_client.databases.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, task_monitor):
        """Test rate limiting behavior."""
        # Test that rate limit check is performed
        with patch("backend-system.shared.rate_limiter.check_rate_limit") as mock_check:
            mock_check.return_value = False  # Rate limit exceeded
            
            # This should handle rate limit gracefully
            result = await task_monitor._check_rate_limits()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_concurrent_task_limit(self, task_monitor, sample_task_data):
        """Test concurrent task execution limits."""
        # Create multiple tasks
        tasks = [sample_task_data.copy() for _ in range(10)]
        for i, task in enumerate(tasks):
            task["id"] = f"task-{i}"
        
        task_monitor.notion_client.databases.query = AsyncMock(
            return_value={"results": tasks}
        )
        
        # Execute with concurrency limit
        await task_monitor.monitor_new_tasks()
        
        # Verify max concurrent tasks respected
        # (Implementation should limit concurrent executions)
        assert task_monitor.research_agent.execute.call_count <= 5
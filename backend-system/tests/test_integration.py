"""
Integration Tests - Full workflow testing
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import json
from datetime import datetime
from fastapi.testclient import TestClient

from main import app
from agents.task_monitor import TaskMonitor
from agents.research_agent import ResearchAgent
from agents.copywriter_agent import CopywriterAgent


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def integration_setup(
        self,
        mock_openai_client,
        mock_notion_client,
        mock_redis_client,
        mock_webhook
    ):
        """Setup for integration tests."""
        # Create real agents with mocked external services
        research_agent = ResearchAgent()
        copywriter_agent = CopywriterAgent()
        task_monitor = TaskMonitor(
            notion_client=mock_notion_client,
            research_agent=research_agent,
            copywriter_agent=copywriter_agent
        )
        
        return {
            "task_monitor": task_monitor,
            "research_agent": research_agent,
            "copywriter_agent": copywriter_agent,
            "client": TestClient(app)
        }
    
    @pytest.mark.asyncio
    async def test_full_content_creation_workflow(
        self,
        integration_setup,
        sample_task_data,
        mock_webhook
    ):
        """Test complete content creation workflow from API to completion."""
        # Setup mocks
        with patch("httpx.AsyncClient", return_value=mock_webhook):
            with patch("serpapi.search") as mock_search:
                mock_search.return_value = {
                    "organic_results": [
                        {
                            "title": "AI Best Practices",
                            "snippet": "Important AI information",
                            "link": "https://example.com"
                        }
                    ]
                }
                
                # Execute full workflow
                task_monitor = integration_setup["task_monitor"]
                await task_monitor.instant_execution(
                    sample_task_data,
                    "/create-content-post"
                )
                
                # Verify workflow completed
                notion_updates = task_monitor.notion_client.pages.update.call_args_list
                
                # Should have status updates: Processing -> Complete
                statuses = [
                    call[1]["properties"].get("Status", {}).get("select", {}).get("name")
                    for call in notion_updates
                    if "Status" in call[1]["properties"]
                ]
                
                assert "Processing" in statuses
                assert "Complete" in statuses
                
                # Verify webhook notifications
                webhook_calls = mock_webhook.post.call_args_list
                assert len(webhook_calls) >= 3  # Start, progress, complete
    
    @pytest.mark.asyncio
    async def test_api_to_notion_flow(
        self,
        integration_setup,
        valid_command_payload,
        mock_redis_client
    ):
        """Test flow from API endpoint to Notion task creation."""
        client = integration_setup["client"]
        
        with patch("redis.asyncio.from_url", return_value=mock_redis_client):
            # Make API request
            response = client.post(
                "/api/v1/execute",
                json=valid_command_payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(
        self,
        integration_setup,
        sample_task_data,
        mock_webhook
    ):
        """Test workflow recovery from errors."""
        task_monitor = integration_setup["task_monitor"]
        
        # Make research fail first time
        call_count = 0
        original_execute = task_monitor.research_agent.execute
        
        async def failing_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary API failure")
            return await original_execute(*args, **kwargs)
        
        task_monitor.research_agent.execute = failing_execute
        
        with patch("httpx.AsyncClient", return_value=mock_webhook):
            await task_monitor.instant_execution(
                sample_task_data,
                "/create-content-post"
            )
            
            # Verify retry happened
            assert call_count > 1
    
    @pytest.mark.asyncio
    async def test_concurrent_task_processing(
        self,
        integration_setup,
        sample_task_data
    ):
        """Test processing multiple tasks concurrently."""
        task_monitor = integration_setup["task_monitor"]
        
        # Create multiple tasks
        tasks = []
        for i in range(5):
            task = sample_task_data.copy()
            task["id"] = f"task-{i}"
            tasks.append(task)
        
        # Process concurrently
        await asyncio.gather(*[
            task_monitor.instant_execution(task, "/create-content-post")
            for task in tasks
        ])
        
        # Verify all tasks processed
        update_calls = task_monitor.notion_client.pages.update.call_args_list
        task_ids = set()
        for call in update_calls:
            if "page_id" in call[1]:
                task_ids.add(call[1]["page_id"])
        
        assert len(task_ids) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(
        self,
        integration_setup,
        sample_task_data
    ):
        """Test rate limit handling across the system."""
        task_monitor = integration_setup["task_monitor"]
        
        # Mock rate limit exceeded
        with patch("backend-system.shared.rate_limiter.check_rate_limit") as mock_check:
            mock_check.side_effect = [False, False, True]  # Fail twice, then succeed
            
            with patch("asyncio.sleep", new_callable=AsyncMock):
                # Should handle rate limit and retry
                await task_monitor.instant_execution(
                    sample_task_data,
                    "/create-content-post"
                )
                
                # Verify retries happened
                assert mock_check.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_webhook_reliability(
        self,
        integration_setup,
        sample_task_data
    ):
        """Test webhook delivery with retries."""
        task_monitor = integration_setup["task_monitor"]
        
        # Mock webhook failures
        webhook_mock = AsyncMock()
        webhook_mock.post = AsyncMock(
            side_effect=[
                Exception("Connection error"),
                MagicMock(status_code=200)
            ]
        )
        
        with patch("httpx.AsyncClient", return_value=webhook_mock):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await task_monitor._send_webhook_notification(
                    "https://test.webhook.site/123",
                    "test_event",
                    {"data": "test"}
                )
                
                # Should retry on failure
                assert webhook_mock.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_performance_metrics(
        self,
        integration_setup,
        sample_task_data
    ):
        """Test performance tracking across workflow."""
        task_monitor = integration_setup["task_monitor"]
        
        start_time = asyncio.get_event_loop().time()
        
        with patch("httpx.AsyncClient", return_value=AsyncMock()):
            await task_monitor.instant_execution(
                sample_task_data,
                "/create-content-post"
            )
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        # Workflow should complete within reasonable time
        assert execution_time < 60  # 60 seconds max
    
    @pytest.mark.asyncio
    async def test_data_consistency(
        self,
        integration_setup,
        sample_task_data,
        sample_research_data,
        sample_content_data
    ):
        """Test data consistency throughout the workflow."""
        task_monitor = integration_setup["task_monitor"]
        
        # Track data flow
        research_data_captured = None
        content_data_captured = None
        
        async def capture_research(*args, **kwargs):
            nonlocal research_data_captured
            research_data_captured = sample_research_data
            return sample_research_data
        
        async def capture_content(*args, **kwargs):
            nonlocal content_data_captured
            # Verify research data was passed
            assert "research_data" in kwargs
            content_data_captured = sample_content_data
            return sample_content_data
        
        task_monitor.research_agent.execute = capture_research
        task_monitor.copywriter_agent.execute = capture_content
        
        with patch("httpx.AsyncClient", return_value=AsyncMock()):
            await task_monitor.instant_execution(
                sample_task_data,
                "/create-content-post"
            )
        
        # Verify data flowed correctly
        assert research_data_captured is not None
        assert content_data_captured is not None
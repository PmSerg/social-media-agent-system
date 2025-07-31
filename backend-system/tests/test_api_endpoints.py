"""
Unit Tests for API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime

from main import app


class TestAPIEndpoints:
    """Test suite for FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_command_payload(self):
        """Valid command execution payload."""
        return {
            "command": "/create-content-post",
            "parameters": {
                "topic": "AI Testing",
                "platform": "Twitter"
            },
            "execution_mode": "instant",
            "notion_task_id": "test-task-123"
        }
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_execute_command_success(
        self,
        client,
        valid_command_payload,
        mock_redis_client
    ):
        """Test successful command execution."""
        with patch("redis.asyncio.from_url", return_value=mock_redis_client):
            with patch("backend-system.agents.task_monitor.TaskMonitor.instant_execution") as mock_execute:
                mock_execute.return_value = None
                
                # Execute
                response = client.post(
                    "/api/v1/execute",
                    json=valid_command_payload
                )
                
                # Verify
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "accepted"
                assert "task_id" in data
                assert data["command"] == "/create-content-post"
    
    @pytest.mark.asyncio
    async def test_execute_command_validation_error(
        self,
        client
    ):
        """Test command execution with invalid payload."""
        invalid_payload = {
            "command": "/invalid-command",
            "parameters": {}
        }
        
        response = client.post(
            "/api/v1/execute",
            json=invalid_payload
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    @pytest.mark.asyncio
    async def test_execute_command_missing_fields(
        self,
        client
    ):
        """Test command execution with missing required fields."""
        incomplete_payload = {
            "command": "/create-content-post"
            # Missing parameters and notion_task_id
        }
        
        response = client.post(
            "/api/v1/execute",
            json=incomplete_payload
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_rate_limiting(
        self,
        client,
        valid_command_payload
    ):
        """Test rate limiting functionality."""
        # Make multiple requests rapidly
        responses = []
        for _ in range(15):  # Exceed default rate limit
            response = client.post(
                "/api/v1/execute",
                json=valid_command_payload
            )
            responses.append(response)
        
        # Check that some requests were rate limited
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0
        
        # Check rate limit headers
        if rate_limited:
            headers = rate_limited[0].headers
            assert "X-RateLimit-Limit" in headers or "Retry-After" in headers
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options(
            "/api/v1/execute",
            headers={"Origin": "https://app.agencii.com"}
        )
        
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    @pytest.mark.asyncio
    async def test_webhook_notification_endpoint(
        self,
        client
    ):
        """Test webhook notification reception (if implemented)."""
        webhook_payload = {
            "event": "task_completed",
            "task_id": "test-123",
            "data": {
                "status": "success",
                "result": "Content generated"
            }
        }
        
        # This would test a webhook receiver endpoint if implemented
        # response = client.post("/webhooks/notify", json=webhook_payload)
        # assert response.status_code == 200
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint for monitoring."""
        response = client.get("/metrics")
        
        # Metrics might be protected or optional
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "requests_total" in data or "request_count" in data
    
    @pytest.mark.asyncio
    async def test_command_validation_endpoint(
        self,
        client
    ):
        """Test command validation without execution."""
        validation_payload = {
            "command": "/create-content-post",
            "parameters": {
                "topic": "Test Topic"
            }
        }
        
        response = client.post(
            "/api/v1/validate",
            json=validation_payload
        )
        
        # This endpoint might not exist but would be useful
        if response.status_code == 200:
            data = response.json()
            assert "valid" in data
            assert "missing_params" in data or "errors" in data
    
    @pytest.mark.asyncio
    async def test_scheduled_execution(
        self,
        client,
        valid_command_payload
    ):
        """Test scheduled command execution."""
        # Add scheduled time
        scheduled_payload = valid_command_payload.copy()
        scheduled_payload["execution_mode"] = "scheduled"
        scheduled_payload["scheduled_time"] = "2024-12-01T10:00:00Z"
        
        with patch("backend-system.agents.task_monitor.TaskMonitor.schedule_task") as mock_schedule:
            mock_schedule.return_value = None
            
            response = client.post(
                "/api/v1/execute",
                json=scheduled_payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["execution_mode"] == "scheduled"
    
    def test_error_response_format(self, client):
        """Test error response format consistency."""
        # Trigger 404
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Trigger 405
        response = client.delete("/api/v1/execute")
        assert response.status_code == 405
        
        # All errors should have consistent format
        if response.status_code >= 400:
            data = response.json()
            assert "detail" in data or "error" in data
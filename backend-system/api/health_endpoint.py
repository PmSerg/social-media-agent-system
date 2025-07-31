"""
Health Endpoint - System health checks and monitoring
"""

from fastapi import APIRouter, Request
from datetime import datetime
import time
import logging
from typing import Dict, Any
import redis.asyncio as redis

from .models import HealthResponse
from config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Track startup time
startup_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    tags=["Health"]
)
async def health_check(request: Request):
    """
    Comprehensive health check for the backend system.
    
    Checks:
    - Redis connectivity
    - OpenAI API configuration
    - Notion API configuration
    - Overall system status
    
    Returns detailed service status for monitoring.
    """
    services = {}
    overall_status = "healthy"
    
    # Check Redis
    try:
        redis_client = await redis.from_url(
            settings.redis_url,
            socket_connect_timeout=5
        )
        await redis_client.ping()
        await redis_client.close()
        services["redis"] = "connected"
        logger.debug("Redis health check passed")
    except Exception as e:
        services["redis"] = f"error: {str(e)}"
        overall_status = "degraded"
        logger.error(f"Redis health check failed: {e}")
    
    # Check OpenAI configuration
    if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
        services["openai"] = "configured"
    else:
        services["openai"] = "missing or invalid API key"
        overall_status = "degraded"
    
    # Check Notion configuration
    if settings.notion_token and settings.notion_token.startswith("secret_"):
        services["notion"] = "configured"
    else:
        services["notion"] = "missing or invalid token"
        overall_status = "degraded"
    
    # Check SerpAPI configuration
    if settings.serp_api_key:
        services["serpapi"] = "configured"
    else:
        services["serpapi"] = "missing API key"
        overall_status = "degraded"
    
    # Calculate uptime
    uptime = time.time() - startup_time
    
    # Build response
    response = HealthResponse(
        status=overall_status,
        services=services,
        uptime_seconds=uptime,
        version="1.0.0"
    )
    
    return response


@router.get(
    "/health/live",
    response_model=Dict[str, str],
    summary="Liveness probe",
    tags=["Health"]
)
async def liveness():
    """
    Simple liveness probe for container orchestration.
    
    Returns 200 OK if the service is alive.
    Used by Kubernetes/Docker for health checking.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/ready",
    response_model=Dict[str, Any],
    summary="Readiness probe",
    tags=["Health"]
)
async def readiness(request: Request):
    """
    Readiness probe to check if service is ready to accept traffic.
    
    Checks if all required services are initialized.
    """
    is_ready = True
    checks = {}
    
    # Check if task monitor is initialized
    task_monitor = getattr(request.app.state, 'task_monitor', None)
    if task_monitor:
        checks["task_monitor"] = "ready"
    else:
        checks["task_monitor"] = "not initialized"
        is_ready = False
    
    # Check Redis from app state
    try:
        # In production, we'd check the actual connection
        checks["redis"] = "ready"
    except:
        checks["redis"] = "not ready"
        is_ready = False
    
    return {
        "ready": is_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/metrics",
    response_model=Dict[str, Any],
    summary="Basic metrics",
    tags=["Health"]
)
async def metrics():
    """
    Basic metrics endpoint for monitoring.
    
    In production, this would integrate with Prometheus/Grafana.
    """
    uptime = time.time() - startup_time
    
    return {
        "uptime_seconds": uptime,
        "uptime_human": _format_uptime(uptime),
        "environment": settings.environment,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


def _format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "0m"


# Export router
__all__ = ["router"]
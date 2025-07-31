"""
Social Media Agent Backend - Main FastAPI Application
Production-ready API with rate limiting, CORS, and error handling.
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Import configuration
from config import settings

# Import API endpoints
from api.command_endpoint import router as command_router
from api.health_endpoint import router as health_router

# Import task monitor
from agents.task_monitor import TaskMonitor

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Global variables
redis_client = None
task_monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown.
    """
    # Startup
    logger.info("Starting Social Media Agent Backend...")
    
    global redis_client, task_monitor
    
    try:
        # Initialize Redis
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Redis connection established")
        
        # Initialize task monitor
        from shared.openai_client import get_openai_client
        from shared.notion_client import get_notion_client
        
        task_monitor = TaskMonitor(
            openai_client=get_openai_client(),
            notion_client=get_notion_client(),
            webhook_client=None  # Will be initialized per request
        )
        logger.info("Task monitor initialized")
        
        # Make task_monitor available globally
        app.state.task_monitor = task_monitor
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Social Media Agent Backend...")
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default]
)

# Create FastAPI app
app = FastAPI(
    title="Social Media Agent Backend",
    version="1.0.0",
    description="Backend system for AI-powered social media content creation",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "status_code": 400,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.is_production:
        error_message = "An internal error occurred"
    else:
        error_message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": error_message,
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "execute_command": "/execute-command",
            "agents": {
                "research": "/agents/research",
                "copywriter": "/agents/copywriter"
            }
        }
    }


# Include routers
app.include_router(command_router, tags=["Commands"])
app.include_router(health_router, tags=["Health"])

# Agent-specific endpoints will be added here
# app.include_router(research_router, prefix="/agents", tags=["Agents"])
# app.include_router(copywriter_router, prefix="/agents", tags=["Agents"])


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring."""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(duration)
    response.headers["X-Server-Name"] = settings.app_name
    
    return response


if __name__ == "__main__":
    """Run the application directly for development."""
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        workers=settings.api_workers if not settings.is_development else 1,
        log_level=settings.log_level.lower()
    )
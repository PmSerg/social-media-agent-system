"""
Command Endpoint - Handles command execution requests
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import logging
from typing import Dict, Any

from .models import CommandRequest, ErrorResponse
from config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Get limiter from app state
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/execute-command",
    response_model=Dict[str, Any],
    responses={
        404: {"model": ErrorResponse, "description": "Command not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
@limiter.limit(settings.rate_limit_commands)
async def execute_command(
    request: Request,
    command_request: CommandRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a command with instant or scheduled processing.
    
    This endpoint:
    1. Validates the command exists
    2. Adds the task to background processing
    3. Returns immediately with processing status
    
    The actual execution happens asynchronously with progress
    updates sent via webhooks.
    """
    logger.info(f"Received command request: {command_request.command} for task {command_request.task_id}")
    
    # Validate command exists
    command_name = command_request.command.lstrip('/')
    command_file = f"commands/{command_name}.md"
    
    if not os.path.exists(command_file):
        logger.warning(f"Command not found: {command_file}")
        raise HTTPException(
            status_code=404,
            detail=f"Command '{command_request.command}' not found"
        )
    
    # Get task monitor from app state
    task_monitor = request.app.state.task_monitor
    if not task_monitor:
        logger.error("Task monitor not initialized")
        raise HTTPException(
            status_code=500,
            detail="Task monitor not available"
        )
    
    # Prepare task data
    task_data = {
        "id": command_request.task_id,
        "params": command_request.params,
        "webhook_url": command_request.webhook_url
    }
    
    # Add to background tasks for instant execution
    if command_request.mode == "Instant":
        logger.info(f"Adding task {command_request.task_id} to background processing")
        background_tasks.add_task(
            task_monitor.instant_execution,
            task_data,
            command_request.command
        )
        
        return {
            "status": "processing",
            "task_id": command_request.task_id,
            "message": "Task execution started",
            "mode": "instant"
        }
    
    else:
        # Scheduled mode (future implementation)
        logger.info(f"Scheduled mode not yet implemented for task {command_request.task_id}")
        raise HTTPException(
            status_code=501,
            detail="Scheduled mode not yet implemented"
        )


@router.get(
    "/commands",
    response_model=Dict[str, Any],
    summary="List available commands"
)
async def list_commands():
    """
    List all available commands with their descriptions.
    
    Returns a list of commands found in the commands directory.
    """
    commands = []
    command_dir = "commands"
    
    if os.path.exists(command_dir):
        for filename in os.listdir(command_dir):
            if filename.endswith('.md'):
                command_name = f"/{filename[:-3]}"  # Remove .md extension
                commands.append({
                    "command": command_name,
                    "file": filename,
                    "available": True
                })
    
    return {
        "commands": commands,
        "total": len(commands)
    }


@router.get(
    "/execute-command/{task_id}/status",
    response_model=Dict[str, Any],
    summary="Get command execution status"
)
async def get_command_status(task_id: str, request: Request):
    """
    Get the status of a command execution.
    
    This endpoint queries Notion to get the current status
    of the task and returns relevant information.
    """
    # This would query Notion for task status
    # For MVP, we'll return a placeholder
    logger.info(f"Status check for task {task_id}")
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Status checking not yet implemented",
        "timestamp": "2024-01-20T10:00:00Z"
    }


# Export router
__all__ = ["router"]
"""
Notion Client - Async client wrapper with error handling and helpers
"""

import logging
from typing import Optional, Dict, Any, List
from notion_client import AsyncClient
import asyncio
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

# Singleton instance
_notion_client: Optional[AsyncClient] = None


def get_notion_client() -> AsyncClient:
    """
    Get or create singleton Notion client.
    
    Returns:
        AsyncClient instance for Notion API
    """
    global _notion_client
    
    if _notion_client is None:
        _notion_client = AsyncClient(
            auth=settings.notion_token,
            log_level=logging.WARNING  # Reduce noise
        )
        logger.info("Notion client initialized")
    
    return _notion_client


async def create_task_page(
    title: str,
    status: str = "Waiting",
    command: Optional[str] = None,
    execution_mode: str = "Instant",
    description: Optional[str] = None,
    additional_properties: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new task page in Notion.
    
    Args:
        title: Task title
        status: Task status (Waiting, Processing, Complete, Error)
        command: Command used
        execution_mode: Instant or Scheduled
        description: Task description
        additional_properties: Additional properties to set
        
    Returns:
        Page ID of created task
    """
    client = get_notion_client()
    
    # Build properties
    properties = {
        "Name": {
            "title": [{"text": {"content": title}}]
        },
        "Status": {
            "select": {"name": status}
        }
    }
    
    if command:
        properties["Command Used"] = {
            "rich_text": [{"text": {"content": command}}]
        }
    
    if execution_mode:
        properties["Execution Mode"] = {
            "select": {"name": execution_mode}
        }
    
    if description:
        properties["Task Description"] = {
            "rich_text": [{"text": {"content": description[:2000]}}]  # Notion limit
        }
    
    # Add any additional properties
    if additional_properties:
        properties.update(additional_properties)
    
    try:
        response = await client.pages.create(
            parent={"database_id": settings.notion_database_id},
            properties=properties
        )
        
        page_id = response["id"]
        logger.info(f"Created Notion task: {page_id}")
        return page_id
        
    except Exception as e:
        logger.error(f"Failed to create Notion task: {e}")
        raise


async def update_task_page(
    page_id: str,
    properties: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing task page.
    
    Args:
        page_id: Notion page ID
        properties: Properties to update
        
    Returns:
        Updated page data
    """
    client = get_notion_client()
    
    try:
        response = await client.pages.update(
            page_id=page_id,
            properties=properties
        )
        
        logger.debug(f"Updated Notion task: {page_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to update Notion task {page_id}: {e}")
        raise


async def query_tasks(
    filter_dict: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, str]]] = None,
    page_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Query tasks from Notion database.
    
    Args:
        filter_dict: Notion filter object
        sorts: Sort criteria
        page_size: Number of results per page
        
    Returns:
        List of task pages
    """
    client = get_notion_client()
    
    # Default sort by created time
    if sorts is None:
        sorts = [{"timestamp": "created_time", "direction": "descending"}]
    
    try:
        response = await client.databases.query(
            database_id=settings.notion_database_id,
            filter=filter_dict,
            sorts=sorts,
            page_size=page_size
        )
        
        return response.get("results", [])
        
    except Exception as e:
        logger.error(f"Failed to query Notion tasks: {e}")
        return []


async def get_task_page(page_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific task page.
    
    Args:
        page_id: Notion page ID
        
    Returns:
        Page data or None if not found
    """
    client = get_notion_client()
    
    try:
        response = await client.pages.retrieve(page_id=page_id)
        return response
        
    except Exception as e:
        logger.error(f"Failed to get Notion task {page_id}: {e}")
        return None


# Helper functions for common operations

async def update_task_status(page_id: str, status: str):
    """Update task status."""
    await update_task_page(page_id, {
        "Status": {"select": {"name": status}}
    })


async def add_task_error(page_id: str, error_message: str):
    """Add error message to task."""
    await update_task_page(page_id, {
        "Status": {"select": {"name": "Error"}},
        "Error": {"rich_text": [{"text": {"content": error_message[:2000]}}]}
    })


async def add_task_content(page_id: str, content: str):
    """Add generated content to task."""
    await update_task_page(page_id, {
        "Content": {"rich_text": [{"text": {"content": content[:2000]}}]}
    })


async def add_task_research(page_id: str, research_data: Dict[str, Any]):
    """Add research data to task."""
    # Convert to string representation
    research_str = f"Summary: {research_data.get('summary', 'N/A')}\n\n"
    
    if research_data.get('key_findings'):
        research_str += "Key Findings:\n"
        for finding in research_data['key_findings'][:5]:
            research_str += f"• {finding}\n"
    
    await update_task_page(page_id, {
        "Research Data": {"rich_text": [{"text": {"content": research_str[:2000]}}]}
    })


async def get_waiting_tasks(limit: int = 10) -> List[Dict[str, Any]]:
    """Get tasks with 'Waiting' status."""
    filter_dict = {
        "property": "Status",
        "select": {"equals": "Waiting"}
    }
    
    return await query_tasks(filter_dict, page_size=limit)


async def get_scheduled_tasks(limit: int = 10) -> List[Dict[str, Any]]:
    """Get tasks with 'Scheduled' execution mode."""
    filter_dict = {
        "and": [
            {"property": "Status", "select": {"equals": "Waiting"}},
            {"property": "Execution Mode", "select": {"equals": "Scheduled"}}
        ]
    }
    
    return await query_tasks(filter_dict, page_size=limit)


# Export functions
__all__ = [
    "get_notion_client",
    "create_task_page",
    "update_task_page",
    "query_tasks",
    "get_task_page",
    "update_task_status",
    "add_task_error",
    "add_task_content",
    "add_task_research",
    "get_waiting_tasks",
    "get_scheduled_tasks"
]
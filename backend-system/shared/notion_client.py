"""
Notion Client - Async client wrapper with error handling and helpers
"""

import logging
from typing import Optional, Dict, Any, List
from notion_client import AsyncClient
import asyncio
from datetime import datetime
import random

from config import settings
from config.notion_databases import ARCHETYPES

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
        "Task name": {
            "title": [{"text": {"content": title}}]
        },
        "Status": {
            "select": {"name": status}
        }
    }
    
    if command:
        properties["Command Used"] = {
            "select": {"name": command}  # Changed to select based on DB structure
        }
    
    if execution_mode:
        properties["Execution Mode"] = {
            "select": {"name": execution_mode}
        }
    
    # Store description in Research Data field
    if description:
        properties["Research Data"] = {
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


# Archetype helper functions

def get_archetype_by_weight() -> Dict[str, Any]:
    """
    Select archetype based on percentage weights.
    
    Returns:
        Selected archetype dictionary
    """
    # Create weighted list
    weighted_choices = []
    for key, archetype in ARCHETYPES.items():
        weighted_choices.extend([key] * archetype["percentage"])
    
    # Random selection based on weights
    selected_key = random.choice(weighted_choices)
    return ARCHETYPES[selected_key]


def get_archetype_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get archetype by name.
    
    Args:
        name: Archetype name (Caregiver, Explorer, Regular Guy)
        
    Returns:
        Archetype dictionary or None
    """
    for key, archetype in ARCHETYPES.items():
        if archetype["name"].lower() == name.lower():
            return archetype
    return None


def get_archetype_voice(archetype_name: str) -> str:
    """
    Get voice description for archetype.
    
    Args:
        archetype_name: Name of archetype
        
    Returns:
        Voice description string
    """
    archetype = get_archetype_by_name(archetype_name)
    if archetype:
        return archetype["voice"]
    return "Professional"  # Default


def get_archetype_traits(archetype_name: str) -> List[str]:
    """
    Get personality traits for archetype.
    
    Args:
        archetype_name: Name of archetype
        
    Returns:
        List of traits
    """
    archetype = get_archetype_by_name(archetype_name)
    if archetype:
        return archetype["traits"]
    return []


async def add_task_archetype(page_id: str, archetype_name: str):
    """Add archetype used to task."""
    await update_task_page(page_id, {
        "Archetype Used": {"select": {"name": archetype_name}}
    })


async def get_brand_guidelines(channel: str) -> Optional[Dict[str, Any]]:
    """
    Get brand guidelines for specific channel from Rules/Examples database.
    
    Args:
        channel: Social media channel name
        
    Returns:
        Brand guidelines or None
    """
    from config.notion_databases import DATABASES
    
    client = get_notion_client()
    
    try:
        # Query Rules/Examples database
        response = await client.databases.query(
            database_id=DATABASES["rules_examples"]["id"],
            filter={
                "property": "Channel",
                "select": {"equals": channel}
            },
            page_size=1
        )
        
        if response.get("results"):
            page = response["results"][0]
            properties = page.get("properties", {})
            
            # Extract relevant guidelines
            guidelines = {
                "tone_of_voice": properties.get("Tone of Voice", {}).get("select", {}).get("name"),
                "brand_guidelines": extract_text_from_property(properties.get("Brand Guidelines")),
                "post_format": extract_text_from_property(properties.get("Post Format")),
                "content_examples": extract_text_from_property(properties.get("Content Examples")),
                "hashtags": extract_text_from_property(properties.get("Hashtags")),
                "cta_examples": extract_text_from_property(properties.get("CTA Examples")),
                "archetype_guidelines": extract_text_from_property(properties.get("Archetype Guidelines")),
                "archetype_examples": extract_text_from_property(properties.get("Archetype Examples"))
            }
            
            return guidelines
            
    except Exception as e:
        logger.error(f"Failed to get brand guidelines: {e}")
        
    return None


def extract_text_from_property(property_value: Any) -> str:
    """Extract text from Notion property value."""
    if not property_value:
        return ""
    
    # Handle rich_text type
    if "rich_text" in property_value:
        texts = []
        for text_block in property_value["rich_text"]:
            if "text" in text_block:
                texts.append(text_block["text"]["content"])
        return " ".join(texts)
    
    return ""


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
    "get_scheduled_tasks",
    # Archetype functions
    "get_archetype_by_weight",
    "get_archetype_by_name",
    "get_archetype_voice",
    "get_archetype_traits",
    "add_task_archetype",
    "get_brand_guidelines",
    "extract_text_from_property"
]
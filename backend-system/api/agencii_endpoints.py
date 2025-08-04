"""
API endpoints specifically for Agencii platform integration
Simplified interface matching OpenAPI specification
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from shared.notion_client import (
    create_task_page, 
    update_task_page, 
    get_task_page,
    query_tasks,
    get_archetype_by_weight
)
from agents.research_agent import ResearchAgent
from agents.copywriter_agent import CopywriterAgent
from config.settings import settings
from api.dependencies import get_openai_client, verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["agencii"])


class CreateContentRequest(BaseModel):
    """Request model for content creation"""
    topic: str = Field(..., description="The topic or subject for the content")
    platform: str = Field("linkedin", description="Target social media platform")
    tone: str = Field("professional", description="Desired tone of the content")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    call_to_action: Optional[str] = Field(None, description="Call-to-action text")
    include_hashtags: bool = Field(True, description="Generate and include hashtags")


class TaskStatusRequest(BaseModel):
    """Request model for checking task status"""
    task_id: str = Field(..., description="Notion task ID to check")


class ListContentRequest(BaseModel):
    """Request model for listing content"""
    limit: int = Field(10, description="Number of items to return")
    platform: Optional[str] = Field(None, description="Filter by platform")
    archetype: Optional[str] = Field(None, description="Filter by archetype used")


@router.post("/create-content")
async def create_content(
    request: CreateContentRequest,
    api_key: str = Depends(verify_api_key),
    openai_client = Depends(get_openai_client)
) -> Dict[str, Any]:
    """
    Create social media content with automatic archetype selection
    """
    try:
        # Select archetype
        archetype = get_archetype_by_weight()
        archetype_name = archetype["name"]
        
        logger.info(f"Creating content for topic: {request.topic}, archetype: {archetype_name}")
        
        # Create Notion task
        task_id = await create_task_page(
            title=f"{request.topic} - {request.platform}",
            status="In Progress",
            command="/create-content",
            execution_mode="Instant",
            additional_properties={
                "Channel": {"select": {"name": request.platform.capitalize()}},
                "Archetype Used": {"select": {"name": archetype_name}}
            }
        )
        
        # Initialize agents
        research_agent = ResearchAgent(openai_client)
        copywriter_agent = CopywriterAgent(openai_client)
        
        # Context for agents
        context = {
            "task_id": task_id,
            "selected_archetype": archetype_name
        }
        
        # Research phase
        await update_task_page(task_id, {
            "Agent Status": {"select": {"name": "Research Agent"}}
        })
        
        research_result = await research_agent.execute(
            context,
            {
                "topic": request.topic,
                "depth": "standard",
                "focus_areas": ["benefits", "features", "trends"]
            }
        )
        
        # Content generation phase
        await update_task_page(task_id, {
            "Agent Status": {"select": {"name": "Copywriter Agent"}},
            "Research Data": {
                "rich_text": [{
                    "text": {"content": research_result.summary[:2000]}
                }]
            }
        })
        
        content_result = await copywriter_agent.execute(
            context,
            {
                "platform": request.platform,
                "topic": request.topic,
                "tone": request.tone,
                "research_data": research_result.dict(),
                "keywords": request.keywords or [],
                "call_to_action": request.call_to_action
            }
        )
        
        # Update task with final content
        await update_task_page(task_id, {
            "Status": {"select": {"name": "Published"}},
            "Agent Status": {"select": {"name": "Complete"}},
            "Final Text": {
                "rich_text": [{
                    "text": {"content": content_result.content[:2000]}
                }]
            }
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "content": content_result.content,
            "hashtags": content_result.hashtags if request.include_hashtags else [],
            "archetype_used": archetype_name,
            "character_count": content_result.character_count,
            "optimal_posting_time": content_result.optimal_posting_time
        }
        
    except Exception as e:
        logger.error(f"Content creation error: {e}", exc_info=True)
        # Try to update task with error
        if 'task_id' in locals():
            await update_task_page(task_id, {
                "Status": {"select": {"name": "Error"}},
                "Error Log": {
                    "rich_text": [{
                        "text": {"content": str(e)[:2000]}
                    }]
                }
            })
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-task-status")
async def check_task_status(
    request: TaskStatusRequest,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Check the status of a content creation task
    """
    try:
        task = await get_task_page(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        properties = task.get("properties", {})
        
        # Extract status information
        status = properties.get("Status", {}).get("select", {}).get("name", "Unknown")
        agent_status = properties.get("Agent Status", {}).get("select", {}).get("name", "Unknown")
        
        # Extract content if available
        final_text = ""
        final_text_prop = properties.get("Final Text", {}).get("rich_text", [])
        if final_text_prop:
            final_text = final_text_prop[0].get("text", {}).get("content", "")
        
        # Extract archetype used
        archetype_used = properties.get("Archetype Used", {}).get("select", {}).get("name", "")
        
        return {
            "task_id": request.task_id,
            "status": status,
            "agent_status": agent_status,
            "content": final_text,
            "archetype_used": archetype_used,
            "is_complete": status == "Published"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/list-recent-content")
async def list_recent_content(
    request: ListContentRequest,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    List recently created content with optional filters
    """
    try:
        # Build filter
        filter_conditions = []
        
        # Only show published content
        filter_conditions.append({
            "property": "Status",
            "select": {"equals": "Published"}
        })
        
        # Platform filter
        if request.platform:
            filter_conditions.append({
                "property": "Channel",
                "select": {"equals": request.platform.capitalize()}
            })
        
        # Archetype filter
        if request.archetype:
            filter_conditions.append({
                "property": "Archetype Used",
                "select": {"equals": request.archetype}
            })
        
        # Build final filter
        filter_dict = None
        if len(filter_conditions) == 1:
            filter_dict = filter_conditions[0]
        elif len(filter_conditions) > 1:
            filter_dict = {"and": filter_conditions}
        
        # Query tasks
        tasks = await query_tasks(
            filter_dict=filter_dict,
            page_size=request.limit
        )
        
        # Format results
        results = []
        for task in tasks:
            properties = task.get("properties", {})
            
            # Extract content
            final_text = ""
            final_text_prop = properties.get("Final Text", {}).get("rich_text", [])
            if final_text_prop:
                final_text = final_text_prop[0].get("text", {}).get("content", "")
            
            # Extract title
            title = ""
            title_prop = properties.get("Task name", {}).get("title", [])
            if title_prop:
                title = title_prop[0].get("text", {}).get("content", "")
            
            results.append({
                "task_id": task["id"],
                "title": title,
                "platform": properties.get("Channel", {}).get("select", {}).get("name", ""),
                "archetype_used": properties.get("Archetype Used", {}).get("select", {}).get("name", ""),
                "content": final_text,
                "created_time": task.get("created_time", "")
            })
        
        return {
            "success": True,
            "count": len(results),
            "content": results
        }
        
    except Exception as e:
        logger.error(f"List content error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
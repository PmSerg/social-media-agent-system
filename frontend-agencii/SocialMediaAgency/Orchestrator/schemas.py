"""
Pydantic schemas for Orchestrator agent tools
These schemas are used by Agencii platform to generate UI and validate inputs
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms"""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class Tone(str, Enum):
    """Content tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"
    EDUCATIONAL = "educational"


class ExecutionMode(str, Enum):
    """Task execution modes"""
    INSTANT = "instant"
    SCHEDULED = "scheduled"


class CreateContentCommand(BaseModel):
    """Schema for content creation command"""
    topic: str = Field(
        ...,
        description="The topic or subject for the content",
        example="Digital banking solutions for small businesses"
    )
    platform: Platform = Field(
        Platform.LINKEDIN,
        description="Target social media platform"
    )
    tone: Tone = Field(
        Tone.PROFESSIONAL,
        description="Desired tone of the content"
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="Keywords to include in the content",
        example=["fintech", "innovation", "banking"]
    )
    call_to_action: Optional[str] = Field(
        None,
        description="Call-to-action to include at the end",
        example="Learn more about our solutions"
    )
    include_hashtags: bool = Field(
        True,
        description="Whether to generate and include hashtags"
    )


class TaskStatus(str, Enum):
    """Task status options"""
    WAITING = "Waiting"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    PUBLISHED = "Published"
    REJECTED = "Rejected"
    ERROR = "Error"


class AgentStatus(str, Enum):
    """Agent processing status"""
    WAITING = "Waiting"
    RESEARCH_AGENT = "Research Agent"
    COPYWRITER_AGENT = "Copywriter Agent"
    IMAGE_PROMPT_AGENT = "Image Prompt Agent"
    IMAGE_GENERATION_AGENT = "Image Generation Agent"
    COMPLETE = "Complete"


class NotionTaskUpdate(BaseModel):
    """Schema for updating Notion task"""
    task_id: str = Field(
        ...,
        description="Notion page ID to update"
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="New task status"
    )
    agent_status: Optional[AgentStatus] = Field(
        None,
        description="Current agent processing status"
    )
    research_data: Optional[str] = Field(
        None,
        description="Research findings to add"
    )
    final_text: Optional[str] = Field(
        None,
        description="Generated content to add"
    )
    error_log: Optional[str] = Field(
        None,
        description="Error message if any"
    )


class ResearchRequest(BaseModel):
    """Schema for research agent request"""
    topic: str = Field(
        ...,
        description="Topic to research"
    )
    depth: Literal["quick", "standard", "deep"] = Field(
        "standard",
        description="Research depth level"
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Specific areas to focus on",
        example=["benefits", "features", "trends"]
    )


class ContentRequest(BaseModel):
    """Schema for copywriter agent request"""
    topic: str = Field(
        ...,
        description="Content topic"
    )
    platform: Platform = Field(
        ...,
        description="Target platform"
    )
    tone: Tone = Field(
        ...,
        description="Content tone"
    )
    research_data: dict = Field(
        ...,
        description="Research data from Research Agent"
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="Keywords to include"
    )
    call_to_action: Optional[str] = Field(
        None,
        description="Call-to-action text"
    )


class TaskResult(BaseModel):
    """Schema for task execution result"""
    success: bool = Field(
        ...,
        description="Whether the task succeeded"
    )
    task_id: str = Field(
        ...,
        description="Notion task ID"
    )
    content: Optional[str] = Field(
        None,
        description="Generated content if successful"
    )
    hashtags: Optional[List[str]] = Field(
        None,
        description="Generated hashtags"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if failed"
    )
    archetype_used: Optional[str] = Field(
        None,
        description="Which brand archetype was used (Caregiver, Explorer, Regular Guy)"
    )
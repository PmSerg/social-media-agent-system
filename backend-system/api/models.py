"""
API Models - Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class ExecutionMode(str, Enum):
    """Task execution modes."""
    INSTANT = "Instant"
    SCHEDULED = "Scheduled"


class AgentStatus(str, Enum):
    """Agent/Task status values."""
    WAITING = "Waiting"
    PROCESSING = "Processing"
    COMPLETE = "Complete"
    ERROR = "Error"


class Platform(str, Enum):
    """Supported social media platforms."""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    # Future platforms
    # FACEBOOK = "facebook"
    # INSTAGRAM = "instagram"


class Tone(str, Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"


class CommandRequest(BaseModel):
    """Request model for command execution."""
    task_id: str = Field(..., description="Notion task ID")
    command: str = Field(..., description="Command to execute (e.g., /create-content-post)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    mode: ExecutionMode = Field(ExecutionMode.INSTANT, description="Execution mode")
    webhook_url: Optional[str] = Field(None, description="URL for progress callbacks")
    
    @validator('command')
    def validate_command(cls, v):
        """Ensure command starts with /."""
        if not v.startswith('/'):
            raise ValueError('Command must start with /')
        return v
    
    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        """Ensure webhook URL is HTTPS in production."""
        if v and not v.startswith(('https://', 'http://')):
            raise ValueError('Webhook URL must be a valid HTTP(S) URL')
        return v


class ProgressUpdate(BaseModel):
    """Progress update model for webhooks."""
    task_id: str
    status: AgentStatus
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


class CreateContentParams(BaseModel):
    """Parameters for content creation."""
    topic: str = Field(..., min_length=1, max_length=500, description="Content topic")
    platform: Platform = Field(..., description="Target platform")
    tone: Optional[Tone] = Field(None, description="Content tone")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    hashtag_count: Optional[int] = Field(5, ge=1, le=10, description="Number of hashtags")
    include_cta: bool = Field(True, description="Include call-to-action")
    
    @validator('topic')
    def clean_topic(cls, v):
        """Clean and validate topic."""
        return v.strip()


class ResearchResult(BaseModel):
    """Result model for research operations."""
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Information sources")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    summary: str = Field("", description="Research summary")
    statistics: Optional[List[str]] = Field(None, description="Relevant statistics")
    trends: Optional[List[str]] = Field(None, description="Identified trends")
    
    @validator('sources')
    def validate_sources(cls, v):
        """Ensure sources have required fields."""
        for source in v:
            if 'title' not in source or 'url' not in source:
                raise ValueError('Each source must have title and url')
        return v


class ContentResult(BaseModel):
    """Result model for content generation."""
    content: str = Field(..., max_length=10000, description="Generated content")
    hashtags: List[str] = Field(default_factory=list, description="Recommended hashtags")
    character_count: int = Field(0, description="Character count")
    platform_optimized: bool = Field(True, description="Platform optimization status")
    tone: str = Field("professional", description="Applied tone")
    engagement_tips: Optional[List[str]] = Field(None, description="Engagement tips")
    optimal_posting_time: Optional[str] = Field(None, description="Suggested posting time")
    cta_effectiveness: Optional[int] = Field(None, ge=1, le=10, description="CTA effectiveness score")
    
    @validator('character_count', always=True)
    def calculate_character_count(cls, v, values):
        """Calculate character count from content."""
        if 'content' in values:
            return len(values['content'])
        return v


class HealthResponse(BaseModel):
    """Health check response model."""
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field("1.0.0")
    services: Dict[str, str] = Field(default_factory=dict)
    uptime_seconds: Optional[float] = None
    
    
class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: str = Field(..., description="Request path")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class AgentRequest(BaseModel):
    """Base request model for agent operations."""
    task_id: str = Field(..., description="Task ID for tracking")
    params: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific parameters")
    timeout: Optional[int] = Field(None, description="Custom timeout in seconds")


class ResearchRequest(AgentRequest):
    """Request model for research agent."""
    topic: str = Field(..., description="Research topic")
    depth: Literal["quick", "standard", "deep"] = Field("standard", description="Research depth")
    focus_areas: Optional[List[str]] = Field(None, description="Specific focus areas")
    max_sources: Optional[int] = Field(10, ge=1, le=50, description="Maximum sources to fetch")


class CopywriterRequest(AgentRequest):
    """Request model for copywriter agent."""
    platform: Platform = Field(..., description="Target platform")
    topic: str = Field(..., description="Content topic")
    tone: Tone = Field(Tone.PROFESSIONAL, description="Content tone")
    research_data: Optional[Dict[str, Any]] = Field(None, description="Research data to base content on")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    call_to_action: Optional[str] = Field(None, description="Specific CTA to include")


# Export all models
__all__ = [
    "ExecutionMode",
    "AgentStatus",
    "Platform",
    "Tone",
    "CommandRequest",
    "ProgressUpdate",
    "CreateContentParams",
    "ResearchResult",
    "ContentResult",
    "HealthResponse",
    "ErrorResponse",
    "AgentRequest",
    "ResearchRequest",
    "CopywriterRequest"
]
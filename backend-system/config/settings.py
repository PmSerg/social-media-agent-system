"""
Application Settings using Pydantic Settings
Loads and validates environment variables with type safety.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses .env file if present, with validation and type conversion.
    """
    
    # Application Settings
    app_name: str = Field(default="Social Media Agent Backend", description="Application name")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Keys
    openai_api_key: str = Field(..., description="OpenAI API key for GPT-4")
    notion_token: str = Field(..., description="Notion integration token")
    serp_api_key: str = Field(..., description="SerpAPI key for web search")
    
    # Database IDs
    notion_database_id: str = Field(..., description="Notion database ID for tasks")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_ttl: int = Field(default=3600, description="Redis cache TTL in seconds")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=1, description="Number of API workers")
    port: Optional[int] = Field(default=None, description="Railway PORT override")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["https://agencii.ai", "https://*.agencii.ai", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Webhook Configuration
    webhook_base_url: str = Field(default="https://agencii.ai/webhooks", description="Webhook base URL")
    webhook_timeout: int = Field(default=10, description="Webhook timeout in seconds")
    webhook_retry_attempts: int = Field(default=3, description="Webhook retry attempts")
    
    # API Security
    backend_webhook_secret: str = Field(..., description="Secret key for API authentication", alias="API_SECRET_KEY")
    
    # Rate Limiting
    rate_limit_default: str = Field(default="100 per minute", description="Default rate limit")
    rate_limit_commands: str = Field(default="10 per minute", description="Command endpoint rate limit")
    
    # Agent Configuration
    agent_timeout: int = Field(default=120, description="Agent execution timeout in seconds")
    workflow_timeout: int = Field(default=300, description="Total workflow timeout in seconds")
    
    # Search Configuration
    serp_max_results: int = Field(default=10, description="Maximum search results to fetch")
    serp_retry_on_429: bool = Field(default=True, description="Retry on rate limit")
    
    # Content Generation
    max_content_length: int = Field(default=10000, description="Maximum content length")
    default_language: str = Field(default="en", description="Default content language")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is valid."""
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if not v.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v
    
    @validator("notion_token")
    def validate_notion_token(cls, v):
        """Validate Notion token format."""
        # New Notion tokens start with 'ntn_' instead of 'secret_'
        if not (v.startswith("secret_") or v.startswith("ntn_")):
            raise ValueError("Notion token must start with 'secret_' or 'ntn_'")
        return v
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    def get_platform_limits(self) -> dict:
        """Get character limits for each platform."""
        return {
            "twitter": 280,
            "linkedin": 3000,
            "facebook": 63206,
            "instagram": 2200,
            "threads": 500,
            "telegram": 4096
        }
    
    def get_tone_prompts(self) -> dict:
        """Get prompt variations for different tones."""
        return {
            "professional": "Use formal language, industry terms, and data-driven insights.",
            "casual": "Use conversational language, relatable examples, and friendly tone.",
            "playful": "Use humor, wordplay, and engaging language while staying respectful."
        }


# Create singleton instance
settings = Settings()

# Export for convenience
__all__ = ["settings", "Settings"]
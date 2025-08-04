"""
API Dependencies for dependency injection
"""

from fastapi import HTTPException, Header
from typing import Optional
import openai
from config.settings import settings
from shared.openai_client import get_openai_client as shared_get_openai_client


async def verify_api_key(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify API key from Authorization header
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    # Verify token
    if token != settings.backend_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token


def get_openai_client() -> openai.AsyncOpenAI:
    """
    Get OpenAI client instance
    """
    return shared_get_openai_client()
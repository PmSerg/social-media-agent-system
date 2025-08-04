"""
Notion configuration with all databases
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Notion API credentials
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"

# Main page
NOTION_PAGE_ID = "24476a959af780638935e84349d9948c"

# Database configurations
DATABASES = {
    "categories": {
        "id": os.getenv("NOTION_DB_CATEGORIES", "24476a959af7814fb3cbeea2c593ab30"),
        "name": "Categories and Topics",
        "description": "Content categories and topics for AI agents"
    },
    "content_plan": {
        "id": os.getenv("NOTION_DB_CONTENT_PLAN", "24476a959af7810d9ff5c3f835e82ed7"),
        "name": "Content Plan - AI Workflow", 
        "description": "Main content planning and workflow tracking"
    },
    "rules_examples": {
        "id": os.getenv("NOTION_DB_RULES_EXAMPLES", "24476a959af781aabc96c0b3627fbd55"),
        "name": "Rules / Examples",
        "description": "Content creation rules and examples"
    },
    "image_styles": {
        "id": os.getenv("NOTION_DB_IMAGE_STYLES", "24476a959af781809184e7676e54acf9"),
        "name": "Image Styles",
        "description": "Visual style guidelines and templates"
    }
}

def get_headers() -> Dict[str, str]:
    """
    Get headers for Notion API requests.
    
    Returns:
        dict: Headers with authorization and content type
    """
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

def get_database_id(db_name: str) -> str:
    """
    Get database ID by name.
    
    Args:
        db_name: Database key name (categories, content_plan, etc.)
        
    Returns:
        str: Database ID
        
    Raises:
        KeyError: If database name not found
    """
    if db_name not in DATABASES:
        raise KeyError(f"Database '{db_name}' not found. Available: {list(DATABASES.keys())}")
    return DATABASES[db_name]["id"]

def get_all_database_ids() -> Dict[str, str]:
    """
    Get all database IDs.
    
    Returns:
        dict: Mapping of database names to IDs
    """
    return {name: config["id"] for name, config in DATABASES.items()}
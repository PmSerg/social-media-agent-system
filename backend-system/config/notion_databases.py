"""
Notion database schemas and configurations
Based on actual Notion database structure
"""
import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# Database IDs - Updated with correct IDs
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
    },
    "brand_assets": {
        "id": os.getenv("NOTION_DB_BRAND_ASSETS", "24476a959af78073-99d3-e5908225fbc6"),
        "name": "Brand Assets",
        "description": "Brand descriptions, press releases, examples, CEO bio"
    },
    "industries": {
        "id": os.getenv("NOTION_DB_INDUSTRIES", "24476a959af7809c-a379-ff5c35b065cd"),
        "name": "Industries & Challenges",
        "description": "Industry categories and banking challenges"
    }
}

# Database Schemas with actual properties and options
SCHEMAS = {
    "categories": {
        "properties": {
            "Topic Name": {"type": "title", "required": True},
            "Category": {
                "type": "select",
                "options": ["Market news", "Case studies", "Events", "Office life/Team", "Products"]
            },
            "Subcategory": {
                "type": "select", 
                "options": ["Payment Rails", "Crypto Services", "Banking Features", "Industry Trends", "Regulatory Updates", "Market Analysis", "Client Success", "Implementation Stories"]
            },
            "Benefits & Key Points": {"type": "rich_text"},
            "Description": {"type": "relation", "database_id": DATABASES["content_plan"]["id"]},
            "Primary Archetype": {
                "type": "select",
                "options": ["Caregiver", "Explorer", "Regular Guy"]
            },
            "Archetype Balance": {"type": "text"},
            "Target Audience": {
                "type": "multi_select",
                "options": ["Underbanked businesses", "E-commerce", "Crypto traders", "SMEs", "Startups", "High-risk businesses"]
            },
            "Priority": {
                "type": "select",
                "options": ["High", "Medium", "Low"]
            },
            "Key Messages": {"type": "rich_text"},
            "Product Type": {
                "type": "select",
                "options": ["Payment Rails", "Banking Services", "Crypto Services", "Compliance Tools"]
            },
            "Content Frequency": {
                "type": "select",
                "options": ["Weekly", "Bi-weekly", "Monthly", "Quarterly"]
            },
            "Industry": {"type": "relation", "database_id": DATABASES["industries"]["id"]},
            "Related Brand Assets": {"type": "relation", "database_id": DATABASES["brand_assets"]["id"]}
        }
    },
    "content_plan": {
        "properties": {
            "Task name": {"type": "title", "required": True},
            "Status": {
                "type": "select",
                "options": ["Idea", "In Progress", "In Review", "Published", "Rejected"]
            },
            "Agent Status": {
                "type": "select",
                "options": ["Waiting", "Research Agent", "Copywriter Agent", "Image Prompt Agent", 
                           "Image Generation Agent", "Complete"]
            },
            "Execution Mode": {
                "type": "select",
                "options": ["Instant", "Scheduled"]
            },
            "Channel": {
                "type": "select",
                "options": ["Facebook", "Instagram", "Twitter", "LinkedIn"]
            },
            "Category": {"type": "relation", "database_id": DATABASES["categories"]["id"]},
            "Command Used": {"type": "rich_text"},
            "Research Data": {"type": "rich_text"},
            "Final Text": {"type": "rich_text"},
            "Image Prompts": {"type": "rich_text"},
            "Image URLs": {"type": "url"},
            "Error Log": {"type": "rich_text"},
            "Publication Date": {"type": "date"},
            "Month": {
                "type": "select",
                "options": ["December", "November", "October", "September", "August"]
            },
            "Week": {
                "type": "select",
                "options": ["Week 1", "Week 2", "Week 3", "Week 4"]
            },
            "Position in Week": {
                "type": "select",
                "options": ["Post 1", "Post 2", "Post 3"]
            },
            "Archetype Used": {
                "type": "select",
                "options": ["Caregiver", "Explorer", "Regular Guy", "Mixed"]
            },
            "Target Audience": {
                "type": "multi_select",
                "options": ["Underbanked businesses", "E-commerce", "Crypto traders", "SMEs", "Startups", "High-risk businesses"]
            },
            "Content Type": {
                "type": "select",
                "options": ["Educational", "Promotional", "News", "Engagement", "Support"]
            },
            "Performance Metrics": {"type": "text"},
            "A/B Test Version": {"type": "text"},
            "CEO Quote Included": {"type": "checkbox"},
            "Press Release Based": {"type": "checkbox"},
            "Related Content": {"type": "relation", "database_id": DATABASES["content_plan"]["id"]},
            "Industry Focus": {"type": "relation", "database_id": DATABASES["industries"]["id"]},
            "Brand Assets Used": {"type": "relation", "database_id": DATABASES["brand_assets"]["id"]}
        }
    },
    "rules_examples": {
        "properties": {
            "Name": {"type": "title", "required": True},
            "Channel": {
                "type": "select",
                "options": ["Threads", "Telegram", "Instagram", "Facebook", "LinkedIn"]
            },
            "Brand Voice": {
                "type": "select",
                "options": ["Caregiver", "Explorer", "Regular Guy", "Mixed Balanced"]
            },
            "Tone of Voice": {
                "type": "select",
                "options": ["Authentic", "Aspirational", "Informative", "Conversational", "Professional"]
            },
            "Brand Guidelines": {"type": "rich_text"},
            "Post Format": {"type": "rich_text"},
            "Content Examples": {"type": "rich_text"},
            "Hashtags": {"type": "rich_text"},
            "CTA Examples": {"type": "rich_text"},
            "Archetype Guidelines": {"type": "rich_text"},
            "Archetype Examples": {"type": "rich_text"},
            "Do's and Don'ts": {"type": "rich_text"},
            "Target Audience per Channel": {"type": "text"},
            "Optimal Posting Times": {"type": "text"},
            "Visual Guidelines": {"type": "rich_text"},
            "CEO Quotes": {"type": "text"},
            "Industry-Specific Rules": {"type": "relation", "database_id": DATABASES["industries"]["id"]},
            "Example Posts": {"type": "relation", "database_id": DATABASES["brand_assets"]["id"]}
        }
    },
    "image_styles": {
        "properties": {
            "Style Name": {"type": "title", "required": True},
            "Base Prompt": {"type": "rich_text"},
            "Image Size": {
                "type": "select",
                "options": ["1792x1024", "1024x1792", "1024x1024"]
            },
            "Mood": {
                "type": "multi_select",
                "options": ["Minimal", "Corporate", "Bold", "Friendly", "Professional", "Trustworthy", "Innovative", "Approachable"]
            },
            "Categories and Topics": {"type": "relation", "database_id": DATABASES["categories"]["id"]},
            "Archetype Alignment": {
                "type": "select",
                "options": ["Caregiver", "Explorer", "Regular Guy", "Universal"]
            },
            "Color Palette": {"type": "text"},
            "Visual Elements": {"type": "text"},
            "Avoid Elements": {"type": "text"},
            "Example Images": {"type": "files"}
        }
    },
    "brand_assets": {
        "properties": {
            "Title": {"type": "title", "required": True},
            "Asset Type": {
                "type": "select",
                "options": ["Brand Description", "Press Release", "Example Posts", "CEO Bio", "Product Info", "Audience Persona"]
            },
            "Content": {"type": "rich_text"},
            "Category": {
                "type": "select",
                "options": ["About Company", "Leadership", "Products", "Target Audience", "PR Materials"]
            },
            "Date Added": {"type": "date"},
            "Status": {
                "type": "select",
                "options": ["Active", "Archived", "Draft"]
            },
            "Tags": {"type": "multi_select"},
            "Archetype Alignment": {
                "type": "multi_select",
                "options": ["Caregiver", "Explorer", "Regular Guy"]
            },
            "Related Categories": {"type": "relation", "database_id": DATABASES["categories"]["id"]}
        }
    },
    "industries": {
        "properties": {
            "Industry Name": {"type": "title", "required": True},
            "Category": {
                "type": "select",
                "options": [
                    "Adult Industry", "Alternative Lending & Finance", "Art & Collectibles",
                    "Cryptocurrency & Blockchain", "Crowdfunding & Peer-to-Peer Platforms",
                    "Cybersecurity & VPN Services", "E-commerce & Dropshipping",
                    "Escort & Dating Services", "Fintech & Digital Banks",
                    "Gaming & eSports", "Gambling & Betting", "High-Risk Travel & Hospitality",
                    "Money Services & Payment Processors", "Online Education & Coaching",
                    "Remittance & Money Transfer", "Subscription-Based Services",
                    "Web Hosting & Cloud Services", "DeFi & Web3 Financial Services",
                    "Nutraceuticals & Alternative Payment Systems", "Precious Metals & Mining",
                    "CBD & Cannabis", "NGOs & Activist Groups", "Freelance & Gig Economy"
                ]
            },
            "Banking Challenges": {"type": "text"},
            "Risk Level": {
                "type": "select",
                "options": ["High", "Medium", "Low"]
            },
            "Example Clients": {"type": "text"},
            "Content Priority": {"type": "number"},
            "Key Messages": {"type": "text"},
            "Our Solutions": {"type": "relation", "database_id": DATABASES["categories"]["id"]}
        }
    }
}

# Field mappings for backward compatibility
FIELD_MAPPINGS = {
    "content_plan": {
        "name": "Task name",
        "title": "Task name",
        "task_name": "Task name",
        "status": "Status",
        "agent_status": "Agent Status",
        "execution_mode": "Execution Mode",
        "channel": "Channel",
        "command": "Command Used",
        "research": "Research Data",
        "content": "Final Text",
        "final_text": "Final Text",
        "image_prompts": "Image Prompts",
        "image_urls": "Image URLs",
        "error": "Error Log",
        "error_log": "Error Log",
        "date": "Publication Date",
        "category": "Category",
        "archetype_used": "Archetype Used",
        "target_audience": "Target Audience",
        "content_type": "Content Type",
        "performance_metrics": "Performance Metrics",
        "ceo_quote": "CEO Quote Included",
        "press_release": "Press Release Based"
    }
}

# Status values
STATUS_VALUES = {
    "task": ["Idea", "In Progress", "In Review", "Published", "Rejected"],
    "agent": ["Waiting", "Research Agent", "Copywriter Agent", "Image Prompt Agent", 
              "Image Generation Agent", "Complete"],
    "old_status": ["Waiting", "Processing", "Complete", "Error"]  # For backward compatibility
}

# Channel configurations
CHANNELS = {
    "twitter": {"char_limit": 280, "name": "Twitter"},
    "linkedin": {"char_limit": 3000, "name": "LinkedIn"},
    "facebook": {"char_limit": 63206, "name": "Facebook"},
    "instagram": {"char_limit": 2200, "name": "Instagram"},
    "threads": {"char_limit": 500, "name": "Threads"},
    "telegram": {"char_limit": 4096, "name": "Telegram"}
}

# Brand archetypes
ARCHETYPES = {
    "caregiver": {
        "name": "Caregiver",
        "percentage": 35,
        "voice": "Caregiver Professional",
        "traits": ["empathetic", "supportive", "nurturing", "understanding"],
        "description": "Nurturing businesses with empathy and support"
    },
    "explorer": {
        "name": "Explorer", 
        "percentage": 35,
        "voice": "Explorer Innovative",
        "traits": ["innovative", "pioneering", "bold", "adventurous"],
        "description": "Boldly exploring new opportunities through tech"
    },
    "regular_guy": {
        "name": "Regular Guy",
        "percentage": 30,
        "voice": "Regular Guy Friendly",
        "traits": ["simple", "friendly", "relatable", "approachable"],
        "description": "Keeping it simple, friendly, and relatable"
    }
}

# Content types
CONTENT_TYPES = ["Educational", "Promotional", "News", "Engagement", "Support"]

# Target audiences
TARGET_AUDIENCES = [
    "Underbanked businesses",
    "E-commerce",
    "Crypto traders",
    "SMEs",
    "Startups", 
    "High-risk businesses"
]

# Helper functions
def get_database_id(db_name: str) -> str:
    """Get database ID by name"""
    if db_name not in DATABASES:
        raise ValueError(f"Unknown database: {db_name}")
    return DATABASES[db_name]["id"]

def get_field_name(db_name: str, field_alias: str) -> str:
    """Get actual field name from alias"""
    if db_name in FIELD_MAPPINGS and field_alias in FIELD_MAPPINGS[db_name]:
        return FIELD_MAPPINGS[db_name][field_alias]
    return field_alias

def get_status_options(status_type: str = "task") -> List[str]:
    """Get status options by type"""
    return STATUS_VALUES.get(status_type, [])
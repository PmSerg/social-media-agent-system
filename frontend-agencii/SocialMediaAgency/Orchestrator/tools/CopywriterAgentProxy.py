"""
Copywriter Agent Proxy Tool - Communicates with backend Copywriter Agent
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import json

load_dotenv()


class CopywriterAgentProxy(BaseTool):
    """
    Proxy tool for communicating with the backend Copywriter Agent.
    Handles content creation requests with platform-specific optimization.
    Ensures content meets character limits and style guidelines.
    """
    
    task_id: str = Field(
        ...,
        description="Notion task ID for tracking the content creation request"
    )
    
    platform: str = Field(
        ...,
        description="Target platform: 'linkedin' or 'twitter'"
    )
    
    topic: str = Field(
        ...,
        description="Content topic or main message to convey"
    )
    
    tone: str = Field(
        "professional",
        description="Content tone: 'professional', 'casual', or 'playful'"
    )
    
    research_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Research data from Research Agent to base content on"
    )
    
    keywords: Optional[str] = Field(
        None,
        description="Comma-separated keywords to include in the content"
    )
    
    call_to_action: Optional[str] = Field(
        None,
        description="Specific call-to-action to include (e.g., 'Learn more', 'Share your thoughts')"
    )
    
    def run(self) -> str:
        """Execute content creation request via backend API."""
        backend_url = os.getenv("BACKEND_URL")
        
        if not backend_url:
            return "❌ Error: Backend URL not configured"
        
        try:
            # Load cached research data if not provided
            if not self.research_data:
                self.research_data = self._load_research_cache(self.task_id)
            
            # Prepare content request
            content_params = {
                "task_id": self.task_id,
                "platform": self.platform.lower(),
                "topic": self.topic,
                "tone": self.tone,
                "research_data": self.research_data or {}
            }
            
            if self.keywords:
                content_params["keywords"] = [
                    kw.strip() for kw in self.keywords.split(",")
                ]
            
            if self.call_to_action:
                content_params["call_to_action"] = self.call_to_action
            
            # Call Copywriter Agent endpoint
            response = requests.post(
                f"{backend_url}/agents/copywriter",
                json=content_params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._format_content_results(result)
            
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Invalid request")
                return f"❌ Invalid request: {error_detail}"
            
            elif response.status_code == 429:
                return "❌ Rate limit reached. Please try again in a few moments."
            
            else:
                error_detail = response.json().get("detail", "Unknown error")
                return f"❌ Copywriter Agent error: {error_detail}"
                
        except requests.exceptions.Timeout:
            return "❌ Content generation timed out. Please try with a simpler request."
        
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Copywriter Agent. Please check backend status."
        
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def _load_research_cache(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load cached research data if available."""
        cache_file = f"/tmp/research_cache/{task_id}.json"
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return None
    
    def _format_content_results(self, result: Dict[str, Any]) -> str:
        """Format content results for presentation."""
        output = "✍️ **Content Created Successfully!**\n\n"
        
        # Platform info
        platform = result.get("platform", "").title()
        char_count = result.get("character_count", 0)
        char_limit = self._get_platform_limit(result.get("platform"))
        
        output += f"**Platform:** {platform}\n"
        output += f"**Character Count:** {char_count}/{char_limit}\n"
        output += f"**Tone:** {result.get('tone', 'professional').title()}\n\n"
        
        # Main content
        output += "**Content:**\n"
        output += "```\n"
        output += result.get("content", "")
        output += "\n```\n\n"
        
        # Hashtags
        if result.get("hashtags"):
            output += "**Hashtags:**\n"
            hashtags = " ".join([f"#{tag}" for tag in result["hashtags"]])
            output += f"{hashtags}\n\n"
        
        # Engagement tips
        if result.get("engagement_tips"):
            output += "**Engagement Tips:**\n"
            for tip in result["engagement_tips"]:
                output += f"• {tip}\n"
            output += "\n"
        
        # Optimal posting time
        if result.get("optimal_posting_time"):
            output += f"**Suggested Posting Time:** {result['optimal_posting_time']}\n\n"
        
        # Call to action effectiveness
        if result.get("cta_effectiveness"):
            output += f"**Call-to-Action Strength:** {result['cta_effectiveness']}/10\n"
        
        # Save full results
        self._save_content_results(self.task_id, result)
        
        return output
    
    def _get_platform_limit(self, platform: str) -> int:
        """Get character limit for platform."""
        limits = {
            "twitter": 280,
            "linkedin": 3000,
            "facebook": 63206,
            "instagram": 2200
        }
        return limits.get(platform, 0)
    
    def _save_content_results(self, task_id: str, results: Dict[str, Any]):
        """Save content results for later use."""
        # Update Notion with the content
        notion_token = os.getenv("NOTION_TOKEN")
        if notion_token:
            from notion_client import Client
            notion = Client(auth=notion_token)
            
            try:
                notion.pages.update(
                    page_id=task_id,
                    properties={
                        "Content": {
                            "rich_text": [
                                {"text": {"content": results.get("content", "")}}
                            ]
                        },
                        "Status": {
                            "select": {"name": "Complete"}
                        }
                    }
                )
            except:
                # Silently fail - don't disrupt the user experience
                pass


# Test the tool if run directly
if __name__ == "__main__":
    tool = CopywriterAgentProxy(
        task_id="test-content-123",
        platform="linkedin",
        topic="The future of AI in social media marketing",
        tone="professional",
        keywords="AI, automation, engagement, analytics",
        call_to_action="Share your thoughts on AI in marketing"
    )
    result = tool.run()
    print(result)
"""
Research Agent Proxy Tool - Communicates with backend Research Agent
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import json
import time

load_dotenv()


class ResearchAgentProxy(BaseTool):
    """
    Proxy tool for communicating with the backend Research Agent.
    Handles research requests, monitors progress, and retrieves results.
    Supports both synchronous and asynchronous communication patterns.
    """
    
    task_id: str = Field(
        ...,
        description="Notion task ID for tracking the research request"
    )
    
    topic: str = Field(
        ...,
        description="Research topic to investigate (e.g., 'AI trends in healthcare')"
    )
    
    depth: str = Field(
        "standard",
        description="Research depth: 'quick' (2-3 sources), 'standard' (5-7 sources), 'deep' (10+ sources)"
    )
    
    focus_areas: Optional[str] = Field(
        None,
        description="Specific areas to focus on, comma-separated (e.g., 'statistics, case studies, expert opinions')"
    )
    
    def run(self) -> str:
        """Execute research request via backend API."""
        backend_url = os.getenv("BACKEND_URL")
        
        if not backend_url:
            return "❌ Error: Backend URL not configured"
        
        try:
            # Prepare research request
            research_params = {
                "task_id": self.task_id,
                "topic": self.topic,
                "depth": self.depth
            }
            
            if self.focus_areas:
                research_params["focus_areas"] = [
                    area.strip() for area in self.focus_areas.split(",")
                ]
            
            # Call Research Agent endpoint
            response = requests.post(
                f"{backend_url}/agents/research",
                json=research_params,
                timeout=60  # Longer timeout for research
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._format_research_results(result)
            
            elif response.status_code == 202:
                # Async processing - poll for results
                job_id = response.json().get("job_id")
                return self._poll_for_results(backend_url, job_id)
            
            elif response.status_code == 429:
                return "❌ Rate limit reached. Please try again in a few moments."
            
            else:
                error_detail = response.json().get("detail", "Unknown error")
                return f"❌ Research Agent error: {error_detail}"
                
        except requests.exceptions.Timeout:
            return "❌ Research request timed out. The topic might be too broad. Try a more specific query."
        
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Research Agent. Please check backend status."
        
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def _poll_for_results(self, backend_url: str, job_id: str, max_attempts: int = 30) -> str:
        """Poll for async research results."""
        for attempt in range(max_attempts):
            try:
                # Check job status
                status_response = requests.get(
                    f"{backend_url}/agents/research/status/{job_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if status_data["status"] == "completed":
                        return self._format_research_results(status_data["result"])
                    
                    elif status_data["status"] == "failed":
                        return f"❌ Research failed: {status_data.get('error', 'Unknown error')}"
                    
                    # Still processing - show progress
                    if attempt % 5 == 0:  # Update every 5 attempts
                        progress = status_data.get("progress", "Processing")
                        print(f"🔄 Research in progress: {progress}")
                
                # Wait before next poll
                time.sleep(2)
                
            except Exception as e:
                # Continue polling despite errors
                pass
        
        return "❌ Research timeout. The task is still processing in the background."
    
    def _format_research_results(self, result: Dict[str, Any]) -> str:
        """Format research results for presentation."""
        output = "🔍 **Research Complete!**\n\n"
        
        # Summary
        if result.get("summary"):
            output += f"**Summary:**\n{result['summary']}\n\n"
        
        # Key Findings
        if result.get("key_findings"):
            output += "**Key Findings:**\n"
            for i, finding in enumerate(result["key_findings"], 1):
                output += f"{i}. {finding}\n"
            output += "\n"
        
        # Sources
        if result.get("sources"):
            output += "**Sources:**\n"
            for source in result["sources"][:5]:  # Limit to top 5
                title = source.get("title", "Untitled")
                url = source.get("url", "#")
                snippet = source.get("snippet", "")
                
                output += f"• [{title}]({url})\n"
                if snippet:
                    output += f"  {snippet[:100]}...\n"
            output += "\n"
        
        # Statistics
        if result.get("statistics"):
            output += "**Key Statistics:**\n"
            for stat in result["statistics"]:
                output += f"• {stat}\n"
        
        # Save full results for later use
        self._cache_results(self.task_id, result)
        
        return output
    
    def _cache_results(self, task_id: str, results: Dict[str, Any]):
        """Cache research results for later use by other agents."""
        # In production, this would store in Redis or similar
        # For MVP, we'll use a simple file cache
        cache_dir = "/tmp/research_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{task_id}.json")
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)


# Test the tool if run directly
if __name__ == "__main__":
    tool = ResearchAgentProxy(
        task_id="test-research-123",
        topic="Latest AI trends in social media marketing",
        depth="standard",
        focus_areas="automation, content generation, analytics"
    )
    result = tool.run()
    print(result)
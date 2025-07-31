"""
Command Processor Tool - Parses and executes structured commands
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import requests
from dotenv import load_dotenv
import re
from typing import Dict, Any

load_dotenv()


class CommandProcessor(BaseTool):
    """
    Process structured commands from Slack and execute them via backend API.
    Handles command parsing, validation, and backend communication.
    Creates tasks in Notion and initiates real-time execution.
    """
    
    command: str = Field(
        ..., 
        description="The command to execute, starting with / (e.g., /create-content-post)"
    )
    raw_params: str = Field(
        ..., 
        description="Raw parameter string from user (e.g., topic='AI trends' platform='linkedin')"
    )
    
    def run(self) -> str:
        """Execute the command by parsing parameters and calling backend."""
        # Get environment variables
        backend_url = os.getenv("BACKEND_URL")
        notion_token = os.getenv("NOTION_TOKEN")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not all([backend_url, notion_token, database_id]):
            return "❌ Error: Missing configuration. Please check environment variables."
        
        # Parse parameters from raw string
        params = self._parse_parameters(self.raw_params)
        
        # Validate command
        if not self.command.startswith('/'):
            return f"❌ Error: Command must start with /. Got: {self.command}"
        
        # Create Notion task first
        from notion_client import Client
        notion = Client(auth=notion_token)
        
        try:
            # Prepare task title
            topic = params.get('topic', 'No topic specified')
            task_title = f"{self.command} - {topic}"
            
            # Create task in Notion
            response = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Name": {
                        "title": [
                            {"text": {"content": task_title}}
                        ]
                    },
                    "Status": {
                        "select": {"name": "Waiting"}
                    },
                    "Command Used": {
                        "rich_text": [
                            {"text": {"content": self.command}}
                        ]
                    },
                    "Execution Mode": {
                        "select": {"name": "Instant"}
                    }
                }
            )
            task_id = response["id"]
            
            # Call backend API
            backend_response = requests.post(
                f"{backend_url}/execute-command",
                json={
                    "task_id": task_id,
                    "command": self.command,
                    "params": params,
                    "mode": "Instant"
                },
                timeout=30
            )
            
            if backend_response.status_code == 200:
                return (f"⚡ Executing {self.command} - Task ID: {task_id}\n"
                       f"I'll update you in real-time as the task progresses!")
            else:
                # Update Notion task with error
                notion.pages.update(
                    page_id=task_id,
                    properties={
                        "Status": {"select": {"name": "Error"}}
                    }
                )
                return f"❌ Backend error: {backend_response.text}"
                
        except requests.exceptions.Timeout:
            return "❌ Error: Backend request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "❌ Error: Cannot connect to backend. Please check if the service is running."
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    def _parse_parameters(self, raw_params: str) -> Dict[str, Any]:
        """Parse parameters from raw string format."""
        params = {}
        
        if not raw_params:
            return params
        
        # Pattern to match key='value' or key="value"
        pattern = r"(\w+)=['\"]([^'\"]+)['\"]"
        matches = re.findall(pattern, raw_params)
        
        for key, value in matches:
            # Convert to appropriate type
            if value.lower() in ['true', 'false']:
                params[key] = value.lower() == 'true'
            elif value.isdigit():
                params[key] = int(value)
            else:
                params[key] = value
        
        return params


# Test the tool if run directly
if __name__ == "__main__":
    # Test case
    tool = CommandProcessor(
        command="/create-content-post",
        raw_params="topic='AI trends 2025' platform='linkedin' tone='professional'"
    )
    result = tool.run()
    print(result)
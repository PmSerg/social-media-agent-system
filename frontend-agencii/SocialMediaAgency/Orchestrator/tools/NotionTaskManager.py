"""
Notion Task Manager Tool - Manages tasks in Notion database
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from notion_client import Client
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

load_dotenv()


class NotionTaskManager(BaseTool):
    """
    Manages tasks in Notion database for the Social Media Agency.
    Handles task creation, updates, queries, and status tracking.
    Supports both instant and scheduled execution modes.
    """
    
    action: str = Field(
        ...,
        description="Action to perform: 'create', 'update', 'query', or 'get'"
    )
    
    task_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Data for task creation or update. Required fields depend on action."
    )
    
    task_id: Optional[str] = Field(
        None,
        description="Notion page ID for update or get operations"
    )
    
    filter_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Filter criteria for query operations (e.g., {'status': 'Waiting'})"
    )
    
    def run(self) -> str:
        """Execute the Notion database operation."""
        # Initialize Notion client
        notion_token = os.getenv("NOTION_TOKEN")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not notion_token or not database_id:
            return "❌ Error: Notion configuration missing. Check environment variables."
        
        notion = Client(auth=notion_token)
        
        try:
            if self.action == "create":
                return self._create_task(notion, database_id)
            elif self.action == "update":
                return self._update_task(notion)
            elif self.action == "query":
                return self._query_tasks(notion, database_id)
            elif self.action == "get":
                return self._get_task(notion)
            else:
                return f"❌ Error: Unknown action '{self.action}'"
                
        except Exception as e:
            return f"❌ Notion API error: {str(e)}"
    
    def _create_task(self, notion: Client, database_id: str) -> str:
        """Create a new task in Notion."""
        if not self.task_data:
            return "❌ Error: task_data required for create action"
        
        # Build properties
        properties = {
            "Name": {
                "title": [
                    {"text": {"content": self.task_data.get("name", "Untitled Task")}}
                ]
            },
            "Status": {
                "select": {"name": self.task_data.get("status", "Waiting")}
            }
        }
        
        # Add optional properties
        if "command" in self.task_data:
            properties["Command Used"] = {
                "rich_text": [
                    {"text": {"content": self.task_data["command"]}}
                ]
            }
        
        if "execution_mode" in self.task_data:
            properties["Execution Mode"] = {
                "select": {"name": self.task_data["execution_mode"]}
            }
        
        if "description" in self.task_data:
            properties["Task Description"] = {
                "rich_text": [
                    {"text": {"content": self.task_data["description"]}}
                ]
            }
        
        # Create the page
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        task_id = response["id"]
        return f"✅ Task created successfully! ID: {task_id}"
    
    def _update_task(self, notion: Client) -> str:
        """Update an existing task in Notion."""
        if not self.task_id:
            return "❌ Error: task_id required for update action"
        
        if not self.task_data:
            return "❌ Error: task_data required for update action"
        
        # Build properties to update
        properties = {}
        
        if "status" in self.task_data:
            properties["Status"] = {
                "select": {"name": self.task_data["status"]}
            }
        
        if "research_data" in self.task_data:
            properties["Research Data"] = {
                "rich_text": [
                    {"text": {"content": json.dumps(self.task_data["research_data"], indent=2)}}
                ]
            }
        
        if "content" in self.task_data:
            properties["Content"] = {
                "rich_text": [
                    {"text": {"content": self.task_data["content"]}}
                ]
            }
        
        if "error" in self.task_data:
            properties["Error"] = {
                "rich_text": [
                    {"text": {"content": self.task_data["error"]}}
                ]
            }
        
        # Update the page
        notion.pages.update(
            page_id=self.task_id,
            properties=properties
        )
        
        return f"✅ Task {self.task_id} updated successfully"
    
    def _query_tasks(self, notion: Client, database_id: str) -> str:
        """Query tasks from Notion based on filter criteria."""
        # Build filter
        filter_obj = None
        if self.filter_criteria:
            filter_obj = self._build_filter(self.filter_criteria)
        
        # Query the database
        response = notion.databases.query(
            database_id=database_id,
            filter=filter_obj,
            sorts=[
                {
                    "timestamp": "created_time",
                    "direction": "descending"
                }
            ],
            page_size=10  # Limit results
        )
        
        # Format results
        tasks = []
        for page in response["results"]:
            task = self._extract_task_info(page)
            tasks.append(task)
        
        if not tasks:
            return "No tasks found matching the criteria."
        
        # Format output
        output = f"Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            output += f"📋 {task['name']}\n"
            output += f"   ID: {task['id']}\n"
            output += f"   Status: {task['status']}\n"
            output += f"   Created: {task['created_time']}\n\n"
        
        return output
    
    def _get_task(self, notion: Client) -> str:
        """Get details of a specific task."""
        if not self.task_id:
            return "❌ Error: task_id required for get action"
        
        # Retrieve the page
        page = notion.pages.retrieve(page_id=self.task_id)
        
        # Extract task information
        task = self._extract_task_info(page)
        
        # Format detailed output
        output = f"📋 Task Details:\n\n"
        output += f"Name: {task['name']}\n"
        output += f"ID: {task['id']}\n"
        output += f"Status: {task['status']}\n"
        output += f"Command: {task.get('command', 'N/A')}\n"
        output += f"Execution Mode: {task.get('execution_mode', 'N/A')}\n"
        output += f"Created: {task['created_time']}\n"
        
        if task.get('content'):
            output += f"\nContent Preview:\n{task['content'][:200]}..."
        
        return output
    
    def _build_filter(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Build Notion API filter from criteria."""
        if "status" in criteria:
            return {
                "property": "Status",
                "select": {
                    "equals": criteria["status"]
                }
            }
        return {}
    
    def _extract_task_info(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task information from Notion page object."""
        properties = page["properties"]
        
        # Extract title
        name = "Untitled"
        if "Name" in properties and properties["Name"]["title"]:
            name = properties["Name"]["title"][0]["text"]["content"]
        
        # Extract other properties
        task = {
            "id": page["id"],
            "name": name,
            "created_time": page["created_time"],
            "status": self._get_select_value(properties.get("Status")),
            "command": self._get_text_value(properties.get("Command Used")),
            "execution_mode": self._get_select_value(properties.get("Execution Mode")),
            "content": self._get_text_value(properties.get("Content"))
        }
        
        return task
    
    def _get_select_value(self, prop: Optional[Dict]) -> Optional[str]:
        """Extract value from select property."""
        if prop and prop.get("select"):
            return prop["select"]["name"]
        return None
    
    def _get_text_value(self, prop: Optional[Dict]) -> Optional[str]:
        """Extract value from rich text property."""
        if prop and prop.get("rich_text") and prop["rich_text"]:
            return prop["rich_text"][0]["text"]["content"]
        return None


# Test the tool if run directly
if __name__ == "__main__":
    # Test creating a task
    tool = NotionTaskManager(
        action="create",
        task_data={
            "name": "Test Task - AI Content",
            "status": "Waiting",
            "command": "/create-content-post",
            "execution_mode": "Instant"
        }
    )
    result = tool.run()
    print(result)
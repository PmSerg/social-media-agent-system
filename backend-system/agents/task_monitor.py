"""
Task Monitor - Orchestrates command execution with real-time updates
"""

import asyncio
import aiofiles
import yaml
import os
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx

from config import settings
from api.models import AgentStatus

logger = logging.getLogger(__name__)


class TaskMonitor:
    """
    Monitors and executes tasks with real-time progress updates.
    Handles workflow orchestration and webhook notifications.
    """
    
    def __init__(self, openai_client, notion_client, webhook_client=None):
        self.openai_client = openai_client
        self.notion_client = notion_client
        self.webhook_client = webhook_client or httpx.AsyncClient()
        self.agents = {}
        self._register_agents()
        
    def _register_agents(self):
        """Register available agents."""
        # Import here to avoid circular imports
        from .research_agent import ResearchAgent
        from .copywriter_agent import CopywriterAgent
        
        self.agents = {
            "research": ResearchAgent(self.openai_client),
            "copywriter": CopywriterAgent(self.openai_client)
        }
        logger.info(f"Registered agents: {list(self.agents.keys())}")
    
    async def instant_execution(self, task: Dict[str, Any], command: str):
        """Execute command with real-time updates via webhooks."""
        task_id = task["id"]
        logger.info(f"Starting instant execution for task {task_id}, command: {command}")
        
        try:
            # Load command workflow
            workflow = await self._load_command_workflow(command)
            
            # Initial notification
            await self._send_webhook(task_id, {
                "status": "PROCESSING",
                "message": f"🚀 Starting execution of {command}",
                "timestamp": datetime.utcnow().isoformat()
            }, task.get("webhook_url"))
            
            # Update Notion status
            await self._update_notion_task(task_id, {
                "Status": {"select": {"name": "Processing"}}
            })
            
            # Execute each step
            context = {
                "task_id": task_id,
                "params": task.get("params", {}),
                "results": {}
            }
            
            for step_num, step in enumerate(workflow.get("steps", []), 1):
                agent_name = step["agent"]
                logger.info(f"Executing step {step_num}: {agent_name}")
                
                # Step start notification
                await self._send_webhook(task_id, {
                    "status": "PROCESSING",
                    "message": f"🔄 Step {step_num}: {agent_name} starting...",
                    "agent": agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }, task.get("webhook_url"))
                
                # Execute agent
                agent = self._get_agent(agent_name)
                if not agent:
                    raise ValueError(f"Agent '{agent_name}' not found")
                
                # Prepare agent params
                agent_params = self._prepare_agent_params(step, context)
                result = await agent.execute(context, agent_params)
                
                # Store result in context
                context["results"][agent_name] = result
                
                # Update Notion with intermediate results
                notion_update = {}
                if agent_name == "research":
                    notion_update["Research Data"] = {
                        "rich_text": [{"text": {"content": str(result.dict() if hasattr(result, 'dict') else result)[:2000]}}]
                    }
                elif agent_name == "copywriter":
                    notion_update["Content"] = {
                        "rich_text": [{"text": {"content": str(result.content if hasattr(result, 'content') else result)[:2000]}}]
                    }
                
                if notion_update:
                    await self._update_notion_task(task_id, notion_update)
                
                # Step complete notification
                await self._send_webhook(task_id, {
                    "status": "PROCESSING",
                    "message": f"✅ Step {step_num}: {agent_name} complete",
                    "agent": agent_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": result.dict() if hasattr(result, 'dict') else {"result": str(result)}
                }, task.get("webhook_url"))
                
                # Add delay to prevent overwhelming
                await asyncio.sleep(0.5)
            
            # Final success
            await self._update_notion_task(task_id, {
                "Status": {"select": {"name": "Complete"}}
            })
            
            await self._send_webhook(task_id, {
                "status": "COMPLETE",
                "message": "🎉 Task completed successfully!",
                "timestamp": datetime.utcnow().isoformat(),
                "final_results": context["results"]
            }, task.get("webhook_url"))
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error in task {task_id}: {str(e)}", exc_info=True)
            
            # Error handling
            await self._update_notion_task(task_id, {
                "Status": {"select": {"name": "Error"}},
                "Error": {"rich_text": [{"text": {"content": str(e)}}]}
            })
            
            await self._send_webhook(task_id, {
                "status": "ERROR",
                "message": f"❌ Error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }, task.get("webhook_url"))
            
            raise
    
    async def _load_command_workflow(self, command: str) -> Dict:
        """Load and parse command workflow from .md file."""
        command_name = command.lstrip('/')
        file_path = f"commands/{command_name}.md"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Command file not found: {file_path}")
        
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        
        # Parse workflow from markdown
        workflow = self._parse_workflow_from_markdown(content)
        return workflow
    
    def _parse_workflow_from_markdown(self, content: str) -> Dict:
        """Parse workflow definition from markdown content."""
        workflow = {
            "steps": [],
            "conditions": {},
            "output": {}
        }
        
        # Extract workflow steps
        steps_match = re.search(r'## Workflow Steps?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if steps_match:
            steps_text = steps_match.group(1)
            # Parse numbered steps
            step_pattern = r'\d+\.\s+(\w+)\s+Agent\s*→\s*(.+?)(?=\n\d+\.|\Z)'
            for match in re.finditer(step_pattern, steps_text, re.DOTALL):
                agent_name = match.group(1).lower()
                description = match.group(2).strip()
                
                workflow["steps"].append({
                    "agent": agent_name,
                    "description": description,
                    "params": {}
                })
        
        # Extract conditions
        conditions_match = re.search(r'## Conditions?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if conditions_match:
            conditions_text = conditions_match.group(1)
            # Parse conditions
            condition_pattern = r'-\s*If\s+(.+?):\s*(.+)'
            for match in re.finditer(condition_pattern, conditions_text):
                condition = match.group(1).strip()
                action = match.group(2).strip()
                workflow["conditions"][condition] = action
        
        # Extract parameters
        params_match = re.search(r'## Parameters?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if params_match:
            params_text = params_match.group(1)
            # Parse parameters
            param_pattern = r'-\s*(\w+):\s*(.+?)(?:\((.+?)\))?\s*(?:-\s*(.+))?$'
            workflow["parameters"] = {}
            for match in re.finditer(param_pattern, params_text, re.MULTILINE):
                param_name = match.group(1)
                param_desc = match.group(2).strip()
                param_type = match.group(3) if match.group(3) else "string"
                param_values = match.group(4).strip() if match.group(4) else None
                
                workflow["parameters"][param_name] = {
                    "description": param_desc,
                    "type": param_type,
                    "values": param_values
                }
        
        return workflow
    
    def _prepare_agent_params(self, step: Dict, context: Dict) -> Dict:
        """Prepare parameters for agent execution."""
        params = context["params"].copy()
        
        # Add results from previous agents
        if "research" in context["results"] and step["agent"] == "copywriter":
            params["research_data"] = context["results"]["research"]
        
        # Apply conditions based on parameters
        if step["agent"] == "copywriter":
            platform = params.get("platform", "").lower()
            if platform == "linkedin":
                params["tone"] = params.get("tone", "professional")
                params["max_length"] = 3000
            elif platform == "twitter":
                params["max_length"] = 280
                params["tone"] = params.get("tone", "casual")
        
        return params
    
    def _get_agent(self, agent_name: str):
        """Get agent instance by name."""
        return self.agents.get(agent_name.lower())
    
    async def _update_notion_task(self, task_id: str, properties: Dict):
        """Update Notion task with properties."""
        try:
            await self.notion_client.pages.update(
                page_id=task_id,
                properties=properties
            )
        except Exception as e:
            logger.error(f"Failed to update Notion task {task_id}: {e}")
    
    async def _send_webhook(self, task_id: str, data: Dict, webhook_url: Optional[str] = None):
        """Send webhook notification with retry logic."""
        if not webhook_url:
            webhook_url = f"{settings.webhook_base_url}/progress/{task_id}"
        
        # Add task_id to data
        data["task_id"] = task_id
        
        for attempt in range(settings.webhook_retry_attempts):
            try:
                response = await self.webhook_client.post(
                    webhook_url,
                    json=data,
                    timeout=settings.webhook_timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return
                elif response.status_code == 429:  # Rate limited
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.warning(f"Webhook failed with status {response.status_code}: {response.text}")
                    
            except httpx.TimeoutException:
                logger.warning(f"Webhook timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Webhook error on attempt {attempt + 1}: {e}")
            
            if attempt < settings.webhook_retry_attempts - 1:
                await asyncio.sleep(2 ** attempt)
    
    async def scheduled_execution(self, task: Dict[str, Any], command: str):
        """Execute scheduled tasks (future implementation)."""
        # For MVP, this is a placeholder
        logger.info(f"Scheduled execution not implemented for task {task['id']}")
        raise NotImplementedError("Scheduled execution will be implemented in Phase 2")
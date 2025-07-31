"""
Orchestrator Agent - Main client-facing agent for Social Media Agency
"""

from agency_swarm import Agent
from .tools.CommandProcessor import CommandProcessor
from .tools.NotionTaskManager import NotionTaskManager
from .tools.ResearchAgentProxy import ResearchAgentProxy
from .tools.CopywriterAgentProxy import CopywriterAgentProxy


class Orchestrator(Agent):
    """
    The Orchestrator Agent serves as the primary interface between users and the Social Media Agency.
    It processes natural language requests, interprets commands, delegates tasks to backend agents,
    and provides real-time updates on task progress.
    """
    
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            description="I'm your Social Media Content Assistant. I help you create research-backed, "
                       "platform-optimized content through simple commands or natural conversation.",
            instructions="./instructions.md",
            tools=[
                CommandProcessor,
                NotionTaskManager,
                ResearchAgentProxy,
                CopywriterAgentProxy
            ],
            model="gpt-4-turbo-preview",  # Latest GPT-4 model for best performance
            temperature=0.7,
            max_prompt_tokens=4000,
        )
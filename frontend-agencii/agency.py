#!/usr/bin/env python3
"""
Social Media MVP Agency - Main Entry Point
This is the main Agency Swarm entry point for the Agencii platform deployment.
"""

from agency_swarm import Agency
from SocialMediaAgency.Orchestrator.Orchestrator import Orchestrator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Orchestrator agent
orchestrator = Orchestrator()

# Create the agency with communication flows
agency = Agency(
    [orchestrator],  # Single agent for MVP
    shared_instructions="./SocialMediaAgency/agency_manifesto.md",
    temperature=0.7,  # Balanced creativity/consistency
    max_prompt_tokens=4000,  # Reasonable context window
)

if __name__ == "__main__":
    # Run the agency in demo mode for testing
    # In production, Agencii platform handles the execution
    agency.demo_gradio()
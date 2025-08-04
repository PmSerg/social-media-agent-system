#!/usr/bin/env python3
"""
Test script for archetype-based content generation workflow
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend-system to path
backend_path = Path(__file__).parent / "backend-system"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment
load_dotenv(backend_path / ".env")

from agents.research_agent import ResearchAgent
from agents.copywriter_agent import CopywriterAgent
from shared.notion_client import get_notion_client, create_task_page, update_task_page

async def test_workflow():
    """Test the complete workflow with archetypes"""
    
    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Initialize agents
    research_agent = ResearchAgent(openai_client)
    copywriter_agent = CopywriterAgent(openai_client)
    
    # Test parameters
    topic = "Digital banking solutions for small businesses"
    platform = "linkedin"
    tone = "professional"
    
    print(f"\n🚀 Starting archetype-based content generation")
    print(f"Topic: {topic}")
    print(f"Platform: {platform}")
    print(f"Tone: {tone}")
    
    # Create Notion task
    print("\n📝 Creating Notion task...")
    task_id = await create_task_page(
        title=f"Test: {topic}",
        status="In Progress",
        command="/create-content-post",
        execution_mode="Instant",
        description="Testing archetype-based content generation"
    )
    print(f"Created task: {task_id}")
    
    # Context for agents
    context = {
        "task_id": task_id
    }
    
    # Research phase
    print("\n🔍 Research Agent starting...")
    research_params = {
        "topic": topic,
        "depth": "standard",
        "focus_areas": ["benefits", "features", "trends"]
    }
    
    research_result = await research_agent.execute(context, research_params)
    
    print(f"✅ Research completed!")
    print(f"   - Selected archetype: {context.get('selected_archetype', 'Unknown')}")
    print(f"   - Sources found: {len(research_result.sources)}")
    print(f"   - Key findings: {len(research_result.key_findings)}")
    
    # Update Notion with research
    await update_task_page(task_id, {
        "Research Data": {
            "rich_text": [{
                "text": {
                    "content": f"Archetype: {context.get('selected_archetype')}\n\n"
                              f"Summary: {research_result.summary}\n\n"
                              f"Findings: {', '.join(research_result.key_findings[:3])}"[:2000]
                }
            }]
        },
        "Agent Status": {"select": {"name": "Copywriter Agent"}}
    })
    
    # Content generation phase
    print("\n✍️  Copywriter Agent starting...")
    copywriter_params = {
        "platform": platform,
        "topic": topic,
        "tone": tone,
        "research_data": research_result.dict(),
        "keywords": ["digital banking", "small business", "financial solutions"],
        "call_to_action": "Learn how Kea can transform your business banking"
    }
    
    content_result = await copywriter_agent.execute(context, copywriter_params)
    
    print(f"✅ Content generated!")
    print(f"   - Character count: {content_result.character_count}")
    print(f"   - Hashtags: {', '.join(['#' + tag for tag in content_result.hashtags])}")
    print(f"   - CTA effectiveness: {content_result.cta_effectiveness}/10")
    
    # Update Notion with final content
    await update_task_page(task_id, {
        "Final Text": {
            "rich_text": [{
                "text": {"content": content_result.content[:2000]}
            }]
        },
        "Status": {"select": {"name": "Published"}},
        "Agent Status": {"select": {"name": "Complete"}}
    })
    
    # Display results
    print("\n" + "="*60)
    print(f"ARCHETYPE USED: {context.get('selected_archetype')}")
    print("="*60)
    print("\nGENERATED CONTENT:")
    print("-"*60)
    print(content_result.content)
    print("-"*60)
    print(f"\nHASHTAGS: {' '.join(['#' + tag for tag in content_result.hashtags])}")
    print(f"\nOPTIMAL POSTING TIME: {content_result.optimal_posting_time}")
    print("\nENGAGEMENT TIPS:")
    for tip in content_result.engagement_tips:
        print(f"  • {tip}")
    
    print(f"\n✅ Workflow complete! Check Notion task: {task_id}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
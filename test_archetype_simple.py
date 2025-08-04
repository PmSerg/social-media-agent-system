#!/usr/bin/env python3
"""
Simple test to demonstrate archetype functionality
"""

import random
from typing import Dict, Any

# Архетипы Kea
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

def get_archetype_by_weight() -> Dict[str, Any]:
    """Select archetype based on percentage weights."""
    weighted_choices = []
    for key, archetype in ARCHETYPES.items():
        weighted_choices.extend([key] * archetype["percentage"])
    
    selected_key = random.choice(weighted_choices)
    return ARCHETYPES[selected_key]

def simulate_research(topic: str, archetype: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate research with archetype perspective."""
    print(f"\n🔍 Research Agent")
    print(f"   Topic: {topic}")
    print(f"   Archetype: {archetype['name']}")
    
    # Simulate different search queries based on archetype
    if archetype["name"] == "Caregiver":
        search_query = f"{topic} support trust reliability customer care"
        findings = [
            "Small businesses need reliable banking partners they can trust",
            "24/7 customer support is crucial for business continuity",
            "Personal relationship managers make a difference"
        ]
    elif archetype["name"] == "Explorer":
        search_query = f"{topic} innovative solutions new opportunities technology"
        findings = [
            "AI-powered banking is revolutionizing small business finance",
            "New fintech solutions offer unprecedented opportunities",
            "Digital transformation is key to competitive advantage"
        ]
    else:  # Regular Guy
        search_query = f"{topic} simple practical easy everyday business"
        findings = [
            "Simple banking solutions save time for busy entrepreneurs",
            "Easy-to-use mobile apps are essential for modern businesses",
            "Practical features matter more than complexity"
        ]
    
    print(f"   Search query: {search_query}")
    print(f"   Key findings: {len(findings)}")
    
    return {
        "archetype": archetype["name"],
        "findings": findings,
        "summary": f"Research focused on {archetype['traits'][0]} aspects of {topic}"
    }

def simulate_content_generation(topic: str, archetype: Dict[str, Any], research: Dict[str, Any]) -> str:
    """Simulate content generation with archetype voice."""
    print(f"\n✍️  Copywriter Agent")
    print(f"   Using {archetype['name']} voice: {archetype['voice']}")
    
    # Generate content based on archetype
    if archetype["name"] == "Caregiver":
        content = f"""At Kea, we understand the challenges small businesses face every day. 

That's why we've built a banking platform that truly cares about your success. With our dedicated support team available 24/7 and personal relationship managers who know your business, we're here to nurture your growth every step of the way.

{research['findings'][0]}. Let us be your trusted financial partner.

#TrustedBanking #SmallBusinessSupport #KeaCares #BusinessGrowth #FinancialPartner"""
    
    elif archetype["name"] == "Explorer":
        content = f"""🚀 The future of small business banking is here!

Kea is pioneering the next generation of financial services with AI-powered insights, instant global payments, and innovative solutions that open new opportunities for your business.

{research['findings'][0]}. Join us in exploring what's possible.

#FintechInnovation #FutureOfBanking #KeaExplorer #DigitalTransformation #BusinessInnovation"""
    
    else:  # Regular Guy
        content = f"""Running a business is hard enough without complicated banking.

That's why Kea keeps it simple. Easy online account opening, straightforward pricing, and a mobile app that just works. No jargon, no hidden fees – just practical banking for real businesses.

{research['findings'][0]}. Banking made simple, just how it should be.

#SimpleBanking #SmallBusiness #KeaSimple #PracticalSolutions #EasyBanking"""
    
    return content

def main():
    """Run the archetype demonstration."""
    print("="*60)
    print("KEA ARCHETYPE-BASED CONTENT GENERATION DEMO")
    print("="*60)
    
    topic = "Digital banking solutions for small businesses"
    
    # Simulate multiple runs to show distribution
    print("\n📊 Running 10 simulations to show archetype distribution:")
    archetype_counts = {"Caregiver": 0, "Explorer": 0, "Regular Guy": 0}
    
    for i in range(10):
        archetype = get_archetype_by_weight()
        archetype_counts[archetype["name"]] += 1
        print(f"   Run {i+1}: {archetype['name']}")
    
    print("\nDistribution:")
    for name, count in archetype_counts.items():
        expected = next(a["percentage"] for a in ARCHETYPES.values() if a["name"] == name)
        print(f"   {name}: {count}/10 ({count*10}%) - Expected: {expected}%")
    
    # Run one complete example
    print("\n" + "="*60)
    print("COMPLETE WORKFLOW EXAMPLE")
    print("="*60)
    
    # Select archetype
    selected_archetype = get_archetype_by_weight()
    print(f"\n🎯 Selected Archetype: {selected_archetype['name']}")
    print(f"   Voice: {selected_archetype['voice']}")
    print(f"   Traits: {', '.join(selected_archetype['traits'])}")
    print(f"   Description: {selected_archetype['description']}")
    
    # Research phase
    research_result = simulate_research(topic, selected_archetype)
    
    # Content generation phase
    content = simulate_content_generation(topic, selected_archetype, research_result)
    
    # Display final result
    print("\n" + "="*60)
    print("GENERATED CONTENT")
    print("="*60)
    print(content)
    print("\n" + "="*60)
    
    print(f"\n✅ Workflow complete with {selected_archetype['name']} archetype!")

if __name__ == "__main__":
    main()
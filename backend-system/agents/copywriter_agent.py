"""
Copywriter Agent - Creates platform-optimized social media content
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from config import settings
from api.models import ContentResult, ResearchResult
from shared.notion_client import get_archetype_by_name, get_archetype_voice, add_task_archetype, get_brand_guidelines

logger = logging.getLogger(__name__)


class CopywriterAgent:
    """
    Copywriter Agent that creates engaging, platform-optimized content
    based on research data and user requirements.
    """
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.platform_limits = settings.get_platform_limits()
        self.tone_prompts = settings.get_tone_prompts()
        
    async def execute(self, context: Dict[str, Any], params: Dict[str, Any]) -> ContentResult:
        """
        Generate content based on platform, topic, and research data.
        
        Args:
            context: Execution context with task_id and previous results
            params: Content parameters including platform, topic, tone, research_data
            
        Returns:
            ContentResult with optimized content and metadata
        """
        platform = params.get("platform", "linkedin").lower()
        topic = params.get("topic", "")
        tone = params.get("tone", "professional").lower()
        research_data = params.get("research_data", {})
        keywords = params.get("keywords", [])
        call_to_action = params.get("call_to_action", "")
        
        # Get archetype from context (set by Research Agent)
        archetype_name = context.get("selected_archetype", "Caregiver")
        archetype = get_archetype_by_name(archetype_name)
        
        logger.info(f"Generating {platform} content about: {topic}, tone: {tone}, archetype: {archetype_name}")
        
        # Get brand guidelines for platform
        brand_guidelines = await get_brand_guidelines(platform.capitalize())
        
        try:
            # Generate content with archetype voice
            content = await self._generate_content(
                platform, topic, tone, research_data, keywords, call_to_action, archetype, brand_guidelines
            )
            
            # Optimize for platform
            optimized_content = self._optimize_for_platform(content, platform)
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(topic, platform, research_data, archetype)
            
            # Create engagement tips
            engagement_tips = self._create_engagement_tips(platform, tone)
            
            # Determine optimal posting time
            optimal_time = self._suggest_posting_time(platform)
            
            # Score CTA effectiveness
            cta_score = self._score_cta(optimized_content, call_to_action)
            
            # Update task with archetype used
            if context.get("task_id"):
                await add_task_archetype(context["task_id"], archetype_name)
            
            result = ContentResult(
                content=optimized_content,
                hashtags=hashtags,
                character_count=len(optimized_content),
                platform_optimized=True,
                tone=tone,
                engagement_tips=engagement_tips,
                optimal_posting_time=optimal_time,
                cta_effectiveness=cta_score
            )
            
            logger.info(f"Content generated: {result.character_count} chars, {len(hashtags)} hashtags, archetype: {archetype_name}")
            return result
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}", exc_info=True)
            # Return minimal content on error
            return ContentResult(
                content=f"Error generating content: {str(e)}",
                hashtags=[],
                character_count=0,
                platform_optimized=False,
                tone=tone
            )
    
    async def _generate_content(
        self,
        platform: str,
        topic: str,
        tone: str,
        research_data: Any,
        keywords: List[str],
        call_to_action: str,
        archetype: Dict[str, Any],
        brand_guidelines: Optional[Dict[str, Any]]
    ) -> str:
        """Generate content using GPT-4."""
        # Prepare research context
        research_context = self._prepare_research_context(research_data)
        
        # Get platform-specific requirements
        char_limit = self.platform_limits.get(platform, 3000)
        tone_guidance = self.tone_prompts.get(tone, "")
        
        # Build keywords string
        keywords_text = f"Include these keywords naturally: {', '.join(keywords)}" if keywords else ""
        
        # Build CTA instruction
        cta_text = f"End with this call-to-action: {call_to_action}" if call_to_action else ""
        
        # Build archetype guidance
        archetype_traits = ', '.join(archetype["traits"])
        archetype_voice = archetype["voice"]
        
        # Extract brand guidelines if available
        guidelines_text = ""
        if brand_guidelines:
            if brand_guidelines.get("brand_guidelines"):
                guidelines_text += f"\nBrand Guidelines: {brand_guidelines['brand_guidelines']}"
            if brand_guidelines.get("archetype_guidelines"):
                guidelines_text += f"\nArchetype Guidelines: {brand_guidelines['archetype_guidelines']}"
        
        prompt = f"""
        Create {platform} content about: {topic}
        
        Platform: {platform} (max {char_limit} characters)
        Base Tone: {tone} - {tone_guidance}
        
        Brand Voice: {archetype_voice}
        Archetype: {archetype['name']} - {archetype['description']}
        Personality Traits: {archetype_traits}
        
        {guidelines_text}
        
        {keywords_text}
        {cta_text}
        
        Research Context:
        {research_context}
        
        Requirements:
        1. Write in the {archetype['name']} voice - be {archetype_traits}
        2. Optimize for {platform} best practices
        3. Make it engaging and shareable
        4. Include relevant insights from research
        5. Stay within character limit
        6. Use appropriate formatting for the platform
        
        Generate only the post content, no explanations.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a social media copywriter for Kea brand. You embody the {archetype['name']} archetype: {archetype['description']}. Your voice is {archetype_voice}."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Balanced creativity
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            logger.error(f"GPT-4 content generation error: {e}")
            raise
    
    def _optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimize content for specific platform requirements."""
        char_limit = self.platform_limits.get(platform, 3000)
        
        if platform == "twitter":
            # Ensure it fits in 280 characters
            if len(content) > char_limit:
                # Try to cut at sentence boundary
                sentences = content.split('. ')
                optimized = ""
                for sentence in sentences:
                    if len(optimized + sentence + ". ") <= char_limit - 20:  # Leave room for hashtags
                        optimized += sentence + ". "
                    else:
                        break
                content = optimized.rstrip()
                if not content:
                    content = content[:char_limit-20] + "..."
        
        elif platform == "linkedin":
            # Add professional formatting
            # Ensure paragraphs are well-spaced
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # Truncate if too long
            if len(content) > char_limit:
                content = content[:char_limit-50]
                # Find last complete sentence
                last_period = content.rfind('.')
                if last_period > char_limit * 0.8:
                    content = content[:last_period+1]
                else:
                    content += "..."
        
        return content.strip()
    
    async def _generate_hashtags(
        self,
        topic: str,
        platform: str,
        research_data: Any,
        archetype: Dict[str, Any]
    ) -> List[str]:
        """Generate relevant hashtags."""
        # Extract keywords from research if available
        research_keywords = []
        if isinstance(research_data, dict):
            if "key_findings" in research_data:
                research_keywords = self._extract_keywords_from_findings(
                    research_data.get("key_findings", [])
                )
        
        # Add archetype-specific hashtag guidance
        archetype_hashtag_hints = {
            "Caregiver": ["support", "trust", "together", "community"],
            "Explorer": ["innovation", "future", "technology", "solutions"],
            "Regular Guy": ["simple", "practical", "business", "everyday"]
        }
        
        hints = archetype_hashtag_hints.get(archetype["name"], [])
        
        prompt = f"""
        Generate {3 if platform == 'twitter' else 5} relevant hashtags for a {platform} post about: {topic}
        
        Brand archetype: {archetype['name']}
        Hashtag themes: {', '.join(hints)}
        Additional context: {', '.join(research_keywords[:5])}
        
        Requirements:
        - Popular and trending hashtags
        - Mix of broad and specific tags
        - Align with {archetype['name']} archetype values
        - No spaces, proper camelCase
        - Return as JSON array
        
        Example: ["TrustedBanking", "InnovativeFinance", "SimpleBusiness"]
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": f"You are a social media hashtag expert for Kea brand with {archetype['name']} personality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Extract hashtags from various possible formats
            if isinstance(data, dict):
                hashtags = data.get("hashtags", [])
            elif isinstance(data, list):
                hashtags = data
            else:
                hashtags = []
            
            # Clean hashtags
            cleaned = []
            for tag in hashtags:
                tag = str(tag).strip().lstrip('#')
                if tag and len(tag) <= 30:  # Reasonable length
                    cleaned.append(tag)
            
            return cleaned[:5]  # Max 5 hashtags
            
        except Exception as e:
            logger.error(f"Hashtag generation error: {e}")
            # Fallback hashtags
            return self._generate_fallback_hashtags(topic, platform)
    
    def _create_engagement_tips(self, platform: str, tone: str) -> List[str]:
        """Create platform-specific engagement tips."""
        tips = []
        
        if platform == "linkedin":
            tips = [
                "Post during business hours (9-10 AM or 4-5 PM) for maximum visibility",
                "Ask a thought-provoking question to encourage comments",
                "Tag relevant people or companies to expand reach",
                "Use LinkedIn polls for increased engagement"
            ]
        elif platform == "twitter":
            tips = [
                "Tweet during peak hours (9-10 AM or 7-9 PM EST)",
                "Use 1-2 hashtags maximum for better engagement",
                "Include a compelling visual or GIF",
                "Retweet with comment for additional visibility"
            ]
        
        # Add tone-specific tips
        if tone == "professional":
            tips.append("Share data or statistics to add credibility")
        elif tone == "casual":
            tips.append("Use emojis sparingly to add personality")
        
        return tips[:3]  # Return top 3 tips
    
    def _suggest_posting_time(self, platform: str) -> str:
        """Suggest optimal posting time based on platform."""
        posting_times = {
            "linkedin": "Tuesday-Thursday, 9-10 AM or 4-5 PM (local time)",
            "twitter": "Weekdays, 9-10 AM or 7-9 PM EST",
            "facebook": "Wednesday-Friday, 1-4 PM (local time)",
            "instagram": "Monday-Friday, 11 AM-1 PM or 7-9 PM (local time)"
        }
        
        return posting_times.get(platform, "Check your analytics for best times")
    
    def _score_cta(self, content: str, requested_cta: str) -> int:
        """Score the effectiveness of the call-to-action."""
        if not requested_cta:
            return 5  # Neutral score if no CTA requested
        
        content_lower = content.lower()
        cta_lower = requested_cta.lower()
        
        score = 5  # Base score
        
        # Check if CTA is present
        if cta_lower in content_lower:
            score += 2
        
        # Check for action words
        action_words = ["learn", "discover", "join", "share", "comment", "download", "sign up", "register"]
        for word in action_words:
            if word in content_lower:
                score += 1
                break
        
        # Check positioning (better if near the end)
        if len(content) > 100:
            last_quarter = content_lower[-len(content)//4:]
            if any(word in last_quarter for word in action_words):
                score += 1
        
        # Check for urgency
        urgency_words = ["now", "today", "limited", "exclusive", "don't miss"]
        if any(word in content_lower for word in urgency_words):
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _prepare_research_context(self, research_data: Any) -> str:
        """Prepare research data for content generation."""
        if not research_data:
            return "No research data available."
        
        context_parts = []
        
        # Handle different research data formats
        if isinstance(research_data, ResearchResult):
            research_data = research_data.dict()
        elif hasattr(research_data, 'dict'):
            research_data = research_data.dict()
        
        if isinstance(research_data, dict):
            if "summary" in research_data:
                context_parts.append(f"Summary: {research_data['summary']}")
            
            if "key_findings" in research_data:
                findings = research_data["key_findings"][:3]  # Top 3
                context_parts.append("Key Findings:")
                for finding in findings:
                    context_parts.append(f"- {finding}")
            
            if "statistics" in research_data and research_data["statistics"]:
                context_parts.append("\nRelevant Statistics:")
                for stat in research_data["statistics"][:2]:  # Top 2
                    context_parts.append(f"- {stat}")
            
            if "trends" in research_data and research_data["trends"]:
                context_parts.append("\nCurrent Trends:")
                for trend in research_data["trends"][:2]:  # Top 2
                    context_parts.append(f"- {trend}")
        
        return "\n".join(context_parts) if context_parts else "No structured research data."
    
    def _extract_keywords_from_findings(self, findings: List[str]) -> List[str]:
        """Extract potential keywords from research findings."""
        keywords = []
        
        # Simple keyword extraction (in production, use NLP)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        
        for finding in findings:
            words = finding.lower().split()
            for word in words:
                word = word.strip('.,!?";')
                if len(word) > 3 and word not in stop_words and word not in keywords:
                    keywords.append(word)
        
        return keywords[:10]
    
    def _generate_fallback_hashtags(self, topic: str, platform: str) -> List[str]:
        """Generate basic fallback hashtags."""
        # Simple hashtag generation from topic
        words = topic.lower().split()
        hashtags = []
        
        # Create hashtags from topic words
        for word in words[:3]:
            word = word.strip('.,!?";')
            if len(word) > 3:
                hashtags.append(word.capitalize())
        
        # Add platform-specific generic tags
        if platform == "linkedin":
            hashtags.extend(["Business", "Professional"])
        elif platform == "twitter":
            hashtags.append("Trending")
        
        return hashtags[:3]
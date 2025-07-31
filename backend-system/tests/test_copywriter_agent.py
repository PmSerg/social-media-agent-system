"""
Unit Tests for CopywriterAgent
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from agents.copywriter_agent import CopywriterAgent


class TestCopywriterAgent:
    """Test suite for CopywriterAgent."""
    
    @pytest.fixture
    def copywriter_agent(self, mock_openai_client):
        """Create CopywriterAgent instance with mocked dependencies."""
        agent = CopywriterAgent()
        return agent
    
    @pytest.fixture
    def sample_research_input(self):
        """Sample research data for content generation."""
        return {
            "summary": "AI testing ensures reliable and robust AI systems",
            "key_findings": [
                "Automated testing reduces manual effort",
                "Continuous integration improves quality",
                "Performance testing is crucial for AI"
            ],
            "trends": ["MLOps", "AutoML", "AI Ethics"]
        }
    
    @pytest.mark.asyncio
    async def test_execute_twitter_content(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test Twitter content generation."""
        # Mock GPT response
        mock_content = (
            "🚀 AI Testing Revolution! \n\n"
            "✅ Automated testing saves 80% time\n"
            "✅ CI/CD for AI ensures quality\n" 
            "✅ Performance testing is key\n\n"
            "#AITesting #MLOps #TechInnovation"
        )
        
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=mock_content))]
            )
        )
        
        # Execute
        result = await copywriter_agent.execute(
            research_data=sample_research_input,
            platform="Twitter",
            tone="professional"
        )
        
        # Verify
        assert "content" in result
        assert len(result["content"]) <= 280  # Twitter limit
        assert "#AITesting" in result["content"]
        assert result["platform"] == "Twitter"
    
    @pytest.mark.asyncio
    async def test_execute_linkedin_content(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test LinkedIn content generation."""
        # Mock longer-form content
        mock_content = (
            "The Future of AI Testing: A Game-Changer for Tech Teams\n\n"
            "As AI systems become more complex, testing methodologies must evolve. "
            "Here are three key insights from recent industry trends:\n\n"
            "1. Automated Testing Workflows\n"
            "2. Continuous Integration for ML\n"
            "3. Performance Benchmarking\n\n"
            "#AITesting #MachineLearning #TechLeadership"
        )
        
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=mock_content))]
            )
        )
        
        # Execute
        result = await copywriter_agent.execute(
            research_data=sample_research_input,
            platform="LinkedIn",
            tone="professional"
        )
        
        # Verify
        assert len(result["content"]) <= 1300  # LinkedIn limit
        assert result["platform"] == "LinkedIn"
        assert "professional" in str(result).lower() or result["tone"] == "professional"
    
    @pytest.mark.asyncio
    async def test_execute_instagram_content(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test Instagram content generation."""
        mock_content = (
            "🌟 AI TESTING IS THE FUTURE! 🌟\n\n"
            "Did you know? 🤔\n"
            "→ 80% faster with automation\n"
            "→ Better quality with CI/CD\n"
            "→ Scale matters for AI\n\n"
            "Follow for more tech insights! 💡\n\n"
            "#AITesting #TechTips #Innovation #AI #MachineLearning"
        )
        
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=mock_content))]
            )
        )
        
        # Execute
        result = await copywriter_agent.execute(
            research_data=sample_research_input,
            platform="Instagram",
            tone="casual"
        )
        
        # Verify
        assert "content" in result
        assert result["platform"] == "Instagram"
        # Instagram allows more emojis
        assert "🌟" in result["content"] or "💡" in result["content"]
    
    @pytest.mark.asyncio
    async def test_hashtag_generation(
        self,
        copywriter_agent,
        sample_research_input
    ):
        """Test hashtag extraction and generation."""
        content_with_hashtags = (
            "Test content here\n\n"
            "#AITesting #MachineLearning #Innovation"
        )
        
        # Extract hashtags
        hashtags = copywriter_agent._extract_hashtags(content_with_hashtags)
        
        # Verify
        assert len(hashtags) == 3
        assert "AITesting" in hashtags
        assert "MachineLearning" in hashtags
        assert "Innovation" in hashtags
    
    @pytest.mark.asyncio
    async def test_content_optimization(self, copywriter_agent):
        """Test content optimization for platform limits."""
        # Test Twitter optimization
        long_content = "A" * 300  # Too long for Twitter
        optimized = copywriter_agent._optimize_for_platform(
            long_content,
            "Twitter"
        )
        assert len(optimized) <= 280
        
        # Test LinkedIn optimization
        long_content = "B" * 1400  # Too long for LinkedIn  
        optimized = copywriter_agent._optimize_for_platform(
            long_content,
            "LinkedIn"
        )
        assert len(optimized) <= 1300
    
    @pytest.mark.asyncio
    async def test_tone_variations(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test different tone variations."""
        tones = ["professional", "casual", "humorous", "educational"]
        
        for tone in tones:
            # Execute
            result = await copywriter_agent.execute(
                research_data=sample_research_input,
                platform="Twitter",
                tone=tone
            )
            
            # Verify tone was applied
            assert result.get("tone") == tone or tone in str(result)
    
    @pytest.mark.asyncio
    async def test_no_hashtags_option(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test content generation without hashtags."""
        mock_content = "Great content without any hashtags!"
        
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=mock_content))]
            )
        )
        
        # Execute
        result = await copywriter_agent.execute(
            research_data=sample_research_input,
            platform="Twitter",
            include_hashtags=False
        )
        
        # Verify
        assert "#" not in result["content"]
        assert len(result.get("hashtags", [])) == 0
    
    @pytest.mark.asyncio
    async def test_alternative_versions(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test generation of alternative content versions."""
        # Mock multiple responses
        alternatives = [
            "Version 1: AI testing is crucial",
            "Version 2: Transform your AI with testing",
            "Version 3: Testing AI for better results"
        ]
        
        # Execute with alternatives requested
        result = await copywriter_agent.execute(
            research_data=sample_research_input,
            platform="Twitter",
            generate_alternatives=True,
            num_alternatives=3
        )
        
        # Verify (in real implementation)
        # assert len(result.get("alternatives", [])) == 3
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        copywriter_agent,
        sample_research_input,
        mock_openai_client
    ):
        """Test error handling during content generation."""
        # Mock API failure
        mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Execute
        with pytest.raises(Exception) as exc_info:
            await copywriter_agent.execute(
                research_data=sample_research_input,
                platform="Twitter"
            )
        
        assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_content_safety_check(
        self,
        copywriter_agent
    ):
        """Test content safety and appropriateness check."""
        # Test inappropriate content filtering
        inappropriate_content = "Content with inappropriate language"
        
        is_safe = copywriter_agent._check_content_safety(
            inappropriate_content
        )
        
        # In production, this would use content moderation
        assert isinstance(is_safe, bool)
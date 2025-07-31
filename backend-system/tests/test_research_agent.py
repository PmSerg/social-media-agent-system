"""
Unit Tests for ResearchAgent
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from agents.research_agent import ResearchAgent


class TestResearchAgent:
    """Test suite for ResearchAgent."""
    
    @pytest.fixture
    def research_agent(self, mock_openai_client):
        """Create ResearchAgent instance with mocked dependencies."""
        agent = ResearchAgent()
        return agent
    
    @pytest.fixture
    def mock_serpapi_response(self):
        """Mock SerpAPI response."""
        return {
            "search_metadata": {"status": "Success"},
            "organic_results": [
                {
                    "title": "AI Testing Best Practices",
                    "link": "https://example.com/ai-testing",
                    "snippet": "Comprehensive guide to testing AI systems..."
                },
                {
                    "title": "Machine Learning Quality Assurance",
                    "link": "https://example.com/ml-qa", 
                    "snippet": "Ensuring quality in ML applications..."
                }
            ],
            "answer_box": {
                "answer": "AI testing involves validating model performance"
            }
        }
    
    @pytest.mark.asyncio
    async def test_execute_research_success(
        self,
        research_agent,
        mock_serpapi_response,
        mock_openai_client
    ):
        """Test successful research execution."""
        # Mock web search
        with patch("serpapi.search", return_value=mock_serpapi_response):
            # Execute
            result = await research_agent.execute(
                topic="AI Testing",
                max_results=5
            )
        
        # Verify result structure
        assert "summary" in result
        assert "key_findings" in result
        assert "sources" in result
        assert "trends" in result
        
        # Verify content
        assert len(result["sources"]) > 0
        assert isinstance(result["key_findings"], list)
    
    @pytest.mark.asyncio
    async def test_execute_with_search_failure(
        self,
        research_agent,
        mock_openai_client
    ):
        """Test research with search API failure."""
        # Mock search failure
        with patch("serpapi.search", side_effect=Exception("API Error")):
            # Execute - should fallback to general knowledge
            result = await research_agent.execute(
                topic="AI Testing"
            )
        
        # Verify fallback worked
        assert "summary" in result
        assert "Note: Web search unavailable" in result.get("summary", "")
    
    @pytest.mark.asyncio
    async def test_search_web(self, research_agent, mock_serpapi_response):
        """Test web search functionality."""
        with patch("serpapi.search", return_value=mock_serpapi_response):
            # Execute
            results = await research_agent._search_web("AI Testing")
        
        # Verify
        assert len(results) == 2
        assert results[0]["title"] == "AI Testing Best Practices"
        assert "link" in results[0]
        assert "snippet" in results[0]
    
    @pytest.mark.asyncio
    async def test_analyze_content(self, research_agent, mock_openai_client):
        """Test content analysis with GPT-4."""
        # Setup mock response
        analysis_response = json.dumps({
            "summary": "AI testing is essential",
            "key_points": ["Unit testing", "Integration testing"],
            "trends": ["Automated testing"]
        })
        
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=analysis_response))]
            )
        )
        
        # Execute
        result = await research_agent._analyze_content(
            "AI Testing",
            [{"snippet": "Test content"}]
        )
        
        # Verify
        assert result["summary"] == "AI testing is essential"
        assert len(result["key_points"]) == 2
        assert "Automated testing" in result["trends"]
    
    @pytest.mark.asyncio
    async def test_identify_trends(self, research_agent):
        """Test trend identification."""
        search_results = [
            {"snippet": "AI automation is growing rapidly"},
            {"snippet": "Machine learning automation tools"},
            {"snippet": "Automated testing for AI models"}
        ]
        
        # Execute
        trends = research_agent._identify_trends(search_results)
        
        # Verify
        assert isinstance(trends, list)
        assert len(trends) > 0
        # Should identify "automation" as a trend
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, research_agent):
        """Test rate limiting for search API."""
        with patch("backend-system.shared.rate_limiter.check_rate_limit") as mock_check:
            mock_check.return_value = False  # Rate limit exceeded
            
            with patch("serpapi.search") as mock_search:
                # Execute
                results = await research_agent._search_web("test")
                
                # Verify search was not called due to rate limit
                mock_search.assert_not_called()
                assert results == []
    
    @pytest.mark.asyncio
    async def test_execute_with_platform_context(
        self,
        research_agent,
        mock_serpapi_response,
        mock_openai_client
    ):
        """Test research with platform-specific context."""
        with patch("serpapi.search", return_value=mock_serpapi_response):
            # Execute with platform context
            result = await research_agent.execute(
                topic="AI Testing",
                platform="LinkedIn",
                additional_context="Focus on enterprise solutions"
            )
        
        # Verify platform context was considered
        # (In real implementation, this would affect search queries)
        assert "summary" in result
    
    @pytest.mark.asyncio
    async def test_search_retry_logic(self, research_agent):
        """Test retry logic for failed searches."""
        call_count = 0
        
        def mock_search(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return {"organic_results": []}
        
        with patch("serpapi.search", side_effect=mock_search):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                # Execute
                results = await research_agent._search_web("test")
                
                # Verify retry happened
                assert call_count == 2
    
    @pytest.mark.asyncio 
    async def test_content_filtering(self, research_agent):
        """Test filtering of inappropriate content."""
        search_results = [
            {"snippet": "Professional AI testing guide"},
            {"snippet": "Inappropriate content here"},
            {"snippet": "Technical best practices"}
        ]
        
        # Execute filtering
        filtered = research_agent._filter_content(search_results)
        
        # Verify inappropriate content removed
        assert len(filtered) == 2
        assert all("inappropriate" not in r["snippet"].lower() for r in filtered)
"""
Research Agent - Performs web search and analysis for content creation
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from serpapi import GoogleSearch

from config import settings
from api.models import ResearchResult

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Research Agent that performs web searches and analyzes results
    to provide comprehensive research for content creation.
    """
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.serp_api_key = settings.serp_api_key
        
    async def execute(self, context: Dict[str, Any], params: Dict[str, Any]) -> ResearchResult:
        """
        Execute research based on the provided topic.
        
        Args:
            context: Execution context with task_id and previous results
            params: Research parameters including topic, depth, focus_areas
            
        Returns:
            ResearchResult with sources, findings, and summary
        """
        topic = params.get("topic", "")
        depth = params.get("depth", "standard")
        focus_areas = params.get("focus_areas", [])
        
        logger.info(f"Starting research for topic: {topic}, depth: {depth}")
        
        try:
            # Perform web search
            search_results = await self._search_web(topic, depth)
            
            # Analyze results with GPT-4
            analysis = await self._analyze_results(topic, search_results, focus_areas)
            
            # Extract key information
            result = ResearchResult(
                sources=self._format_sources(search_results),
                key_findings=analysis.get("findings", []),
                summary=analysis.get("summary", ""),
                statistics=analysis.get("statistics", []),
                trends=analysis.get("trends", [])
            )
            
            logger.info(f"Research completed: {len(result.sources)} sources, {len(result.key_findings)} findings")
            return result
            
        except Exception as e:
            logger.error(f"Research error: {str(e)}", exc_info=True)
            # Return minimal result on error
            return ResearchResult(
                sources=[],
                key_findings=[f"Research error: {str(e)}"],
                summary="Unable to complete research due to an error."
            )
    
    async def _search_web(self, topic: str, depth: str) -> List[Dict]:
        """Perform web search using SerpAPI."""
        # Determine number of results based on depth
        num_results = {
            "quick": 5,
            "standard": 10,
            "deep": 20
        }.get(depth, 10)
        
        results = []
        
        try:
            # Run search in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                self._perform_serp_search,
                topic,
                num_results
            )
            results.extend(search_results)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            # Continue with partial results
        
        return results
    
    def _perform_serp_search(self, query: str, num_results: int) -> List[Dict]:
        """Perform the actual SerpAPI search (sync)."""
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serp_api_key,
                "num": num_results,
                "hl": "en",
                "gl": "us"
            })
            
            results = search.get_dict()
            
            # Handle rate limiting
            if results.get("error") == "Google hasn't returned any results for this query.":
                logger.warning("No results found for query")
                return []
            
            return results.get("organic_results", [])
            
        except Exception as e:
            logger.error(f"SerpAPI error: {e}")
            return []
    
    async def _analyze_results(
        self,
        topic: str,
        search_results: List[Dict],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Analyze search results using GPT-4."""
        if not search_results:
            return {
                "findings": ["No search results available"],
                "summary": "Unable to find relevant information.",
                "statistics": [],
                "trends": []
            }
        
        # Prepare content for analysis
        results_text = self._prepare_results_for_analysis(search_results)
        
        # Create analysis prompt
        focus_text = f"Focus on these areas: {', '.join(focus_areas)}" if focus_areas else ""
        
        prompt = f"""
        Analyze the following search results about: {topic}
        {focus_text}
        
        Search Results:
        {results_text}
        
        Please provide:
        1. Key Findings: List 3-5 most important findings
        2. Summary: 2-3 sentence overview
        3. Statistics: Any relevant numbers or data points
        4. Trends: Current or emerging trends
        
        Format as JSON with keys: findings (list), summary (string), statistics (list), trends (list)
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a research analyst. Analyze information and extract key insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for factual analysis
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            # Ensure all expected fields exist
            return {
                "findings": analysis.get("findings", [])[:5],  # Limit to 5
                "summary": analysis.get("summary", ""),
                "statistics": analysis.get("statistics", [])[:5],
                "trends": analysis.get("trends", [])[:3]
            }
            
        except Exception as e:
            logger.error(f"GPT-4 analysis error: {e}")
            return {
                "findings": ["Analysis error occurred"],
                "summary": "Unable to analyze results.",
                "statistics": [],
                "trends": []
            }
    
    def _format_sources(self, search_results: List[Dict]) -> List[Dict]:
        """Format search results as sources."""
        sources = []
        
        for result in search_results[:10]:  # Limit to top 10
            source = {
                "title": result.get("title", "Untitled"),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "position": result.get("position", 0)
            }
            
            # Add date if available
            if "date" in result:
                source["date"] = result["date"]
            
            sources.append(source)
        
        return sources
    
    def _prepare_results_for_analysis(self, results: List[Dict]) -> str:
        """Prepare search results for GPT-4 analysis."""
        formatted_results = []
        
        for i, result in enumerate(results[:10], 1):  # Analyze top 10
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            formatted_results.append(
                f"{i}. {title}\n"
                f"   {snippet}\n"
                f"   Source: {link}\n"
            )
        
        return "\n".join(formatted_results)
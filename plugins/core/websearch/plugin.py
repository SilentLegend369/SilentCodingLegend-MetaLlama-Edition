"""
Web Search Plugin for SilentCodingLegend AI Agent
Provides comprehensive web search capabilities using multiple search providers
"""

import aiohttp
import asyncio
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urljoin
import logging

from src.plugins import BasePlugin, PluginMetadata, PluginType
from src.plugins.tool_registry import Tool, ToolParameter, ParameterType

# Use standard logging to avoid circular imports
logger = logging.getLogger(__name__)


class WebSearchPlugin(BasePlugin):
    """Web search plugin with multiple search providers"""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="WebSearch",
            version="1.0.0", 
            description="Web search tools for finding information online using multiple search providers",
            author="SilentCodingLegend",
            plugin_type=PluginType.TOOL,
            dependencies=["aiohttp", "beautifulsoup4", "urllib3"]
        )
        super().__init__(metadata)
        
    async def initialize(self):
        """Initialize the web search plugin"""
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        return True
        
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None
        except Exception as e:
            logger.warning(f"Error closing session: {e}")
    
    def __del__(self):
        """Destructor to clean up resources"""
        try:
            if hasattr(self, 'session') and self.session and not self.session.closed:
                # Can't call async method in destructor, just log
                logger.warning("Session not properly closed in destructor")
        except:
            pass

    def get_tools(self) -> List[Tool]:
        """Get available tools"""
        return [
            Tool(
                name="search_web",
                description="Search the web for information using multiple search engines",
                category="search",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="Search query",
                        required=True
                    ),
                    ToolParameter(
                        name="provider",
                        type=ParameterType.STRING,
                        description="Search provider (duckduckgo, google, bing, all)",
                        required=False,
                        default="duckduckgo"
                    ),
                    ToolParameter(
                        name="max_results",
                        type=ParameterType.INTEGER,
                        description="Maximum number of results to return (1-20)",
                        required=False,
                        default=10
                    ),
                    ToolParameter(
                        name="include_snippets",
                        type=ParameterType.BOOLEAN,
                        description="Include content snippets from results",
                        required=False,
                        default=True
                    )
                ],
                function=self.search_web,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="search_news",
                description="Search for recent news articles",
                category="search",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="News search query",
                        required=True
                    ),
                    ToolParameter(
                        name="max_results",
                        type=ParameterType.INTEGER,
                        description="Maximum number of news results (1-15)",
                        required=False,
                        default=10
                    ),
                    ToolParameter(
                        name="time_filter",
                        type=ParameterType.STRING,
                        description="Time filter (day, week, month, year)",
                        required=False,
                        default="week"
                    )
                ],
                function=self.search_news,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="search_academic",
                description="Search for academic papers and scholarly content",
                category="search",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="Academic search query",
                        required=True
                    ),
                    ToolParameter(
                        name="max_results",
                        type=ParameterType.INTEGER,
                        description="Maximum number of academic results (1-15)",
                        required=False,
                        default=8
                    )
                ],
                function=self.search_academic,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="search_images",
                description="Search for images related to a query",
                category="search",
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="Image search query",
                        required=True
                    ),
                    ToolParameter(
                        name="max_results",
                        type=ParameterType.INTEGER,
                        description="Maximum number of image results (1-20)",
                        required=False,
                        default=10
                    ),
                    ToolParameter(
                        name="safe_search",
                        type=ParameterType.BOOLEAN,
                        description="Enable safe search filtering",
                        required=False,
                        default=True
                    )
                ],
                function=self.search_images,
                plugin_name=self.metadata.name
            )
        ]
    
    async def _get_session(self):
        """Get or create HTTP session with better event loop handling"""
        try:
            if not self.session or self.session.closed:
                import random
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(
                    headers=headers,
                    connector=connector,
                    timeout=timeout
                )
            return self.session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            # Create a new session as fallback
            import random
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=timeout
            )
            return self.session

    async def search_web(self, query: str, provider: str = "duckduckgo", 
                        max_results: int = 10, include_snippets: bool = True) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            # Validate and set defaults
            if not provider or provider.strip() == "":
                provider = "duckduckgo"
            provider = provider.strip().lower()
            
            max_results = min(max_results, 20)  # Limit to 20 results
            
            if provider == "all":
                # Search multiple providers and combine results
                results = []
                providers = ["duckduckgo", "bing"]  # Start with these two
                
                for prov in providers:
                    try:
                        prov_results = await self._search_provider(query, prov, max_results // len(providers), include_snippets)
                        results.extend(prov_results)
                    except Exception as e:
                        logger.warning(f"Provider {prov} failed: {e}")
                        continue
                        
                # Remove duplicates by URL
                seen_urls = set()
                unique_results = []
                for result in results:
                    if result.get('url') not in seen_urls:
                        seen_urls.add(result.get('url'))
                        unique_results.append(result)
                        
                results = unique_results[:max_results]
            else:
                results = await self._search_provider(query, provider, max_results, include_snippets)
            
            return {
                "query": query,
                "provider": provider,
                "total_results": len(results),
                "results": results,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "query": query,
                "provider": provider,
                "error": str(e),
                "status": "error"
            }

    async def _search_provider(self, query: str, provider: str, max_results: int, include_snippets: bool) -> List[Dict[str, Any]]:
        """Search using a specific provider"""
        if provider == "duckduckgo":
            return await self._search_duckduckgo(query, max_results, include_snippets)
        elif provider == "bing":
            return await self._search_bing(query, max_results, include_snippets)
        elif provider == "google":
            return await self._search_google(query, max_results, include_snippets)
        else:
            raise ValueError(f"Unknown search provider: {provider}")

    async def _search_duckduckgo(self, query: str, max_results: int, include_snippets: bool) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        # Ensure max_results is an integer
        max_results = int(max_results) if max_results else 10
        
        session = await self._get_session()
        
        # DuckDuckGo search
        search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        
        async with session.get(search_url) as response:
            if response.status != 200:
                raise Exception(f"DuckDuckGo search failed with status {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            results = []
            result_elements = soup.find_all('div', class_='result')
            
            for element in result_elements[:max_results]:
                try:
                    title_elem = element.find('a', class_='result__a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    snippet = ""
                    if include_snippets:
                        snippet_elem = element.find('div', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "DuckDuckGo"
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to parse DuckDuckGo result: {e}")
                    continue
            
            return results

    async def _search_bing(self, query: str, max_results: int, include_snippets: bool) -> List[Dict[str, Any]]:
        """Search using Bing"""
        # Ensure max_results is an integer
        max_results = int(max_results) if max_results else 10
        
        session = await self._get_session()
        
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
        
        async with session.get(search_url) as response:
            if response.status != 200:
                raise Exception(f"Bing search failed with status {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            results = []
            result_elements = soup.find_all('li', class_='b_algo')
            
            for element in result_elements[:max_results]:
                try:
                    title_elem = element.find('h2')
                    if not title_elem:
                        continue
                    
                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue
                        
                    title = link_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    
                    snippet = ""
                    if include_snippets:
                        snippet_elem = element.find('div', class_='b_caption')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "Bing"
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to parse Bing result: {e}")
                    continue
            
            return results

    async def _search_google(self, query: str, max_results: int, include_snippets: bool) -> List[Dict[str, Any]]:
        """Search using Google (via web scraping)"""
        # Ensure max_results is an integer
        max_results = int(max_results) if max_results else 10
        
        session = await self._get_session()
        
        # Note: Google heavily rate-limits and blocks scrapers
        # In production, you'd want to use the Google Custom Search API
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}"
        
        try:
            async with session.get(search_url) as response:
                if response.status != 200:
                    raise Exception(f"Google search failed with status {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                
                # Google search results have different selectors
                # This is a basic implementation that may need updates
                result_elements = soup.find_all('div', class_='g')
                
                for element in result_elements[:max_results]:
                    try:
                        # Find title and link
                        title_elem = element.find('h3')
                        if not title_elem:
                            continue
                        
                        link_elem = element.find('a')
                        if not link_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        
                        # Clean up Google's redirect URLs
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        snippet = ""
                        if include_snippets:
                            # Look for snippet text
                            snippet_selectors = [
                                'div[data-sncf="1"]',
                                '.s',
                                '.st'
                            ]
                            
                            for selector in snippet_selectors:
                                snippet_elem = element.select_one(selector)
                                if snippet_elem:
                                    snippet = snippet_elem.get_text(strip=True)
                                    break
                        
                        if title and url and not url.startswith('#'):
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source": "Google"
                            })
                            
                    except Exception as e:
                        logger.warning(f"Failed to parse Google result: {e}")
                        continue
                
                return results
                
        except Exception as e:
            logger.warning(f"Google search failed (likely blocked): {e}")
            # Fallback to DuckDuckGo if Google fails
            logger.info("Falling back to DuckDuckGo search")
            return await self._search_duckduckgo(query, max_results, include_snippets)

    async def search_news(self, query: str, max_results: int = 10, time_filter: str = "week") -> Dict[str, Any]:
        """Search for recent news articles"""
        try:
            session = await self._get_session()
            max_results = min(max_results, 15)
            
            # Use DuckDuckGo news search
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}&iar=news"
            
            async with session.get(search_url) as response:
                if response.status != 200:
                    raise Exception(f"News search failed with status {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                news_elements = soup.find_all('div', class_='result')
                
                for element in news_elements[:max_results]:
                    try:
                        title_elem = element.find('a', class_='result__a')
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        snippet = ""
                        snippet_elem = element.find('div', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                        
                        # Try to extract date
                        date = ""
                        date_elem = element.find('span', class_='result__timestamp')
                        if date_elem:
                            date = date_elem.get_text(strip=True)
                        
                        if title and url:
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "date": date,
                                "source": "News Search"
                            })
                            
                    except Exception as e:
                        logger.warning(f"Failed to parse news result: {e}")
                        continue
                
                return {
                    "query": query,
                    "time_filter": time_filter,
                    "total_results": len(results),
                    "results": results,
                    "status": "success"
                }
                
        except RuntimeError as e:
            if "Event loop is closed" in str(e) or "cannot be called from a running event loop" in str(e):
                logger.error(f"Event loop issue in news search: {e}")
                return {
                    "query": query,
                    "error": "Event loop conflict - please try again",
                    "status": "error",
                    "suggestion": "This is a temporary issue, please retry your search"
                }
            else:
                logger.error(f"Runtime error in news search: {e}")
                return {
                    "query": query,
                    "error": str(e),
                    "status": "error"
                }
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "status": "error"
            }

    async def search_academic(self, query: str, max_results: int = 8) -> Dict[str, Any]:
        """Search for academic papers and scholarly content"""
        try:
            # This is a simplified implementation
            # In a real-world scenario, you'd integrate with APIs like:
            # - Google Scholar
            # - arXiv API
            # - PubMed API
            # - CrossRef API
            
            return {
                "query": query,
                "message": "Academic search functionality would integrate with scholarly databases",
                "suggested_apis": [
                    "Google Scholar",
                    "arXiv API",
                    "PubMed API", 
                    "CrossRef API",
                    "Semantic Scholar API"
                ],
                "status": "placeholder"
            }
            
        except Exception as e:
            logger.error(f"Academic search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "status": "error"
            }

    async def search_images(self, query: str, max_results: int = 10, safe_search: bool = True) -> Dict[str, Any]:
        """Search for images related to a query"""
        try:
            return {
                "query": query,
                "message": "Image search functionality would integrate with image search APIs",
                "suggested_apis": [
                    "Unsplash API",
                    "Pixabay API",
                    "Pexels API",
                    "Google Custom Search API"
                ],
                "safe_search": safe_search,
                "status": "placeholder"
            }
            
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "status": "error"
            }

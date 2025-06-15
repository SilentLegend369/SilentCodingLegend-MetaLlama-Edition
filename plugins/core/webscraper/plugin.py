"""
Web Scraper Plugin for SilentCodingLegend AI Agent
Provides web scraping and content extraction tools
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse

from src.plugins import BasePlugin, PluginMetadata, PluginType
from src.plugins.tool_registry import Tool, ToolParameter, ParameterType


class WebScraperPlugin(BasePlugin):
    """Web scraping and content extraction plugin"""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="WebScraper",
            version="1.0.0", 
            description="Web scraping and content extraction tools",
            author="SilentCodingLegend",
            plugin_type=PluginType.TOOL,
            dependencies=["aiohttp", "beautifulsoup4"]
        )
        super().__init__(metadata)
        
    async def initialize(self):
        """Initialize the web scraper plugin"""
        self.session = None
        return True
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    def get_tools(self) -> List[Tool]:
        """Get available tools"""
        return [
            Tool(
                name="scrape_webpage",
                description="Scrape content from a webpage",
                parameters=[
                    ToolParameter(
                        name="url",
                        type=ParameterType.STRING,
                        description="URL to scrape",
                        required=True
                    ),
                    ToolParameter(
                        name="selector",
                        type=ParameterType.STRING, 
                        description="CSS selector to extract specific content",
                        required=False
                    )
                ],
                function=self.scrape_webpage,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="extract_links",
                description="Extract all links from a webpage",
                parameters=[
                    ToolParameter(
                        name="url",
                        type=ParameterType.STRING,
                        description="URL to extract links from",
                        required=True
                    ),
                    ToolParameter(
                        name="filter_domain",
                        type=ParameterType.BOOLEAN,
                        description="Only return links from the same domain",
                        required=False
                    )
                ],
                function=self.extract_links,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="get_page_metadata",
                description="Extract metadata from a webpage (title, description, etc.)",
                parameters=[
                    ToolParameter(
                        name="url",
                        type=ParameterType.STRING,
                        description="URL to extract metadata from",
                        required=True
                    )
                ],
                function=self.get_page_metadata,
                plugin_name=self.metadata.name
            )
        ]
        
    async def scrape_webpage(self, url: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """Scrape content from a webpage"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response.reason}"
                    }
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                if selector:
                    # Extract specific content using CSS selector
                    elements = soup.select(selector)
                    content = [elem.get_text(strip=True) for elem in elements]
                else:
                    # Extract main content
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    content = soup.get_text(strip=True)
                
                return {
                    "success": True,
                    "url": url,
                    "content": content,
                    "title": soup.title.string if soup.title else "",
                    "selector": selector
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def extract_links(self, url: str, filter_domain: bool = False) -> Dict[str, Any]:
        """Extract all links from a webpage"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response.reason}"
                    }
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                links = []
                base_domain = urlparse(url).netloc
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    
                    if filter_domain:
                        link_domain = urlparse(absolute_url).netloc
                        if link_domain != base_domain:
                            continue
                    
                    links.append({
                        "url": absolute_url,
                        "text": link.get_text(strip=True),
                        "title": link.get('title', '')
                    })
                
                return {
                    "success": True,
                    "url": url,
                    "links": links,
                    "total_links": len(links)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_page_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from a webpage"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response.reason}"
                    }
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                metadata = {
                    "success": True,
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "description": "",
                    "keywords": "",
                    "author": "",
                    "og_title": "",
                    "og_description": "",
                    "og_image": ""
                }
                
                # Extract meta tags
                for meta in soup.find_all('meta'):
                    name = meta.get('name', '').lower()
                    property_attr = meta.get('property', '').lower()
                    content = meta.get('content', '')
                    
                    if name == 'description':
                        metadata['description'] = content
                    elif name == 'keywords':
                        metadata['keywords'] = content
                    elif name == 'author':
                        metadata['author'] = content
                    elif property_attr == 'og:title':
                        metadata['og_title'] = content
                    elif property_attr == 'og:description':
                        metadata['og_description'] = content
                    elif property_attr == 'og:image':
                        metadata['og_image'] = content
                
                return metadata
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Plugin entry point
def create_plugin():
    """Create and return the plugin instance"""
    return WebScraperPlugin()

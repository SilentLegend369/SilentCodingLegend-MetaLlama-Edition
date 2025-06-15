"""
Web Scraper Plugin for SilentCodingLegend AI Agent  
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from src.plugins.base_plugin import ToolPlugin, PluginMetadata, PluginType

class WebScraperPlugin(ToolPlugin):
    """Plugin providing web scraping capabilities"""
    
    async def initialize(self) -> bool:
        """Initialize the web scraper plugin"""
        
        self.register_tool(
            "fetch_webpage",
            self.fetch_webpage,
            "Fetch and parse a webpage",
            {
                "url": {"type": "string", "description": "URL to fetch", "required": True},
                "extract_text": {"type": "boolean", "description": "Extract text only", "default": True}
            }
        )
        
        self.register_tool(
            "extract_links",
            self.extract_links,
            "Extract all links from a webpage", 
            {
                "url": {"type": "string", "description": "URL to analyze", "required": True}
            }
        )
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in Llama format"""
        return [tool.to_llama_schema() for tool in self._tools.values()]
    
    async def fetch_webpage(self, url: str, extract_text: bool = True) -> str:
        """Fetch a webpage and optionally extract text"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    
                    if extract_text:
                        soup = BeautifulSoup(html, 'html.parser')
                        return soup.get_text(strip=True)
                    else:
                        return html
                        
        except Exception as e:
            raise RuntimeError(f"Failed to fetch webpage {url}: {e}")
    
    async def extract_links(self, url: str) -> List[str]:
        """Extract all links from a webpage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    links = []
                    
                    for link in soup.find_all('a', href=True):
                        links.append(link['href'])
                    
                    return links
                    
        except Exception as e:
            raise RuntimeError(f"Failed to extract links from {url}: {e}")

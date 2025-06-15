"""
Llama API client for the silentcodinglegend AI agent
"""
import asyncio
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any
import httpx
import json
from ..core.config import llama_config
from .rate_limiter import RateLimiter
from .retry_handler import RetryHandler

logger = logging.getLogger(__name__)

class LlamaAPIClient:
    """Client for interacting with the Llama API with tool calling support"""
    
    def __init__(self):
        self.config = llama_config
        self.base_url = self.config.base_url
        self.api_key = self.config.api_key
        self.rate_limiter = RateLimiter()
        self.retry_handler = RetryHandler()
        
        # Tool calling support
        self.tools_enabled = True
        self.available_tools = []
        
    def set_available_tools(self, tools: List[Dict[str, Any]]) -> None:
        """Set available tools for function calling"""
        self.available_tools = tools
        logger.info(f"Set {len(tools)} available tools for function calling")
    
    def enable_tools(self, enabled: bool = True) -> None:
        """Enable or disable tool calling"""
        self.tools_enabled = enabled
        logger.info(f"Tool calling {'enabled' if enabled else 'disabled'}")
        
    async def _make_request(
        self, 
        endpoint: str, 
        data: Dict, 
        stream: bool = False
    ) -> Dict:
        """Make an authenticated request to the Llama API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Add tools to request if available and enabled
        if self.tools_enabled and self.available_tools and "tools" not in data:
            data["tools"] = self.available_tools
            # Set tool choice to auto to let the model decide when to use tools
            data["tool_choice"] = "auto"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if stream:
                return await self._stream_request(client, url, headers, data)
            else:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
    
    async def _stream_request(
        self, 
        client: httpx.AsyncClient, 
        url: str, 
        headers: Dict, 
        data: Dict
    ) -> AsyncGenerator[str, None]:
        """Handle streaming responses from the API"""
        async with client.stream("POST", url, json=data, headers=headers) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk.strip():
                    yield chunk
    
    async def chat_completion(
        self, 
        messages: List[Dict], 
        stream: bool = False,
        **kwargs
    ) -> Dict:
        """Send a chat completion request to the Llama API"""
        await self.rate_limiter.acquire()
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": stream
        }
        
        try:
            return await self.retry_handler.execute(
                self._make_request, 
                "chat/completions", 
                data, 
                stream
            )
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def generate_text(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Generate text using the Llama model"""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(messages, stream=stream, **kwargs)
        
        if stream:
            return response  # Return the async generator for streaming
        else:
            return response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    async def code_completion(
        self, 
        code_context: str, 
        language: str = "python",
        **kwargs
    ) -> str:
        """Generate code completion suggestions"""
        system_message = f"""You are silentcodinglegend, an expert {language} developer. 
        Provide clean, efficient, and well-documented code completions."""
        
        prompt = f"Complete the following {language} code:\n\n{code_context}"
        
        return await self.generate_text(
            prompt, 
            system_message=system_message, 
            **kwargs
        )
    
    async def explain_code(self, code: str, language: str = "python") -> str:
        """Explain what a piece of code does"""
        system_message = """You are silentcodinglegend, an expert code analyst. 
        Provide clear, detailed explanations of code functionality."""
        
        prompt = f"Explain the following {language} code:\n\n{code}"
        
        return await self.generate_text(
            prompt, 
            system_message=system_message
        )
    
    async def debug_code(self, code: str, error_message: str, language: str = "python") -> str:
        """Help debug code issues"""
        system_message = """You are silentcodinglegend, an expert debugger. 
        Analyze the code and error, then provide solutions."""
        
        prompt = f"""Debug this {language} code:

Code:
{code}

Error:
{error_message}

Provide a solution with explanations."""
        
        return await self.generate_text(prompt, system_message=system_message)
    
    async def chat_with_tools(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict:
        """Chat completion with function calling support"""
        # Override tools for this specific request if provided
        original_tools = self.available_tools.copy()
        if tools:
            self.set_available_tools(tools)
        
        try:
            response = await self.chat_completion(messages, **kwargs)
            
            # Check if the response contains tool calls
            if self._has_tool_calls(response):
                return await self._handle_tool_calls(response, messages)
            
            return response
            
        finally:
            # Restore original tools
            self.set_available_tools(original_tools)
    
    def _has_tool_calls(self, response: Dict) -> bool:
        """Check if response contains tool calls"""
        try:
            message = response.get("choices", [{}])[0].get("message", {})
            return "tool_calls" in message and message["tool_calls"]
        except (IndexError, KeyError):
            return False
    
    async def _handle_tool_calls(self, response: Dict, original_messages: List[Dict]) -> Dict:
        """Handle tool calls in the response"""
        try:
            message = response["choices"][0]["message"]
            tool_calls = message.get("tool_calls", [])
            
            # Add the assistant's message with tool calls to conversation
            messages = original_messages + [message]
            
            # Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                
                try:
                    # Execute tool (this would be handled by plugin manager)
                    tool_result = await self._execute_tool(function_name, function_args)
                    
                    # Add tool response to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(tool_result)
                    })
                    
                except Exception as e:
                    # Add error response
                    messages.append({
                        "role": "tool", 
                        "tool_call_id": tool_call["id"],
                        "content": f"Error executing tool: {str(e)}"
                    })
            
            # Get final response with tool results
            return await self.chat_completion(messages)
            
        except Exception as e:
            logger.error(f"Error handling tool calls: {e}")
            return response
    
    async def _execute_tool(self, function_name: str, function_args: Dict) -> Any:
        """Execute a tool function - to be overridden by plugin manager integration"""
        # This is a placeholder - the actual implementation will be provided
        # by the plugin manager when it's integrated
        logger.warning(f"Tool execution not implemented: {function_name}")
        return {"error": "Tool execution not available"}
    
    def set_tool_executor(self, executor: callable) -> None:
        """Set the tool execution function (called by plugin manager)"""
        self._execute_tool = executor
        logger.info("Tool executor set for function calling")
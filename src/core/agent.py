"""
SilentCodingLegend AI Agent - Main agent class with Chain-of-Thought reasoning
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional, AsyncGenerator, Tuple, Union, Any
from datetime import datetime
from ..api.llama_client import LlamaAPIClient
from ..core.config import agent_config
from ..core.memory import ConversationMemory
from ..core.enhanced_memory import EnhancedMemoryManager  # New import
from ..core.chain_of_thought import LoopOfThoughtAgent, ChainOfThoughtReasoner, ReasoningType, ReasoningChain
from ..plugins.plugin_manager import PluginManager, plugin_manager
from ..plugins.tool_registry import tool_registry
from ..utils.logging import get_logger

logger = get_logger(__name__)

class SilentCodingLegendAgent:
    """Main AI agent class for SilentCodingLegend with Chain-of-Thought reasoning and plugin support"""
    
    def __init__(self):
        self.name = agent_config.name
        self.description = agent_config.description
        self.client = LlamaAPIClient()
        self.memory = ConversationMemory()
        
        # Initialize Enhanced Memory Management
        self.enhanced_memory: Optional[EnhancedMemoryManager] = None
        # Temporarily disabled to prevent SentenceTransformer loading issues
        # TODO: Re-enable with lazy loading or configuration option
        self.memory_features_enabled = False
        
        # Initialize Chain-of-Thought capabilities
        self.cot_agent = LoopOfThoughtAgent(self)
        self.reasoning_enabled = True
        
        # Initialize Plugin System
        self.plugin_manager = plugin_manager
        self.tool_registry = tool_registry
        self.plugins_initialized = False
        
        # Set up tool execution for the client
        self.client.set_tool_executor(self._execute_plugin_tool)
        
        self.capabilities = [
            "Code Generation",
            "Code Review", 
            "Bug Fixing",
            "Algorithm Design",
            "Documentation",
            "Technical Consulting",
            "Architecture Planning",
            "Chain-of-Thought Reasoning",  # New capability
            "Problem Decomposition",       # New capability
            "ReAct Reasoning",             # New capability
            "Plugin System",               # New capability
            "Tool Calling",                # New capability
            "Extensibility",               # New capability
            "Knowledge Graph Management",  # New capability
            "Semantic Search",             # New capability
            "Long-term Memory",            # New capability
            "RAG (Retrieval Augmented Generation)"  # New capability
        ]
        logger.info(f"Initialized {self.name} agent with Chain-of-Thought reasoning and plugin support")
    
    async def initialize_enhanced_memory(self) -> bool:
        """Initialize the enhanced memory management system"""
        try:
            if self.memory_features_enabled:
                self.enhanced_memory = EnhancedMemoryManager()
                success = await self.enhanced_memory.initialize()
                
                if success:
                    logger.info("Enhanced memory management initialized successfully")
                    return True
                else:
                    logger.error("Failed to initialize enhanced memory management")
                    return False
            else:
                logger.info("Enhanced memory features disabled")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing enhanced memory: {e}")
            return False
    
    async def initialize_memory_system(self) -> bool:
        """Initialize the enhanced memory and knowledge management system"""
        try:
            if self.memory_features_enabled:
                self.enhanced_memory = EnhancedMemoryManager()
                success = await self.enhanced_memory.initialize()
                
                if success:
                    logger.info("Enhanced memory system initialized successfully")
                    return True
                else:
                    logger.error("Failed to initialize enhanced memory system")
                    self.enhanced_memory = None
                    return False
            else:
                logger.info("Memory features disabled")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing memory system: {e}")
            self.enhanced_memory = None
            return False
    
    def initialize_plugins_sync(self) -> bool:
        """Synchronous wrapper for plugin initialization"""
        try:
            import asyncio
            return asyncio.run(self.initialize_plugins())
        except Exception as e:
            logger.error(f"Error in sync plugin initialization wrapper: {e}")
            return False
    
    async def initialize_plugins(self) -> bool:
        """Initialize the plugin system"""
        try:
            await self.plugin_manager.initialize(agent=self)
            
            # Initialize enhanced memory management only if enabled
            await self.initialize_enhanced_memory()
            
            # Update available tools in the client
            await self._update_available_tools()
            
            # Auto-start backup system if available
            await self._auto_start_backup_system()
            
            # Skip auto-start knowledge management to prevent SentenceTransformer hanging
            # Auto-start knowledge management if available
            # await self._auto_start_knowledge_management()
            logger.info("Skipping knowledge management auto-start to prevent SentenceTransformer loading hang")
            
            self.plugins_initialized = True
            logger.info("Plugin system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}")
            return False
    
    async def _auto_start_backup_system(self) -> None:
        """Automatically start the backup system if BackupManager plugin is available"""
        try:
            # Check if BackupManager plugin is loaded
            backup_plugin = None
            for plugin in self.plugin_manager._loaded_plugins.values():
                if plugin.metadata.name == "BackupManager":
                    backup_plugin = plugin
                    break
            
            if backup_plugin and hasattr(backup_plugin, 'backup_manager'):
                # Check if auto-backup is enabled in config
                config_result = await backup_plugin.get_backup_config()
                if config_result.get("success") and config_result.get("config", {}).get("enabled", False):
                    # Start automatic backup
                    start_result = await backup_plugin.start_auto_backup()
                    if start_result.get("success"):
                        logger.info("Automatic backup system started successfully")
                    else:
                        logger.warning(f"Failed to start automatic backup: {start_result.get('error')}")
                else:
                    logger.info("Automatic backup is disabled in configuration")
            else:
                logger.info("BackupManager plugin not available for auto-start")
                
        except Exception as e:
            logger.error(f"Error starting automatic backup system: {e}")
    
    async def _auto_start_knowledge_management(self) -> None:
        """Automatically start the knowledge management system if KnowledgeManager plugin is available"""
        try:
            # Check if KnowledgeManager plugin is loaded
            knowledge_plugin = None
            for plugin in self.plugin_manager._loaded_plugins.values():
                if plugin.metadata.name == "KnowledgeManager":
                    knowledge_plugin = plugin
                    break
            
            if knowledge_plugin:
                logger.info("KnowledgeManager plugin found and initialized")
                # The plugin initialization handles the memory manager setup
            else:
                logger.info("KnowledgeManager plugin not available")
                
        except Exception as e:
            logger.error(f"Error starting knowledge management system: {e}")
    
    async def _update_available_tools(self) -> None:
        """Update available tools in the Llama client"""
        tools_schema = self.tool_registry.get_llama_tools_schema()
        self.client.set_available_tools(tools_schema)
        logger.info(f"Updated {len(tools_schema)} available tools in client")
    
    async def _execute_plugin_tool(self, function_name: str, function_args: Dict) -> Dict:
        """Execute a plugin tool"""
        try:
            result = await self.tool_registry.execute_tool(function_name, function_args)
            return {"result": result, "success": True}
        except Exception as e:
            logger.error(f"Tool execution failed for {function_name}: {e}")
            return {"error": str(e), "success": False}
    
    def enable_reasoning(self, enabled: bool = True):
        """Enable or disable Chain-of-Thought reasoning"""
        self.reasoning_enabled = enabled
        logger.info(f"Chain-of-Thought reasoning {'enabled' if enabled else 'disabled'}")
    
    def set_reasoning_type(self, reasoning_type: ReasoningType):
        """Set the default reasoning type"""
        self.default_reasoning_type = reasoning_type
        logger.info(f"Default reasoning type set to: {reasoning_type.value}")
    
    async def chat_with_reasoning(
        self, 
        message: Union[str, Dict], 
        session_id: Optional[str] = None,
        use_cot: Optional[bool] = None,
        reasoning_type: Optional[ReasoningType] = None,
        stream: bool = False
    ) -> Tuple[str, Optional[ReasoningChain]]:
        """
        Enhanced chat interface with Chain-of-Thought reasoning
        
        Args:
            message: User input (string or dict for multimodal)
            session_id: Optional session identifier
            use_cot: Force CoT usage (None for auto-detection)
            reasoning_type: Specific reasoning type to use
            stream: Whether to stream the response
            
        Returns:
            Tuple of (response, reasoning_chain)
        """
        if self.reasoning_enabled and isinstance(message, str):
            return await self.cot_agent.enhanced_chat(
                message, session_id, use_cot, reasoning_type
            )
        else:
            # Fallback to regular chat for multimodal or when reasoning is disabled
            response = await self.chat(message, session_id, stream)
            return response, None
        
    async def chat(
        self, 
        message, 
        session_id: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Main chat interface for the agent with enhanced memory support"""
        try:
            # Get conversation history
            conversation_history = self.memory.get_conversation(session_id)
            
            # Get enhanced context if available
            enhanced_context = None
            if self.enhanced_memory and isinstance(message, str):
                try:
                    context_data = await self.enhanced_memory.get_relevant_context(
                        query=message,
                        session_id=session_id,
                        max_results=3
                    )
                    if context_data and (context_data["semantic_matches"] or context_data["knowledge_entities"]):
                        enhanced_context = context_data
                        logger.debug(f"Enhanced context found: {context_data['summary']}")
                except Exception as e:
                    logger.warning(f"Error getting enhanced context: {e}")
            
            # Prepare messages for the API
            if isinstance(message, dict):
                # Multimodal message (e.g., vision)
                messages = self._prepare_multimodal_messages(message, conversation_history, enhanced_context)
            else:
                # Text-only message
                messages = self._prepare_messages(message, conversation_history, enhanced_context)
            
            # Generate response
            if stream:
                return await self._stream_response(messages, session_id, message)
            else:
                response = await self.client.chat_completion(messages)
                logger.debug(f"Raw API response: {response}")
                
                # Parse Meta Llama API response format
                response_text = ""
                try:
                    if "completion_message" in response:
                        # Meta Llama API format
                        completion_msg = response["completion_message"]
                        
                        # Check if this is a tool call response
                        if "tool_calls" in completion_msg and completion_msg["tool_calls"]:
                            # Handle tool calls
                            tool_results = []
                            for tool_call in completion_msg["tool_calls"]:
                                function_name = tool_call["function"]["name"]
                                function_args = json.loads(tool_call["function"]["arguments"])
                                
                                logger.debug(f"🔧 Executing tool: {function_name} with args: {function_args}")
                                
                                # Execute the tool
                                try:
                                    result = await self._execute_plugin_tool(function_name, function_args)
                                    tool_results.append(f"**{function_name} results:**\n{self._format_tool_result(result)}")
                                except Exception as tool_error:
                                    tool_results.append(f"**{function_name} error:** {str(tool_error)}")
                            
                            response_text = "\n\n".join(tool_results)
                        
                        # Check for regular content
                        elif "content" in completion_msg:
                            if isinstance(completion_msg["content"], dict) and "text" in completion_msg["content"]:
                                response_text = completion_msg["content"]["text"]
                            elif isinstance(completion_msg["content"], str):
                                response_text = completion_msg["content"]
                            else:
                                response_text = str(completion_msg["content"])
                        else:
                            # No content or tool calls found
                            response_text = "No response content available."
                            
                    elif "choices" in response and len(response["choices"]) > 0:
                        # OpenAI format (fallback)
                        choice = response["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            response_text = choice["message"]["content"]
                        elif "text" in choice:
                            response_text = choice["text"]
                        else:
                            response_text = str(choice)
                    elif "content" in response:
                        # Direct content field
                        response_text = response["content"]
                    elif "text" in response:
                        # Direct text field
                        response_text = response["text"]
                    elif isinstance(response, str):
                        # Response is already a string
                        response_text = response
                    else:
                        # Unknown format, try to extract meaningful content
                        logger.warning(f"Unknown response format: {response}")
                        if isinstance(response, dict):
                            # Try to find any text-like content
                            for key in ["message", "result", "output", "response"]:
                                if key in response:
                                    response_text = str(response[key])
                                    break
                            if not response_text:
                                response_text = str(response)
                        else:
                            response_text = str(response)
                except KeyError as e:
                    logger.error(f"Missing expected key in response: {e}")
                    response_text = f"Error parsing response: missing key '{e}'"
                except Exception as e:
                    logger.error(f"Error parsing response: {e}")
                    response_text = f"Error parsing response: {str(e)}"
                
                logger.debug(f"Extracted response text: {response_text}")
                
                # Store in memory (both traditional and enhanced)
                if isinstance(message, dict):
                    # For multimodal messages, store a simplified text representation
                    user_message_text = self._extract_text_from_multimodal(message)
                    self.memory.add_message(session_id, "user", user_message_text)
                else:
                    self.memory.add_message(session_id, "user", message)
                    # Store in enhanced memory if available
                    if self.enhanced_memory:
                        try:
                            await self.enhanced_memory.add_conversation_turn(
                                session_id=session_id,
                                user_message=message,
                                assistant_response=response_text
                            )
                        except Exception as e:
                            logger.warning(f"Error storing in enhanced memory: {e}")
                
                self.memory.add_message(session_id, "assistant", response_text)
                
                return response_text
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def _stream_response(
        self, 
        messages: List[Dict], 
        session_id: str, 
        user_message: str
    ) -> AsyncGenerator[str, None]:
        """Handle streaming responses"""
        try:
            response_chunks = []
            async for chunk in await self.client.chat_completion(messages, stream=True):
                response_chunks.append(chunk)
                yield chunk
            
            # Store complete response in memory
            complete_response = "".join(response_chunks)
            self.memory.add_message(session_id, "user", user_message)
            self.memory.add_message(session_id, "assistant", complete_response)
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"Error: {str(e)}"
    
    def _prepare_messages(
        self, 
        current_message: str, 
        conversation_history: List[Dict],
        enhanced_context: Optional[Dict] = None
    ) -> List[Dict]:
        """Prepare messages for the API call with optional enhanced context"""
        
        # Build system message with enhanced context if available
        system_content = f"""You are {self.name}, {self.description}.

Your capabilities include:
{chr(10).join(f"- {cap}" for cap in self.capabilities)}

You should:
- Provide clear, helpful, and accurate responses
- Write clean, efficient, and well-documented code
- Explain complex concepts in an understandable way
- Be proactive in suggesting improvements
- Maintain a professional but friendly tone"""

        # Add enhanced context if available
        if enhanced_context:
            context_info = []
            
            if enhanced_context.get("semantic_matches"):
                context_info.append(f"RELEVANT CONTEXT from similar conversations:")
                for match in enhanced_context["semantic_matches"][:3]:  # Top 3 matches
                    context_info.append(f"- {match['content'][:200]}..." if len(match['content']) > 200 else f"- {match['content']}")
            
            if enhanced_context.get("knowledge_entities"):
                entity_names = [entity["name"] for entity in enhanced_context["knowledge_entities"][:5]]
                context_info.append(f"RELATED CONCEPTS: {', '.join(entity_names)}")
            
            if context_info:
                system_content += f"\n\nRELEVANT KNOWLEDGE:\n{chr(10).join(context_info)}"
        
        system_content += f"\n\nCurrent timestamp: {datetime.now().isoformat()}"
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages = [system_message]
        
        # Add conversation history (keep last 10 exchanges to manage context length)
        recent_history = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
        messages.extend(recent_history)
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def _prepare_multimodal_messages(
        self, 
        multimodal_message: Dict, 
        conversation_history: List[Dict],
        enhanced_context: Optional[Dict] = None
    ) -> List[Dict]:
        """Prepare multimodal messages for the API call with optional enhanced context"""
        
        system_content = f"""You are {self.name}, {self.description}.

Your capabilities include:
{chr(10).join(f"- {cap}" for cap in self.capabilities)}

You are also equipped with vision capabilities and can analyze images. When analyzing images:
- Provide detailed, accurate descriptions
- Identify objects, text, patterns, and visual elements
- Analyze technical aspects like composition, quality, and structure
- Provide insights relevant to the user's request

You should:
- Provide clear, helpful, and accurate responses
- Write clean, efficient, and well-documented code
- Explain complex concepts in an understandable way
- Be proactive in suggesting improvements
- Maintain a professional but friendly tone"""

        # Add enhanced context if available
        if enhanced_context:
            context_info = []
            
            if enhanced_context.get("semantic_matches"):
                context_info.append(f"RELEVANT CONTEXT from similar conversations:")
                for match in enhanced_context["semantic_matches"][:3]:
                    context_info.append(f"- {match['content'][:200]}..." if len(match['content']) > 200 else f"- {match['content']}")
            
            if enhanced_context.get("knowledge_entities"):
                entity_names = [entity["name"] for entity in enhanced_context["knowledge_entities"][:5]]
                context_info.append(f"RELATED CONCEPTS: {', '.join(entity_names)}")
            
            if context_info:
                system_content += f"\n\nRELEVANT KNOWLEDGE:\n{chr(10).join(context_info)}"

        system_content += f"\n\nCurrent timestamp: {datetime.now().isoformat()}"
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages = [system_message]
        
        # Add conversation history (keep last 10 exchanges to manage context length)
        recent_history = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
        messages.extend(recent_history)
        
        # Add multimodal message
        messages.append(multimodal_message)
        
        return messages
    
    async def _enhanced_chat_with_context(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Enhanced chat with RAG context retrieval"""
        context_info = {}
        
        try:
            if self.enhanced_memory:
                # Get relevant context from all sources
                context = await self.enhanced_memory.get_relevant_context(
                    query=message,
                    session_id=session_id,
                    max_results=5
                )
                
                context_info = context
                
                # Enhance the message with context if available
                if context.get("semantic_matches") or context.get("knowledge_entities"):
                    enhanced_message = self._build_enhanced_prompt(message, context)
                    return enhanced_message, context_info
            
            return message, context_info
            
        except Exception as e:
            logger.error(f"Error in enhanced chat context: {e}")
            return message, {"error": str(e)}
    
    def _build_enhanced_prompt(self, original_message: str, context: Dict[str, Any]) -> str:
        """Build an enhanced prompt with retrieved context"""
        prompt_parts = [original_message]
        
        # Add semantic matches if available
        if context.get("semantic_matches"):
            prompt_parts.append("\n\n--- Relevant Previous Conversations ---")
            for match in context["semantic_matches"][:3]:  # Top 3 matches
                prompt_parts.append(f"Previous context (relevance: {match['score']:.2f}): {match['content'][:200]}...")
        
        # Add knowledge entities if available
        if context.get("knowledge_entities"):
            prompt_parts.append("\n\n--- Related Knowledge ---")
            for entity in context["knowledge_entities"][:3]:  # Top 3 entities
                prompt_parts.append(f"{entity['type']}: {entity['name']} - {entity.get('properties', {})}")
        
        # Add knowledge relationships if available
        if context.get("knowledge_relationships"):
            prompt_parts.append("\n\n--- Knowledge Relationships ---")
            for rel in context["knowledge_relationships"][:3]:  # Top 3 relationships
                prompt_parts.append(f"{rel['source']} {rel['type']} {rel['target']}")
        
        return "\n".join(prompt_parts)
    
    async def generate_code(
        self, 
        description: str, 
        language: str = "python",
        include_tests: bool = False,
        session_id: Optional[str] = None
    ) -> str:
        """Generate code based on description"""
        prompt = f"""Generate {language} code for: {description}

Requirements:
- Clean, readable code with proper formatting
- Include comments explaining key functionality
- Follow best practices for {language}
"""
        
        if include_tests:
            prompt += "- Include unit tests\n"
        
        return await self.chat(prompt, session_id)
    
    async def review_code(
        self, 
        code: str, 
        language: str = "python",
        session_id: Optional[str] = None
    ) -> str:
        """Review code and provide suggestions"""
        prompt = f"""Please review this {language} code and provide feedback:

```{language}
{code}
```

Focus on:
- Code quality and readability
- Performance optimizations
- Security considerations
- Best practices
- Potential bugs or issues
"""
        
        return await self.chat(prompt, session_id)
    
    async def debug_code(
        self, 
        code: str, 
        error_message: str, 
        language: str = "python",
        session_id: Optional[str] = None
    ) -> str:
        """Help debug code issues"""
        prompt = f"""Help me debug this {language} code:

Code:
```{language}
{code}
```

Error Message:
```
{error_message}
```

Please:
1. Identify the root cause of the error
2. Provide a fixed version of the code
3. Explain what was wrong and why the fix works
"""
        
        return await self.chat(prompt, session_id)
    
    async def explain_code(
        self, 
        code: str, 
        language: str = "python",
        session_id: Optional[str] = None
    ) -> str:
        """Explain what code does"""
        prompt = f"""Please explain what this {language} code does:

```{language}
{code}
```

Provide:
- High-level overview of functionality
- Step-by-step breakdown
- Key concepts used
- Potential use cases
"""
        
        return await self.chat(prompt, session_id)
    
    def get_agent_info(self) -> Dict:
        """Get information about the agent"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "status": "active"
        }
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the conversation"""
        history = self.memory.get_conversation(session_id)
        if not history:
            return "No conversation history found."
        
        # Create a summary prompt
        history_text = "\n".join([
            f"{msg['role']}: {msg['content'][:100]}..." 
            for msg in history[-10:]  # Last 10 messages
        ])
        
        prompt = f"""Summarize this conversation:

{history_text}

Provide a brief summary of:
- Main topics discussed
- Key solutions provided
- Current context/state
"""
        
        return await self.chat(prompt, session_id="summary")
    
    def chat_sync(self, message, session_id: Optional[str] = None) -> str:
        """Synchronous wrapper for the async chat method"""
        try:
            # Try to run in a new event loop
            return asyncio.run(self.chat(message, session_id))
        except RuntimeError as e:
            # If there's already a running event loop
            if "cannot be called from a running event loop" in str(e):
                # Use thread-based approach for Streamlit compatibility
                import concurrent.futures
                
                def run_in_thread():
                    # Create a new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(self.chat(message, session_id))
                    finally:
                        loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                # Other runtime error, try event loop approach
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.chat(message, session_id))
        except Exception as e:
            logger.error(f"Error in sync chat wrapper: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _extract_text_from_multimodal(self, multimodal_message: Dict) -> str:
        """Extract text content from a multimodal message for memory storage"""
        if "content" in multimodal_message and isinstance(multimodal_message["content"], list):
            text_parts = []
            for item in multimodal_message["content"]:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif item.get("type") == "image_url":
                    text_parts.append("[Image uploaded]")
            return " ".join(text_parts)
        elif "content" in multimodal_message and isinstance(multimodal_message["content"], str):
            return multimodal_message["content"]
        else:
            return "[Multimodal content]"
    
    def _format_tool_result(self, result: Any) -> str:
        """Format tool execution results for display"""
        try:
            if isinstance(result, dict):
                if "error" in result:
                    return f"❌ Error: {result['error']}"
                elif "results" in result:
                    # Handle search results
                    results_list = result["results"]
                    if not results_list:
                        return "No results found."
                    
                    formatted_results = []
                    for i, item in enumerate(results_list[:5], 1):  # Show top 5 results
                        if isinstance(item, dict):
                            title = item.get("title", "Untitled")
                            url = item.get("url", "")
                            snippet = item.get("snippet", "")
                            date = item.get("date", "")
                            
                            result_text = f"{i}. **{title}**"
                            if date:
                                result_text += f" ({date})"
                            if snippet:
                                result_text += f"\n   {snippet}"
                            if url:
                                result_text += f"\n   🔗 {url}"
                            formatted_results.append(result_text)
                    
                    return "\n\n".join(formatted_results)
                else:
                    # Generic dict formatting
                    return json.dumps(result, indent=2, ensure_ascii=False)
            else:
                return str(result)
        except Exception as e:
            return f"Error formatting result: {e}"
    
    # Chain-of-Thought Reasoning Methods
    
    def chat_sync_with_reasoning(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        use_cot: Optional[bool] = None,
        reasoning_type: Optional[ReasoningType] = None
    ) -> Tuple[str, Optional[ReasoningChain]]:
        """
        Synchronous wrapper for chat with reasoning
        
        Args:
            message: User input
            session_id: Optional session identifier
            use_cot: Force CoT usage (None for auto-detection)
            reasoning_type: Specific reasoning type to use
            
        Returns:
            Tuple of (response, reasoning_chain)
        """
        try:
            return asyncio.run(self.chat_with_reasoning(message, session_id, use_cot, reasoning_type))
        except RuntimeError as e:
            # If there's already a running event loop
            if "cannot be called from a running event loop" in str(e):
                # Use thread-based approach for Streamlit compatibility
                import concurrent.futures
                
                def run_in_thread():
                    # Create a new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(
                            self.chat_with_reasoning(message, session_id, use_cot, reasoning_type)
                        )
                    finally:
                        loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                # Other runtime error, try event loop approach
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(
                    self.chat_with_reasoning(message, session_id, use_cot, reasoning_type)
                )
        except Exception as e:
            logger.error(f"Error in sync reasoning chat: {e}")
            return f"I apologize, but I encountered an error: {str(e)}", None
    
    def get_reasoning_history(self) -> List[ReasoningChain]:
        """Get the history of reasoning chains"""
        return self.cot_agent.get_reasoning_history()
    
    def export_reasoning_analysis(self) -> Dict:
        """Export reasoning analysis for review"""
        return self.cot_agent.export_reasoning_analysis()
    
    def should_use_reasoning(self, message: str) -> bool:
        """Check if a message would benefit from Chain-of-Thought reasoning"""
        return self.cot_agent.reasoner.should_use_cot_reasoning(message)
    
    def get_reasoning_recommendation(self, message: str) -> ReasoningType:
        """Get recommended reasoning type for a message"""
        return self.cot_agent.reasoner.select_reasoning_type(message)
    
    def generate_reasoning_prompt(self, message: str, reasoning_type: Optional[ReasoningType] = None) -> str:
        """Generate a Chain-of-Thought reasoning prompt"""
        return self.cot_agent.reasoner.generate_reasoning_prompt(message, reasoning_type)
    
    async def initialize_knowledge_management_lazy(self) -> bool:
        """Lazily initialize knowledge management when needed"""
        try:
            if not hasattr(self, '_knowledge_management_initialized'):
                await self._auto_start_knowledge_management()
                self._knowledge_management_initialized = True
                logger.info("Knowledge management initialized lazily")
            return True
        except Exception as e:
            logger.error(f"Error in lazy knowledge management initialization: {e}")
            return False
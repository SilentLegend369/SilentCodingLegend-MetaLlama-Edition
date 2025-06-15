"""
Core module for agent, configuration, and memory management
"""
from .agent import SilentCodingLegendAgent
from .config import llama_config, agent_config, app_config
from .memory import ConversationMemory

__all__ = ['SilentCodingLegendAgent', 'llama_config', 'agent_config', 'app_config', 'ConversationMemory']
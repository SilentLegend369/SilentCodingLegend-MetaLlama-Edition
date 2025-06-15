"""
Configuration module for the silentcodinglegend AI agent
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LlamaAPIConfig(BaseSettings):
    """Configuration for Llama API"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields
    )
    
    api_key: str = Field(..., alias="LLAMA_API_KEY")
    base_url: str = Field(default="https://api.llama.com/v1", alias="LLAMA_API_BASE_URL")
    model: str = Field(default="Llama-3.3-70B-Instruct", alias="LLAMA_MODEL")
    max_tokens: int = Field(default=2048, alias="MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")

class AgentConfig(BaseSettings):
    """Configuration for the AI agent"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields
    )
    
    name: str = Field(default="silentcodinglegend", alias="AGENT_NAME")
    description: str = Field(
        default="A powerful AI coding assistant specialized in software development and problem solving",
        alias="AGENT_DESCRIPTION"
    )

class AppConfig(BaseSettings):
    """Application configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields
    )
    
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

# Global configuration instances
llama_config = LlamaAPIConfig()
agent_config = AgentConfig()
app_config = AppConfig()
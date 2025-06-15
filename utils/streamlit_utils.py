"""
Utility functions for the Streamlit application
"""
import streamlit as st
import os
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from src.core.agent import SilentCodingLegendAgent
import config

logger = logging.getLogger(__name__)

def load_css() -> bool:
    """
    Loads CSS file into the Streamlit app safely using configuration.
    
    Returns:
        bool: True if CSS was loaded successfully, False otherwise
    """
    primary_path = config.PATHS_CONFIG["css_file_path"]
    fallback_path = config.PATHS_CONFIG["backup_css_file_path"]
    
    return load_css_from_file(primary_path, fallback_path)

def load_css_from_file(file_path: str, fallback_path: Optional[str] = None) -> bool:
    """
    Loads a CSS file into the Streamlit app safely.
    
    Args:
        file_path: Primary path to the CSS file
        fallback_path: Optional fallback path if primary fails
        
    Returns:
        bool: True if CSS was loaded successfully, False otherwise
    """
    def _load_css_file(path: str) -> bool:
        """Helper function to load a single CSS file."""
        full_path = Path(path)
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
                    logger.info(f"Successfully loaded CSS from: {full_path}")
                    return True
            except Exception as e:
                logger.error(f"Failed to load CSS from {full_path}: {e}")
                return False
        else:
            logger.warning(f"CSS file not found at path: {full_path}")
            return False
    
    # Try primary path first
    if _load_css_file(file_path):
        return True
    
    # Try fallback path if provided
    if fallback_path and _load_css_file(fallback_path):
        logger.info(f"Used fallback CSS file: {fallback_path}")
        return True
    
    # If both fail, log error but don't crash the app
    logger.error(f"Failed to load CSS from both primary ({file_path}) and fallback ({fallback_path}) paths")
    return False

@st.cache_resource(ttl=config.PERFORMANCE_CONFIG["cache_ttl_seconds"])
def get_cached_agent() -> SilentCodingLegendAgent:
    """
    Initializes and caches the agent and its plugins.
    This function runs only once and caches the result.
    
    Returns:
        SilentCodingLegendAgent: The initialized agent instance
    """
    logger.info("Creating and caching a new agent instance...")
    agent = SilentCodingLegendAgent()
    
    try:
        # Use synchronous initialization to avoid event loop issues
        success = agent.initialize_plugins_sync()
        if success:
            logger.info("Plugin system initialized successfully during caching")
        else:
            logger.warning("Plugin system initialization completed with warnings during caching")
    except Exception as e:
        logger.error(f"Failed to initialize plugins during caching: {e}")
    
    return agent

def generate_error_id() -> str:
    """
    Generates a unique error ID for tracking user-reported issues.
    
    Returns:
        str: Unique error identifier
    """
    timestamp = int(time.time())
    return f"{config.ERROR_CONFIG['error_id_prefix']}-{timestamp}"

def safe_get_model_info(model_name: str) -> str:
    """
    Safely retrieves model information with fallback.
    
    Args:
        model_name: Name of the model
        
    Returns:
        str: Model information or fallback message
    """
    return config.MODEL_CONFIG["model_capabilities"].get(model_name, "ℹ️ Model information not available")

def validate_session_state() -> bool:
    """
    Validates that required session state variables are present.
    This function is flexible and checks for either main app keys or page-specific keys.
    
    Returns:
        bool: True if session state is valid, False otherwise
    """
    # Main app keys
    main_keys = ['agent', 'session_id', 'messages']
    # Coding page keys
    coding_keys = ['coding_agent', 'coding_session_id', 'coding_history']
    
    # Check if we have main app keys OR coding page keys
    has_main_keys = all(key in st.session_state for key in main_keys)
    has_coding_keys = all(key in st.session_state for key in coding_keys)
    
    if not has_main_keys and not has_coding_keys:
        # Only log missing keys if neither set is complete
        logger.info("Session state validation: Neither main app keys nor coding page keys are fully initialized yet")
        return False
    
    return True

def clear_cache_safely() -> None:
    """
    Safely clears Streamlit caches with error handling.
    """
    try:
        st.cache_resource.clear()
        st.cache_data.clear()
        logger.info("Successfully cleared Streamlit caches")
    except Exception as e:
        logger.error(f"Failed to clear caches: {e}")

def format_model_display_name(model_key: str) -> str:
    """
    Formats model name for display in UI components.
    
    Args:
        model_key: The model key from config
        
    Returns:
        str: Formatted display name
    """
    return config.MODEL_CONFIG["available_models"].get(model_key, model_key)

def is_multimodal_model(model_name: str) -> bool:
    """
    Checks if a model supports multimodal input (images + text).
    
    Args:
        model_name: Name of the model
        
    Returns:
        bool: True if model supports images, False otherwise
    """
    multimodal_keywords = ['vision', 'scout', 'multimodal']
    return any(keyword in model_name.lower() for keyword in multimodal_keywords)

def validate_user_input(input_text: str) -> Tuple[bool, str]:
    """
    Validates user input for security and length constraints.
    
    Args:
        input_text: The user's input text
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not input_text.strip():
        return False, "Input cannot be empty."
    
    max_length = config.SECURITY_CONFIG["max_input_length"]
    if len(input_text) > max_length:
        return False, f"Input too long. Maximum {max_length} characters allowed."
    
    # Additional security checks can be added here
    if config.SECURITY_CONFIG["sanitize_user_input"]:
        # Basic sanitization check - can be expanded
        dangerous_patterns = ['<script', 'javascript:', 'onclick=']
        for pattern in dangerous_patterns:
            if pattern.lower() in input_text.lower():
                return False, "Input contains potentially unsafe content."
    
    return True, ""

def get_session_metrics() -> dict:
    """
    Retrieves session metrics for display.
    
    Returns:
        dict: Session metrics including message counts
    """
    if not hasattr(st.session_state, 'messages'):
        return {"total_messages": 0, "user_messages": 0, "assistant_messages": 0}
    
    messages = st.session_state.messages
    total_messages = len(messages)
    user_messages = len([m for m in messages if m["role"] == "user"])
    assistant_messages = len([m for m in messages if m["role"] == "assistant"])
    
    return {
        "total_messages": total_messages,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages
    }

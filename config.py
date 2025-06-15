"""
Configuration file for SilentCodingLegend AI Agent
Contains all static configurations for models, prompts, and UI settings
"""

# Model Configuration
MODEL_CONFIG = {
    "available_models": {
        "Llama-3.3-70B-Instruct": "Llama 3.3 70B (Recommended - Text only)",
        "Llama-3.3-8B-Instruct": "Llama 3.3 8B (Fast - Text only)", 
        "Llama-4-Scout-17B-16E-Instruct-FP8": "Llama 4 Scout (Multimodal - Text + Images)",
        "Llama-4-Maverick-17B-128E-Instruct-FP8": "Llama 4 Maverick (Advanced - Text only)",
        "Llama-3.2-90B-Vision-Instruct": "Llama 3.2 90B Vision (Multimodal - Text + Images)",
        "Llama-3.2-11B-Vision-Instruct": "Llama 3.2 11B Vision (Compact Multimodal)",
        "Llama-3.1-405B-Instruct": "Llama 3.1 405B (Flagship - Text only)",
        "Llama-3.1-70B-Instruct": "Llama 3.1 70B (Balanced - Text only)",
        "Llama-3.1-8B-Instruct": "Llama 3.1 8B (Fast - Text only)"
    },
    "model_capabilities": {
        "Llama-3.3-70B-Instruct": "🎯 Best for complex coding tasks",
        "Llama-3.3-8B-Instruct": "⚡ Fast responses for simple queries",
        "Llama-4-Scout-17B-16E-Instruct-FP8": "🖼️ Supports images + code analysis",
        "Llama-4-Maverick-17B-128E-Instruct-FP8": "🚀 Advanced reasoning capabilities",
        "Llama-3.2-90B-Vision-Instruct": "🔍 Advanced vision + coding",
        "Llama-3.2-11B-Vision-Instruct": "📱 Compact multimodal model",
        "Llama-3.1-405B-Instruct": "🏆 Most capable, slower responses",
        "Llama-3.1-70B-Instruct": "⚖️ Good balance of speed and capability",
        "Llama-3.1-8B-Instruct": "🏃 Fastest responses"
    },
    "loading_indicators": {
        "70B": "🧠 Processing with advanced model...",
        "405B": "🚀 Using flagship model (this may take longer)...",
        "8B": "⚡ Generating fast response...",
        "Scout": "🖼️ Analyzing with multimodal capabilities...",
        "Vision": "👁️ Processing with vision capabilities..."
    },
    "default_loading_message": "🤖 Thinking...",
    "default_model": "Llama-3.3-70B-Instruct"
}

# Reasoning Configuration
REASONING_CONFIG = {
    "reasoning_types": {
        "chain_of_thought": "🔗 Chain-of-Thought (Step-by-step reasoning)",
        "react": "🔄 ReAct (Reasoning + Acting)",
        "reflection": "🪞 Reflection (Self-critique and improvement)",
        "tree_of_thought": "🌳 Tree-of-Thought (Explore multiple paths)",
        "loop_of_thought": "🔄 Loop-of-Thought (Iterative refinement)"
    },
    "default_reasoning_type": "chain_of_thought",
    "default_cot_enabled": False,
    "nltk_features_description": "🔬 **Enhanced Analysis**: Uses NLTK for advanced linguistic analysis including sentiment, complexity, and semantic understanding."
}

# UI Configuration
UI_CONFIG = {
    "page_title": "SilentCodingLegend AI Agent",
    "page_icon": "🤖",
    "layout": "wide",
    "sidebar_state": "expanded",
    "app_name": "SilentCodingLegend AI Agent",
    "app_subtitle": "Advanced AI with Chain-of-Thought reasoning",
    "app_icon": "🤖",
    "chat_placeholder": "Ask me anything about coding...",
    "max_input_length": 5000,
    "tool_suggestions": [
        "🌐 \"Search the web for the latest Python frameworks\"",
        "📁 \"List files in my current directory\"", 
        "🔍 \"Analyze this code file for potential issues\"",
        "📊 \"Generate a report on project structure\""
    ]
}

# Session Configuration
SESSION_CONFIG = {
    "timeout_minutes": 30,
    "max_message_history": 100,
    "session_id_prefix": "streamlit"
}

# Plugin Configuration
PLUGIN_CONFIG = {
    "discovery_timeout": 30,  # seconds
    "max_init_retries": 3,
    "enabled_by_default": True
}

# Security Settings
SECURITY_CONFIG = {
    "allowed_file_extensions": ['.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.yaml', '.yml'],
    "max_file_size_mb": 10,
    "sanitize_user_input": True,
    "max_input_length": 5000
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "cache_ttl_seconds": 3600,  # 1 hour
    "max_concurrent_requests": 10
}

# Error Handling Configuration
ERROR_CONFIG = {
    "error_id_prefix": "SCL-ERR",
    "generic_error_message": "❌ An unexpected error occurred. Please try again later.",
    "connection_error_message": "🔌 Connection failed. Please check your internet connection and try again.",
    "timeout_error_message": "⏱️ Request timed out. Please try again with a shorter message."
}

# File Paths
PATHS_CONFIG = {
    "css_file_path": "assets/styles.css",
    "backup_css_file_path": "style.css"  # Fallback to existing file
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_chain_of_thought": True,
    "enable_tool_calling": True,
    "enable_plugin_system": True,
    "enable_enhanced_memory": True,
    "enable_debug_mode": False
}

# Logging Configuration
LOGGING_CONFIG = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": "INFO"
}

# Advanced AI Capabilities Configuration
ADVANCED_AI_CONFIG = {
    # Multi-modal AI settings
    "multimodal": {
        "enabled": True,
        "supported_formats": {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
            "audio": [".mp3", ".wav", ".ogg", ".m4a"],
            "video": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
            "documents": [".pdf", ".docx", ".txt", ".md"]
        },
        "max_file_size_mb": 50,
        "vision_models": ["Llama-4-Scout-17B-16E-Instruct-FP8", "Llama-3.2-90B-Vision-Instruct", "Llama-3.2-11B-Vision-Instruct"],
        "analysis_features": ["object_detection", "text_extraction", "scene_description", "code_analysis"]
    },
    
    # Code execution sandbox
    "code_sandbox": {
        "enabled": True,
        "supported_languages": ["python", "javascript", "bash", "sql"],
        "timeout_seconds": 30,
        "memory_limit_mb": 512,
        "max_output_lines": 1000,
        "allowed_imports": [
            "numpy", "pandas", "matplotlib", "seaborn", "plotly", 
            "requests", "json", "datetime", "math", "random", "os", "sys"
        ],
        "restricted_functions": ["exec", "eval", "open", "__import__", "compile"],
        "sandbox_directory": "/tmp/scl_sandbox"
    },
    
    # AI-powered testing
    "ai_testing": {
        "enabled": True,
        "test_frameworks": ["pytest", "unittest", "jest", "mocha"],
        "coverage_threshold": 80,
        "test_types": ["unit", "integration", "end_to_end", "performance"],
        "auto_generate": True,
        "mock_generation": True,
        "test_data_generation": True
    },
    
    # Code refactoring suggestions
    "code_refactoring": {
        "enabled": True,
        "analysis_types": [
            "complexity_reduction", "performance_optimization", "readability_improvement",
            "security_enhancement", "design_pattern_application", "code_smell_detection"
        ],
        "supported_languages": ["python", "javascript", "typescript", "java", "cpp"],
        "severity_levels": ["info", "warning", "error", "critical"],
        "auto_fix_suggestions": True,
        "best_practices_enforcement": True
    }
}

# Tool Suggestions for Advanced Features
ADVANCED_TOOL_SUGGESTIONS = [
    "🖼️ \"Analyze this image and extract any code or text\"",
    "🎵 \"Process this audio file for speech-to-text conversion\"", 
    "📹 \"Extract frames from this video for analysis\"",
    "⚡ \"Execute this Python code safely in a sandbox\"",
    "🧪 \"Generate comprehensive tests for this function\"",
    "🔧 \"Refactor this code for better performance and readability\"",
    "🛡️ \"Analyze this code for security vulnerabilities\"",
    "📊 \"Generate performance benchmarks for this algorithm\""
]

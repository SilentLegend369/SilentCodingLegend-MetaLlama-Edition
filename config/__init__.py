"""Config package initialization"""

# Import all configurations from the main config module
import sys
from pathlib import Path

# Add parent directory to path to import the main config
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from app_config import *
except ImportError as e:
    print(f"Error importing app_config: {e}")
    # Fallback defaults
    MODEL_CONFIG = {}
    REASONING_CONFIG = {}
    PERFORMANCE_CONFIG = {"cache_ttl_seconds": 3600, "max_concurrent_requests": 10}
    ERROR_CONFIG = {}
    PATHS_CONFIG = {}
    UI_CONFIG = {}
    AGENT_CONFIG = {}
    ADVANCED_CONFIG = {}

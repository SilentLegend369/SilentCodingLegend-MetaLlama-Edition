"""
Analytics Configuration Module
Centralized configuration for analytics dashboard
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "conversations"
LOGS_DIR = BASE_DIR / "logs"

@dataclass
class ModelPricing:
    """Model pricing configuration"""
    # Example pricing (adjust based on your actual model costs)
    gpt_4_input: float = 30.0 / 1_000_000  # $30.00 per 1M input tokens
    gpt_4_output: float = 60.0 / 1_000_000  # $60.00 per 1M output tokens
    gpt_35_input: float = 1.5 / 1_000_000   # $1.50 per 1M input tokens  
    gpt_35_output: float = 2.0 / 1_000_000  # $2.00 per 1M output tokens
    default_input: float = 5.0 / 1_000_000   # Default pricing
    default_output: float = 15.0 / 1_000_000

@dataclass
class AnalyticsConfig:
    """Analytics dashboard configuration"""
    data_directory: Path = DATA_DIR
    logs_directory: Path = LOGS_DIR
    max_files_to_process: int = 1000
    token_estimation_ratio: float = 4.0  # 1 token ≈ 4 characters
    cache_ttl: int = 300  # 5 minutes cache TTL
    max_chart_points: int = 100
    date_format: str = '%Y-%m-%d'
    pricing: ModelPricing = field(default_factory=ModelPricing)

# Global configuration instance
ANALYTICS_CONFIG = AnalyticsConfig()

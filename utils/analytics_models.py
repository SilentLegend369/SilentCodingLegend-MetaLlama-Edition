"""
Analytics Data Models
Type-safe data classes for analytics results
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class AnalyticsResult:
    """Type-safe container for analytics results"""
    total_conversations: int = 0
    total_messages: int = 0
    total_tokens: int = 0
    user_tokens: int = 0
    assistant_tokens: int = 0
    avg_conversation_length: float = 0.0
    model_usage: Dict[str, int] = field(default_factory=dict)
    daily_usage: Dict[str, int] = field(default_factory=dict)
    reasoning_usage: Dict[str, int] = field(default_factory=dict)
    nltk_enhancements: int = 0
    avg_confidence: float = 0.0
    conversation_lengths: List[int] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    error_rate: float = 0.0
    estimated_cost: float = 0.0
    
    @property
    def conversations_per_day(self) -> float:
        """Calculate average conversations per day"""
        if not self.daily_usage:
            return 0.0
        return len(self.daily_usage) / max(1, len(self.daily_usage))
    
    @property
    def avg_tokens_per_conversation(self) -> float:
        """Calculate average tokens per conversation"""
        if self.total_conversations == 0:
            return 0.0
        return self.total_tokens / self.total_conversations
    
    @property
    def user_to_assistant_ratio(self) -> float:
        """Calculate ratio of user to assistant tokens"""
        if self.assistant_tokens == 0:
            return 0.0
        return self.user_tokens / self.assistant_tokens

@dataclass
class ConversationMetrics:
    """Metrics for individual conversation analysis"""
    id: str
    timestamp: Optional[datetime]
    message_count: int
    token_count: int
    model_used: Optional[str]
    confidence_score: Optional[float]
    reasoning_type: Optional[str]
    nltk_enhanced: bool = False
    source_file: Optional[str] = None
    
@dataclass
class PerformanceInsight:
    """Container for performance insights"""
    message: str
    severity: str  # 'success', 'warning', 'error', 'info'
    category: str  # 'performance', 'usage', 'cost', 'quality'
    value: Optional[float] = None
    threshold: Optional[float] = None

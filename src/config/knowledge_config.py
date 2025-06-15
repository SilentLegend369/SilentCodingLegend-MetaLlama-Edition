"""
Configuration for Knowledge Management Dashboard
Centralized configuration following best practices for security, performance, and maintainability
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class KnowledgeFeature(Enum):
    """Available knowledge management features"""
    SEMANTIC_SEARCH = "semantic_search"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    KNOWLEDGE_NOTES = "knowledge_notes"
    ANALYTICS = "analytics"
    MANAGEMENT = "management"
    EXPORT = "export"
    CLEANUP = "cleanup"


@dataclass
class SecurityLimits:
    """Security limits and constraints"""
    max_search_query_length: int = 500
    min_search_query_length: int = 3
    max_note_title_length: int = 200
    max_note_content_length: int = 10000
    max_tag_length: int = 50
    max_tags_per_note: int = 10
    max_search_results: int = 100
    max_entities_display: int = 200
    max_relationships_display: int = 50
    session_timeout_minutes: int = 60
    rate_limit_requests_per_minute: int = 100
    allowed_file_extensions: List[str] = field(default_factory=lambda: ['.txt', '.md', '.json'])
    max_file_size_mb: int = 10


@dataclass
class PerformanceSettings:
    """Performance and caching settings"""
    cache_ttl_seconds: int = 300  # 5 minutes
    stats_refresh_minutes: int = 5
    async_timeout_seconds: int = 30
    batch_size_entities: int = 50
    batch_size_documents: int = 20
    max_concurrent_operations: int = 5
    pagination_size: int = 20
    debounce_delay_ms: int = 500


@dataclass
class KnowledgeConfig:
    """Knowledge Management configuration settings"""
    
    # UI Configuration
    PAGE_TITLE: str = "Knowledge Management - SilentCodingLegend"
    PAGE_ICON: str = "🧠"
    LAYOUT: str = "wide"
    
    # Security limits
    security: SecurityLimits = field(default_factory=SecurityLimits)
    
    # Performance settings
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    
    # Feature flags
    features_enabled: Dict[KnowledgeFeature, bool] = field(default_factory=lambda: {
        KnowledgeFeature.SEMANTIC_SEARCH: True,
        KnowledgeFeature.KNOWLEDGE_GRAPH: True,
        KnowledgeFeature.KNOWLEDGE_NOTES: True,
        KnowledgeFeature.ANALYTICS: True,
        KnowledgeFeature.MANAGEMENT: True,
        KnowledgeFeature.EXPORT: True,
        KnowledgeFeature.CLEANUP: True,
    })
    
    # UI Messages
    SUCCESS_MESSAGES: Dict[str, str] = None
    ERROR_MESSAGES: Dict[str, str] = None
    WARNING_MESSAGES: Dict[str, str] = None
    INFO_MESSAGES: Dict[str, str] = None
    
    # Validation patterns
    validation_patterns: Dict[str, str] = field(default_factory=lambda: {
        "session_id": r"^[a-zA-Z0-9_-]{1,64}$",
        "entity_id": r"^[a-zA-Z0-9_-]{1,128}$",
        "tag": r"^[a-zA-Z0-9_-]{1,50}$",
        "category": r"^[a-zA-Z0-9_-]{1,30}$",
        "safe_text": r"^[a-zA-Z0-9\s.,_\-?!():;\"']+$"
    })
    
    # Entity and relationship types
    entity_types: List[str] = field(default_factory=lambda: [
        "PERSON", "ORGANIZATION", "LOCATION", "EVENT", "CONCEPT",
        "TECHNOLOGY", "PROGRAMMING_LANGUAGE", "FRAMEWORK", "LIBRARY",
        "DATABASE", "API", "METHOD", "FUNCTION", "CLASS", "VARIABLE"
    ])
    
    relationship_types: List[str] = field(default_factory=lambda: [
        "RELATED_TO", "CONTAINS", "USES", "IMPLEMENTS", "EXTENDS",
        "CALLS", "DEPENDS_ON", "SIMILAR_TO", "OPPOSITE_OF", "EXAMPLE_OF"
    ])
    
    # Note categories
    note_categories: List[str] = field(default_factory=lambda: [
        "general", "programming", "debugging", "architecture", 
        "best-practices", "tutorials", "documentation", "research"
    ])
    
    # Search suggestions
    search_suggestions: List[str] = field(default_factory=lambda: [
        "Python programming", "Error debugging", "Machine learning",
        "Web development", "API integration", "Database queries",
        "React components", "TypeScript features", "Docker containers", "Git workflows"
    ])
    
    
    def __post_init__(self):
        """Initialize message dictionaries and validate configuration"""
        if self.SUCCESS_MESSAGES is None:
            self.SUCCESS_MESSAGES = {
                'note_added': "✅ Knowledge note added successfully!",
                'note_updated': "✅ Knowledge note updated successfully!",
                'note_deleted': "🗑️ Knowledge note deleted successfully!",
                'cache_cleared': "🔄 Cache cleared and data refreshed!",
                'search_completed': "🔍 Search completed successfully!",
                'export_completed': "📤 Export completed successfully!",
                'cleanup_completed': "🧹 Data cleanup completed successfully!",
                'system_initialized': "🚀 Knowledge management system initialized successfully!"
            }
        
        if self.ERROR_MESSAGES is None:
            self.ERROR_MESSAGES = {
                'connection_error': "❌ Connection Error: Could not connect to the knowledge base.",
                'invalid_input': "❌ Invalid input: Please check your input and try again.",
                'search_failed': "❌ Search failed: Unable to perform search operation.",
                'note_save_failed': "❌ Failed to save note: Please try again later.",
                'initialization_failed': "❌ Failed to initialize knowledge management system.",
                'unexpected_error': "❌ An unexpected error occurred. Please contact support.",
                'memory_manager_init': "❌ Failed to initialize memory manager.",
                'search_query_empty': "❌ Please enter a search query.",
                'search_query_too_long': f"❌ Search query must be less than {self.security.max_search_query_length} characters.",
                'note_title_required': "❌ Note title is required.",
                'note_title_too_long': f"❌ Note title must be less than {self.security.max_note_title_length} characters.",
                'note_content_required': "❌ Note content is required.",
                'note_content_too_long': f"❌ Note content must be less than {self.security.max_note_content_length} characters.",
                'too_many_tags': f"❌ Maximum {self.security.max_tags_per_note} tags allowed.",
                'tag_too_long': f"❌ Each tag must be less than {self.security.max_tag_length} characters.",
                'invalid_session_id': "❌ Invalid session ID format.",
                'invalid_entity_type': "❌ Invalid entity type selected.",
                'export_failed': "❌ Export operation failed.",
                'cleanup_failed': "❌ Data cleanup operation failed.",
                'stats_load_failed': "❌ Failed to load statistics.",
                'system_unavailable': "❌ Knowledge management system is temporarily unavailable."
            }
        
        if self.WARNING_MESSAGES is None:
            self.WARNING_MESSAGES = {
                'empty_query': "⚠️ Please enter a search query.",
                'query_too_short': f"⚠️ Search query must be at least {self.security.min_search_query_length} characters long.",
                'query_too_long': f"⚠️ Search query is too long. Maximum {self.security.max_search_query_length} characters allowed.",
                'invalid_characters': "⚠️ Invalid characters detected in input.",
                'no_results': "ℹ️ No results found for your search query.",
                'system_unavailable': "⚠️ Knowledge management system is temporarily unavailable.",
                'stats_outdated': "⚠️ Statistics may be outdated. Consider refreshing.",
                'export_large': "⚠️ Export may take some time for large datasets.",
                'cleanup_permanent': "⚠️ Data cleanup is permanent and cannot be undone."
            }
        
        if self.INFO_MESSAGES is None:
            self.INFO_MESSAGES = {
                'search_help': "💡 Use natural language to search through conversations and knowledge.",
                'graph_help': "💡 Explore entities and relationships in your knowledge base.",
                'notes_help': "💡 Add structured knowledge notes to enhance your knowledge base.",
                'analytics_help': "💡 View insights and trends from your knowledge data.",
                'management_help': "💡 Manage and maintain your knowledge base.",
                'loading_stats': "📊 Loading knowledge base statistics...",
                'searching': "🔍 Searching knowledge base...",
                'exporting': "📤 Exporting knowledge base...",
                'cleaning': "🧹 Cleaning up old data..."
            }
    
    def is_feature_enabled(self, feature: KnowledgeFeature) -> bool:
        """Check if a feature is enabled"""
        return self.features_enabled.get(feature, False)
    
    def validate_input(self, text: str, pattern_key: str) -> bool:
        """Validate input against pattern"""
        if pattern_key not in self.validation_patterns:
            return False
        pattern = self.validation_patterns[pattern_key]
        return bool(re.match(pattern, text))
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input"""
        # Remove potentially dangerous characters
        safe_pattern = self.validation_patterns.get("safe_text", r"^[a-zA-Z0-9\s.,_\-?!():;\"']+$")
        if not re.match(safe_pattern, text):
            # Remove unsafe characters
            text = re.sub(r'[^\w\s.,_\-?!():;"\']', '', text)
        return text.strip()
    
    def get_tab_config(self, tab_key: str) -> Dict[str, Any]:
        """Get configuration for a specific tab"""
        return TAB_CONFIG.get(tab_key, {})
    
    def validate_limits(self) -> bool:
        """Validate configuration limits"""
        try:
            assert self.security.max_search_query_length > 0
            assert self.security.max_note_content_length > 0
            assert self.performance.cache_ttl_seconds > 0
            assert self.performance.async_timeout_seconds > 0
            return True
        except AssertionError:
            return False


# Global configuration instance
KNOWLEDGE_CONFIG = KnowledgeConfig()


# Tab configurations
TAB_CONFIG = {
    'overview': {
        'title': "📊 Overview",
        'description': "System statistics and health metrics",
        'order': 1,
        'enabled': True
    },
    'search': {
        'title': "🔍 Semantic Search", 
        'description': "Search through knowledge base using AI",
        'order': 2,
        'enabled': True
    },
    'graph': {
        'title': "🕸️ Knowledge Graph",
        'description': "Visualize entity relationships",
        'order': 3,
        'enabled': True
    },
    'notes': {
        'title': "📝 Knowledge Notes",
        'description': "Manage knowledge entries",
        'order': 4,
        'enabled': True
    },
    'analytics': {
        'title': "📈 Analytics",
        'description': "Usage patterns and insights",
        'order': 5,
        'enabled': True
    },
    'management': {
        'title': "⚙️ Management",
        'description': "System administration tools",
        'order': 6,
        'enabled': True
    }
}


# Chart configurations
CHART_CONFIG = {
    'default_height': 400,
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'theme': 'plotly_white',
    'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
    'font_size': 12,
    'title_font_size': 14
}


# Default values for forms and inputs
DEFAULTS = {
    'max_search_results': 10,
    'max_entities': 20,
    'cleanup_days': 30,
    'export_format': 'json',
    'include_vectors': False,
    'note_category': 'general',
    'pagination_size': 20,
    'chart_height': 400
}


# Export configurations
EXPORT_CONFIG = {
    'formats': ['json', 'csv', 'xlsx'],
    'max_file_size_mb': 100,
    'include_metadata': True,
    'include_vectors': False,
    'compression': 'zip'
}


# Cache keys for Streamlit session state
CACHE_KEYS = {
    'memory_manager': 'knowledge_memory_manager',
    'stats': 'knowledge_stats',
    'last_refresh': 'knowledge_last_refresh',
    'search_results': 'knowledge_search_results',
    'selected_entities': 'knowledge_selected_entities',
    'chart_data': 'knowledge_chart_data'
}

"""
Enhanced Analytics Processor with Security, Performance, and Maintainability Improvements
Professional-grade analytics engine for SilentCodingLegend AI Agent
"""

import json
import logging
import streamlit as st
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict, Counter
from dataclasses import asdict

# Local imports
from config.analytics_config import ANALYTICS_CONFIG, ModelPricing
from utils.analytics_models import AnalyticsResult, ConversationMetrics, PerformanceInsight

# Configure logging
logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_path(path: Path, base_path: Path) -> bool:
        """Validate that path is within base_path to prevent path traversal"""
        try:
            path.resolve().relative_to(base_path.resolve())
            return True
        except ValueError:
            logger.warning(f"Path traversal attempt detected: {path}")
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent injection attacks"""
        # Remove dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        return "".join(c for c in filename if c in safe_chars)

class CostEstimator:
    """Advanced cost estimation with model-specific pricing"""
    
    def __init__(self, pricing: ModelPricing = None):
        self.pricing = pricing or ANALYTICS_CONFIG.pricing
    
    def estimate_cost(self, user_tokens: int, assistant_tokens: int, model: str = None) -> float:
        """Estimate cost based on token usage and model type"""
        if not model:
            input_rate = self.pricing.default_input
            output_rate = self.pricing.default_output
        elif "gpt-4" in model.lower():
            input_rate = self.pricing.gpt_4_input
            output_rate = self.pricing.gpt_4_output
        elif "gpt-3.5" in model.lower():
            input_rate = self.pricing.gpt_35_input
            output_rate = self.pricing.gpt_35_output
        else:
            input_rate = self.pricing.default_input
            output_rate = self.pricing.default_output
        
        input_cost = user_tokens * input_rate
        output_cost = assistant_tokens * output_rate
        return input_cost + output_cost

class EnhancedAnalyticsProcessor:
    """
    Professional-grade analytics processor with enhanced security, performance, and maintainability
    """
    
    def __init__(self, config=None):
        self.config = config or ANALYTICS_CONFIG
        self.data_dir = self.config.data_directory
        self.logs_dir = self.config.logs_directory
        self.security = SecurityValidator()
        self.cost_estimator = CostEstimator(self.config.pricing)
        
        # Ensure directories exist and are secure
        self._validate_directories()
    
    def _validate_directories(self):
        """Validate and create necessary directories securely"""
        try:
            # Ensure data directory exists
            if not self.data_dir.exists():
                logger.warning(f"Data directory not found: {self.data_dir}")
                self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Validate paths are within expected boundaries
            if not self.security.validate_path(self.data_dir, Path.cwd()):
                raise SecurityError(f"Invalid data directory path: {self.data_dir}")
                
        except Exception as e:
            logger.error(f"Directory validation failed: {e}")
            raise
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_conversation_data(_self) -> List[Dict]:
        """
        Load conversation data with enhanced security and error handling
        Note: _self parameter naming is required for Streamlit caching
        """
        conversations = []
        
        if not _self.data_dir.exists():
            st.warning(f"📂 Conversation data directory not found: {_self.data_dir}")
            return conversations
        
        # Get JSON files securely
        json_files = list(_self.data_dir.glob("*.json"))
        
        if not json_files:
            st.info("📁 No conversation files found in the data directory.")
            return conversations
        
        # Limit files processed to prevent DoS
        if len(json_files) > _self.config.max_files_to_process:
            st.warning(f"⚠️ Found {len(json_files)} files. Processing only the first {_self.config.max_files_to_process} for performance.")
            json_files = json_files[:_self.config.max_files_to_process]
        
        files_processed = 0
        files_failed = 0
        
        for file_path in json_files:
            try:
                # Additional security validation
                if not _self.security.validate_path(file_path, _self.data_dir):
                    logger.warning(f"Skipping potentially unsafe file path: {file_path}")
                    continue
                
                with file_path.open('r', encoding='utf-8', errors='replace') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            item['source_file'] = _self.security.sanitize_filename(file_path.name)
                            conversations.append(item)
                elif isinstance(data, dict):
                    data['source_file'] = _self.security.sanitize_filename(file_path.name)
                    conversations.append(data)
                
                files_processed += 1
                
            except json.JSONDecodeError as e:
                files_failed += 1
                st.warning(f"🔴 Failed to decode JSON from '{file_path.name}': {str(e)[:100]}...")
                logger.error(f"JSON decode error in {file_path}: {e}")
            except UnicodeDecodeError as e:
                files_failed += 1
                st.warning(f"🔴 Encoding error in '{file_path.name}': File may be corrupted")
                logger.error(f"Unicode error in {file_path}: {e}")
            except PermissionError:
                files_failed += 1
                st.error(f"🔴 Permission denied reading '{file_path.name}'")
                logger.error(f"Permission denied: {file_path}")
            except Exception as e:
                files_failed += 1
                st.error(f"🔴 Unexpected error reading '{file_path.name}': {str(e)[:100]}...")
                logger.error(f"Unexpected error in {file_path}: {e}")
        
        # Report processing results
        if files_processed > 0:
            st.success(f"✅ Successfully processed {files_processed} files")
        if files_failed > 0:
            st.error(f"❌ Failed to process {files_failed} files")
        
        logger.info(f"Loaded {len(conversations)} conversations from {files_processed} files")
        return conversations
    
    @st.cache_data(ttl=300)
    def analyze_conversations(_self, conversations: Tuple[Dict, ...]) -> AnalyticsResult:
        """
        Analyze conversations with comprehensive metrics and type safety
        Note: conversations converted to tuple for caching hashability
        """
        if not conversations:
            return AnalyticsResult()
        
        # Convert back to list for processing
        conversations_list = list(conversations)
        
        # Initialize counters and metrics
        total_conversations = len(conversations_list)
        total_messages = 0
        total_tokens = 0
        user_tokens = 0
        assistant_tokens = 0
        
        model_usage = Counter()
        daily_usage = defaultdict(int)
        conversation_lengths = []
        response_times = []
        reasoning_usage = defaultdict(int)
        nltk_enhancements = 0
        confidence_scores = []
        total_errors = 0
        
        # Process each conversation
        for conv in conversations_list:
            try:
                # Extract and validate timestamp
                timestamp = _self._extract_timestamp(conv)
                if timestamp:
                    day = timestamp.strftime(_self.config.date_format)
                    daily_usage[day] += 1
                
                # Process messages
                messages = _self._extract_messages(conv)
                total_messages += len(messages)
                conversation_lengths.append(len(messages))
                
                # Analyze tokens per message
                for msg in messages:
                    content = msg.get('content', '')
                    if content:
                        tokens = _self._estimate_tokens(content)
                        total_tokens += tokens
                        
                        role = msg.get('role', '').lower()
                        if role == 'user':
                            user_tokens += tokens
                        elif role == 'assistant':
                            assistant_tokens += tokens
                
                # Extract model information
                model = _self._extract_model(conv)
                if model:
                    model_usage[model] += 1
                
                # Analyze reasoning and enhancements
                reasoning_info = _self._extract_reasoning_info(conv)
                if reasoning_info:
                    reasoning_type = reasoning_info.get('type', 'unknown')
                    reasoning_usage[reasoning_type] += 1
                    
                    if reasoning_info.get('nltk_enhanced', False):
                        nltk_enhancements += 1
                    
                    confidence = reasoning_info.get('confidence')
                    if confidence is not None and isinstance(confidence, (int, float)):
                        confidence_scores.append(float(confidence))
                
                # Extract response times if available
                response_time = _self._extract_response_time(conv)
                if response_time is not None:
                    response_times.append(response_time)
                    
            except KeyError as e:
                total_errors += 1
                logger.warning(f"Missing key {e} in conversation from {conv.get('source_file', 'unknown')}")
            except (TypeError, ValueError) as e:
                total_errors += 1
                logger.warning(f"Data type error in conversation from {conv.get('source_file', 'unknown')}: {e}")
            except Exception as e:
                total_errors += 1
                logger.error(f"Unexpected error processing conversation: {e}")
        
        # Calculate advanced metrics
        avg_conversation_length = np.mean(conversation_lengths) if conversation_lengths else 0.0
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        error_rate = total_errors / total_conversations if total_conversations > 0 else 0.0
        
        # Estimate costs
        estimated_cost = _self.cost_estimator.estimate_cost(user_tokens, assistant_tokens)
        
        return AnalyticsResult(
            total_conversations=total_conversations,
            total_messages=total_messages,
            total_tokens=total_tokens,
            user_tokens=user_tokens,
            assistant_tokens=assistant_tokens,
            avg_conversation_length=avg_conversation_length,
            model_usage=dict(model_usage),
            daily_usage=dict(daily_usage),
            reasoning_usage=dict(reasoning_usage),
            nltk_enhancements=nltk_enhancements,
            avg_confidence=avg_confidence,
            conversation_lengths=conversation_lengths,
            response_times=response_times,
            error_rate=error_rate,
            estimated_cost=estimated_cost
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Enhanced token estimation with validation"""
        if not text or not isinstance(text, str):
            return 0
        
        # More sophisticated token estimation
        # Account for whitespace, punctuation, and common patterns
        clean_text = text.strip()
        if not clean_text:
            return 0
        
        # Basic estimation: adjust ratio based on text characteristics
        ratio = self.config.token_estimation_ratio
        
        # Adjust for code-heavy content (more tokens per character)
        if any(keyword in clean_text.lower() for keyword in ['def ', 'class ', 'import ', 'function', '{', '}', ';']):
            ratio *= 0.8  # Code tends to have more tokens per character
        
        return max(1, int(len(clean_text) / ratio))
    
    def _extract_timestamp(self, conv: Dict) -> Optional[datetime]:
        """Extract timestamp with multiple fallback strategies"""
        timestamp_keys = ['timestamp', 'created_at', 'date', 'time', 'datetime']
        
        for key in timestamp_keys:
            if key in conv and conv[key]:
                try:
                    value = conv[key]
                    if isinstance(value, str):
                        # Handle various timestamp formats
                        for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', 
                                   '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                            try:
                                return datetime.strptime(value.replace('Z', ''), fmt.replace('Z', ''))
                            except ValueError:
                                continue
                        # Try ISO format parsing
                        return datetime.fromisoformat(value.replace('Z', '+00:00'))
                    elif isinstance(value, (int, float)):
                        return datetime.fromtimestamp(value)
                except (ValueError, TypeError) as e:
                    logger.debug(f"Failed to parse timestamp {key}={conv[key]}: {e}")
                    continue
        
        return None
    
    def _extract_messages(self, conv: Dict) -> List[Dict]:
        """Extract messages with validation"""
        message_keys = ['messages', 'conversation', 'content', 'dialog']
        
        for key in message_keys:
            if key in conv and isinstance(conv[key], list):
                return [msg for msg in conv[key] if isinstance(msg, dict)]
        
        return []
    
    def _extract_model(self, conv: Dict) -> Optional[str]:
        """Extract model information with fallbacks"""
        model_keys = ['model', 'model_name', 'llm_model', 'ai_model', 'engine']
        
        for key in model_keys:
            if key in conv and conv[key]:
                model = str(conv[key]).strip()
                if model:
                    return model
        
        return None
    
    def _extract_reasoning_info(self, conv: Dict) -> Optional[Dict]:
        """Extract reasoning and enhancement information"""
        reasoning_keys = ['reasoning', 'chain_of_thought', 'cot', 'thinking']
        
        for key in reasoning_keys:
            if key in conv and isinstance(conv[key], dict):
                return conv[key]
        
        # Check for NLTK enhancements in metadata
        if 'metadata' in conv and isinstance(conv['metadata'], dict):
            metadata = conv['metadata']
            if any(key in metadata for key in ['nltk', 'enhancement', 'reasoning']):
                return metadata
        
        return None
    
    def _extract_response_time(self, conv: Dict) -> Optional[float]:
        """Extract response time if available"""
        time_keys = ['response_time', 'processing_time', 'duration', 'elapsed']
        
        for key in time_keys:
            if key in conv:
                try:
                    return float(conv[key])
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def generate_insights(self, analysis: AnalyticsResult) -> List[PerformanceInsight]:
        """Generate intelligent performance insights"""
        insights = []
        
        # Performance insights
        if analysis.avg_conversation_length < 5:
            insights.append(PerformanceInsight(
                "🟡 Short conversations detected - consider improving engagement",
                "warning", "performance", analysis.avg_conversation_length, 5.0
            ))
        elif analysis.avg_conversation_length > 15:
            insights.append(PerformanceInsight(
                "🟢 High engagement - users having detailed conversations",
                "success", "performance", analysis.avg_conversation_length, 15.0
            ))
        
        # Cost insights
        if analysis.estimated_cost > 10.0:
            insights.append(PerformanceInsight(
                f"💰 High estimated costs: ${analysis.estimated_cost:.2f} - monitor usage",
                "warning", "cost", analysis.estimated_cost, 10.0
            ))
        
        # Quality insights
        if analysis.avg_confidence > 0 and analysis.avg_confidence < 0.7:
            insights.append(PerformanceInsight(
                f"🟡 Low confidence scores ({analysis.avg_confidence:.2f}) - review model performance",
                "warning", "quality", analysis.avg_confidence, 0.7
            ))
        elif analysis.avg_confidence >= 0.9:
            insights.append(PerformanceInsight(
                f"🟢 Excellent confidence scores ({analysis.avg_confidence:.2f})",
                "success", "quality", analysis.avg_confidence, 0.9
            ))
        
        # Enhancement insights
        if analysis.nltk_enhancements > 0:
            enhancement_rate = analysis.nltk_enhancements / analysis.total_conversations
            insights.append(PerformanceInsight(
                f"🧠 NLTK enhancements active in {enhancement_rate:.1%} of conversations",
                "info", "usage", enhancement_rate
            ))
        
        # Error rate insights
        if analysis.error_rate > 0.1:
            insights.append(PerformanceInsight(
                f"🔴 High error rate ({analysis.error_rate:.1%}) - check data quality",
                "error", "quality", analysis.error_rate, 0.1
            ))
        elif analysis.error_rate == 0:
            insights.append(PerformanceInsight(
                "🟢 No processing errors detected - excellent data quality",
                "success", "quality", 0.0
            ))
        
        return insights

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

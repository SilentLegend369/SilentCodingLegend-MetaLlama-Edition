"""
Input validation and sanitization utilities for Knowledge Management Dashboard
Implements security best practices for user input handling
"""

import re
import html
import bleach
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import streamlit as st
from src.config.knowledge_config import KNOWLEDGE_CONFIG


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    cleaned_value: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class KnowledgeValidator:
    """Comprehensive input validator for knowledge management features"""
    
    def __init__(self):
        self.config = KNOWLEDGE_CONFIG
        
        # Allowed HTML tags for rich text (very limited for security)
        self.allowed_tags = ['b', 'i', 'em', 'strong', 'code', 'pre']
        self.allowed_attributes = {}
        
        # Common patterns for validation
        self.patterns = {
            'safe_text': re.compile(r'^[a-zA-Z0-9\s.,_\-?!():;"\'\n\r]+$'),
            'session_id': re.compile(r'^[a-zA-Z0-9_-]{1,64}$'),
            'entity_id': re.compile(r'^[a-zA-Z0-9_-]{1,128}$'),
            'tag': re.compile(r'^[a-zA-Z0-9_-]{1,50}$'),
            'category': re.compile(r'^[a-zA-Z0-9_-]{1,30}$'),
            'filename': re.compile(r'^[a-zA-Z0-9._-]{1,255}$')
        }


def sanitize_input(text: str) -> str:
    """
    Basic sanitization function for backward compatibility
    """
    validator = KnowledgeValidator()
    return validator._sanitize_text(text)


    
    def validate_search_query(self, query: str) -> ValidationResult:
        """Validate search query input"""
        if not query or not query.strip():
            return ValidationResult(
                is_valid=False,
                error_message=self.config.ERROR_MESSAGES['search_query_empty']
            )
        
        query = query.strip()
        
        # Check length limits
        if len(query) < self.config.security.min_search_query_length:
            return ValidationResult(
                is_valid=False,
                error_message=self.config.WARNING_MESSAGES['query_too_short']
            )
        
        if len(query) > self.config.security.max_search_query_length:
            return ValidationResult(
                is_valid=False,
                error_message=self.config.WARNING_MESSAGES['query_too_long']
            )
        
        # Sanitize and validate characters
        cleaned_query = self._sanitize_text(query)
        
        return ValidationResult(
            is_valid=True,
            cleaned_value=cleaned_query
        )
    
    def validate_note_title(self, title: str) -> ValidationResult:
        """Validate note title"""
        if not title or not title.strip():
            return ValidationResult(
                is_valid=False,
                error_message=self.config.ERROR_MESSAGES['note_title_required']
            )
        
        title = title.strip()
        
        if len(title) > self.config.security.max_note_title_length:
            return ValidationResult(
                is_valid=False,
                error_message=self.config.ERROR_MESSAGES['note_title_too_long']
            )
        
        cleaned_title = self._sanitize_text(title)
        
        return ValidationResult(
            is_valid=True,
            cleaned_value=cleaned_title
        )
    
    def validate_note_content(self, content: str) -> ValidationResult:
        """Validate note content"""
        if not content or not content.strip():
            return ValidationResult(
                is_valid=False,
                error_message=self.config.ERROR_MESSAGES['note_content_required']
            )
        
        content = content.strip()
        
        if len(content) > self.config.security.max_note_content_length:
            return ValidationResult(
                is_valid=False,
                error_message=self.config.ERROR_MESSAGES['note_content_too_long']
            )
        
        # Allow more flexible content but still sanitize
        cleaned_content = self._sanitize_rich_text(content)
        
        return ValidationResult(
            is_valid=True,
            cleaned_value=cleaned_content
        )
    
    def validate_tags(self, tags_input: str) -> ValidationResult:
        """Validate and clean tags input"""
        if not tags_input:
            return ValidationResult(is_valid=True, cleaned_value="")
        
        # Split tags by comma and clean each one
        raw_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        if len(raw_tags) > self.config.security.max_tags_per_note:
            return ValidationResult(
                is_valid=False,
                error_message=self.config.ERROR_MESSAGES['too_many_tags']
            )
        
        validated_tags = []
        warnings = []
        
        for tag in raw_tags:
            if len(tag) > self.config.security.max_tag_length:
                warnings.append(f"Tag '{tag}' is too long and was truncated")
                tag = tag[:self.config.security.max_tag_length]
            
            # Validate tag format
            if not self.patterns['tag'].match(tag):
                warnings.append(f"Tag '{tag}' contains invalid characters and was cleaned")
                tag = re.sub(r'[^a-zA-Z0-9_-]', '', tag)
            
            if tag:  # Only add non-empty tags
                validated_tags.append(tag.lower())  # Normalize to lowercase
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in validated_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        return ValidationResult(
            is_valid=True,
            cleaned_value=','.join(unique_tags),
            warnings=warnings
        )
    
    def _sanitize_text(self, text: str) -> str:
        """Basic text sanitization"""
        # HTML escape
        text = html.escape(text)
        
        # Remove null bytes and other dangerous characters
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _sanitize_rich_text(self, text: str) -> str:
        """Sanitize rich text content allowing basic formatting"""
        # Use bleach to clean HTML while allowing basic tags
        cleaned = bleach.clean(
            text,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
        
        # Additional cleaning
        cleaned = cleaned.replace('\x00', '')
        
        return cleaned


# Global validator instance
knowledge_validator = KnowledgeValidator()


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Legacy function for backward compatibility
    """
    result = knowledge_validator.validate_search_query(query)
    return result.is_valid, result.error_message


def validate_note_content(title: str, content: str) -> Tuple[bool, Optional[str]]:
    """
    Legacy function for backward compatibility
    """
    # Validate title
    title_result = knowledge_validator.validate_note_title(title)
    if not title_result.is_valid:
        return False, title_result.error_message
    
    # Validate content
    content_result = knowledge_validator.validate_note_content(content)
    if not content_result.is_valid:
        return False, content_result.error_message
    
    return True, None


def validate_entity_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate entity name for knowledge graph operations (legacy function)
    """
    if not name or not name.strip():
        return False, "Entity name is required."
    
    sanitized_name = sanitize_input(name)
    if not sanitized_name:
        return False, "Entity name contains invalid characters."
    
    if len(sanitized_name) > 100:
        return False, "Entity name is too long. Maximum 100 characters allowed."
    
    return True, None


def safe_int_conversion(value: str, default: int = 10, min_val: int = 1, max_val: int = 100) -> int:
    """
    Safely convert string to integer with bounds checking.
    """
    try:
        converted = int(value)
        return max(min_val, min(max_val, converted))
    except (ValueError, TypeError):
        return default


def validate_and_sanitize_form_data(form_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validate and sanitize entire form data dictionary
    
    Returns:
        Tuple of (is_valid, cleaned_data, error_messages)
    """
    cleaned_data = {}
    error_messages = []
    all_warnings = []
    
    validator = knowledge_validator
    
    # Define validation mapping
    validation_map = {
        'search_query': validator.validate_search_query,
        'note_title': validator.validate_note_title,
        'note_content': validator.validate_note_content,
        'tags': validator.validate_tags,
    }
    
    for field, value in form_data.items():
        if field in validation_map:
            result = validation_map[field](value)
            
            if result.is_valid:
                cleaned_data[field] = result.cleaned_value
                if result.warnings:
                    all_warnings.extend(result.warnings)
            else:
                error_messages.append(result.error_message)
        else:
            # For fields without specific validation, just clean the text
            if isinstance(value, str):
                cleaned_data[field] = validator._sanitize_text(value)
            else:
                cleaned_data[field] = value
    
    # Show warnings if any
    if all_warnings:
        for warning in all_warnings:
            st.warning(warning)
    
    return len(error_messages) == 0, cleaned_data, error_messages


def display_validation_errors(errors: List[str]) -> None:
    """Display validation errors in Streamlit"""
    if errors:
        for error in errors:
            st.error(error)


def create_safe_input(label: str, value: str = "", max_length: int = None, 
                     validator_func=None, **kwargs) -> str:
    """Create a safe text input with built-in validation"""
    if max_length is None:
        max_length = KNOWLEDGE_CONFIG.security.max_search_query_length
    
    user_input = st.text_input(label, value=value, max_chars=max_length, **kwargs)
    
    if user_input and validator_func:
        result = validator_func(user_input)
        if not result.is_valid:
            st.error(result.error_message)
            return ""
        if result.warnings:
            for warning in result.warnings:
                st.warning(warning)
        return result.cleaned_value or user_input
    
    return user_input

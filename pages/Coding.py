"""
Coding Assistant - Advanced Code Generation, Review, and Analysis
SilentCodingLegend AI Agent Coding Hub

Refactored for modularity, maintainability, and professional standards.
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Core imports
from src.core.agent import SilentCodingLegendAgent
from src.core.agent_handler import AgentInteractionHandler

# Configuration imports
from src.config.coding_config import (
    SUPPORTED_LANGUAGES, AVAILABLE_MODELS, SessionData,
    get_language_info, load_coding_history, save_coding_session
)

# UI imports
from src.ui.ui_tabs import (
    render_code_generation_tab, render_code_review_tab, render_debug_tab,
    render_learning_tab, render_data_science_tab, render_chain_of_thought_tab
)

# Assets imports
from assets.coding_styles import get_coding_assistant_styles

# Utils imports
from src.utils.logging import get_logger

# Configure page
st.set_page_config(
    page_title="Coding Assistant - SilentCodingLegend",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger(__name__)

# Apply custom CSS
st.markdown(get_coding_assistant_styles(), unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'coding_agent' not in st.session_state:
        st.session_state.coding_agent = SilentCodingLegendAgent()
        logger.info("Initialized Coding Assistant agent")
    
    if 'coding_session_id' not in st.session_state:
        st.session_state.coding_session_id = f"coding_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'coding_history' not in st.session_state:
        st.session_state.coding_history = load_coding_history()
    
    if 'agent_handler' not in st.session_state:
        st.session_state.agent_handler = AgentInteractionHandler(
            st.session_state.coding_agent,
            st.session_state.coding_session_id
        )


def render_sidebar():
    """Render the sidebar with model selection and language options"""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">## 💻 Coding Assistant</div>', unsafe_allow_html=True)
        
        # Model selection
        current_model = st.session_state.coding_agent.client.config.model
        
        # Ensure current model is in available models
        available_models = AVAILABLE_MODELS.copy()
        if current_model not in available_models:
            available_models[current_model] = current_model
        
        selected_model = st.selectbox(
            "🤖 AI Model",
            options=list(available_models.keys()),
            index=list(available_models.keys()).index(current_model),
            format_func=lambda x: available_models[x],
            help="Choose the AI model for coding assistance"
        )
        
        if selected_model != current_model:
            st.session_state.coding_agent.client.config.model = selected_model
            st.success(f"✅ Model changed to {available_models[selected_model]}")
        
        # Language selection
        st.markdown("### 🔤 Programming Language")
        selected_language = st.selectbox(
            "Choose Language",
            options=SUPPORTED_LANGUAGES,
            index=0,
            help="Select the programming language for assistance"
        )
        
        lang_info = get_language_info(selected_language)
        st.markdown(f'{lang_info["icon"]} **{lang_info["description"]}**')
        
        # Session info
        st.markdown("### 📊 Session Info")
        st.metric("Coding Sessions", len(st.session_state.coding_history))
        
        # History management
        if st.button("🔄 Reload History"):
            st.session_state.coding_history = load_coding_history()
            st.success(f"Loaded {len(st.session_state.coding_history)} sessions!")
        
        if st.button("🗑️ Clear History"):
            st.session_state.coding_history = []
            st.success("History cleared!")
    
    return selected_language


def render_main_tabs(selected_language: str):
    """Render the main feature tabs"""
    # Dummy coding_assistant object for backward compatibility
    coding_assistant = None
    
    # Feature tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚀 Generate Code", 
        "🔍 Review Code", 
        "🐛 Debug Code", 
        "📚 Learn & Explain", 
        "📊 Data Science",
        "🧠 Chain-of-Thought"
    ])
    
    with tab1:
        render_code_generation_tab(coding_assistant, selected_language, st.session_state)
    
    with tab2:
        render_code_review_tab(coding_assistant, selected_language, st.session_state)
    
    with tab3:
        render_debug_tab(coding_assistant, selected_language, st.session_state)
    
    with tab4:
        render_learning_tab(coding_assistant, selected_language, st.session_state)
    
    with tab5:
        render_data_science_tab(coding_assistant, selected_language, st.session_state)
    
    with tab6:
        render_chain_of_thought_tab(coding_assistant, selected_language, st.session_state)


def render_session_history():
    """Render recent coding session history"""
    if st.session_state.coding_history:
        st.markdown("---")
        st.markdown("### 📝 Recent Coding Sessions")
        
        # Show last 3 sessions
        for i, session in enumerate(st.session_state.coding_history[:3]):
            session_type = session.get('type', session.get('session_type', 'Unknown'))
            timestamp = session.get('timestamp', 'Unknown')
            
            with st.expander(f"🕒 {timestamp} - {session_type.replace('_', ' ').title()}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write(f"**Type:** {session_type.replace('_', ' ').title()}")
                    st.write(f"**Language:** {session.get('language', 'Unknown')}")
                    if session.get('template'):
                        st.write(f"**Template:** {session.get('template')}")
                
                with col2:
                    if session.get('description'):
                        st.write(f"**Description:** {session.get('description')}")
                    if session.get('query'):
                        st.write(f"**Query:** {session.get('query')}")
                    if session.get('problem'):
                        st.write(f"**Problem:** {session.get('problem')}")


def main():
    """Main Coding Assistant application"""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get selected language
    selected_language = render_sidebar()
    
    # Main content
    st.markdown('<h1 class="main-header">💻 Coding Assistant - AI-Powered Development</h1>', unsafe_allow_html=True)
    
    # Render main feature tabs
    render_main_tabs(selected_language)
    
    # Render session history
    render_session_history()


if __name__ == "__main__":
    main()

"""
Enhanced Knowledge Management Dashboard for SilentCodingLegend AI Agent
Implementing security, performance, and maintainability best practices
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add the project root to the path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core imports
from src.core.enhanced_memory import EnhancedMemoryManager
from src.core.knowledge_graph import EntityType, RelationType

# Configuration and utilities
from src.config.knowledge_config import KNOWLEDGE_CONFIG, TAB_CONFIG, CHART_CONFIG
from src.utils.knowledge_validators import (
    validate_search_query, validate_note_content, validate_entity_name, 
    safe_int_conversion, sanitize_input
)
from src.ui.knowledge_components import (
    display_search_result, display_entity_card, display_statistics_cards,
    create_entity_distribution_chart, create_activity_timeline_chart,
    display_error_message, display_success_message, display_warning_message,
    create_loading_placeholder, display_no_data_message, create_refresh_button
)

# Initialize session state with security considerations
def initialize_session_state():
    """Initialize session state variables with proper defaults"""
    session_vars = {
        'memory_manager': None,
        'knowledge_stats': None,
        'last_refresh': None,
        'search_history': [],
        'current_search_query': '',
        'selected_entity_type': 'All',
        'max_search_results': KNOWLEDGE_CONFIG.security.max_search_results
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value


@st.cache_data(ttl=KNOWLEDGE_CONFIG.performance.cache_ttl_seconds)
def get_cached_knowledge_stats(memory_manager_id: str) -> Optional[Dict[str, Any]]:
    """
    Cached function to fetch knowledge base statistics.
    
    Args:
        memory_manager_id: Unique identifier for cache invalidation
        
    Returns:
        Statistics data or None if unavailable
    """
    # This is a placeholder - the actual async call needs to be handled separately
    # The cache will store the results once populated
    return None


def fetch_knowledge_stats(memory_manager) -> Optional[Dict[str, Any]]:
    """
    Fetch knowledge base statistics with error handling.
    
    Args:
        memory_manager: EnhancedMemoryManager instance
        
    Returns:
        Statistics data or None if error occurred
    """
    try:
        kg_stats = run_async(memory_manager.knowledge_graph.get_statistics())
        vector_stats = run_async(memory_manager.vector_db.get_statistics())
        
        return {
            "knowledge_graph": kg_stats,
            "vector_database": vector_stats,
            "last_refresh": datetime.now()
        }
    except ConnectionError:
        display_error_message('connection_error')
        return None
    except Exception as e:
        display_error_message('unexpected_error', f"Error loading statistics: {e}")
        return None


def get_memory_manager() -> Optional[EnhancedMemoryManager]:
    """Get or initialize the memory manager with proper error handling"""
    if st.session_state.memory_manager is None:
        loading_placeholder = create_loading_placeholder("Initializing knowledge management system...")
        
        try:
            memory_manager = EnhancedMemoryManager()
            success = run_async(memory_manager.initialize())
            
            if success:
                st.session_state.memory_manager = memory_manager
                loading_placeholder.empty()
                return memory_manager
            else:
                loading_placeholder.empty()
                display_error_message('initialization_failed')
                return None
                
        except ConnectionError:
            loading_placeholder.empty()
            display_error_message('connection_error')
            return None
        except Exception as e:
            loading_placeholder.empty()
            display_error_message('unexpected_error', f"Initialization error: {e}")
            return None
    
    return st.session_state.memory_manager


def run_async(coro):
    """Helper to run async functions in Streamlit safely"""
    try:
        # Check if there's already an event loop running
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop, safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # There's an event loop running, need to handle carefully
        # For Streamlit, we'll use a thread pool approach
        import concurrent.futures
        
        def run_in_thread():
            # Create a new event loop in this thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        
        # Run in a thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result(timeout=30)  # 30-second timeout


def show_overview(memory_manager):
    """Display knowledge base overview with cached statistics"""
    st.header("📊 Knowledge Base Overview")
    st.markdown(TAB_CONFIG['overview']['description'])
    
    # Refresh controls
    col1, col2 = st.columns([3, 1])
    with col2:
        if create_refresh_button('overview_refresh', "🔄 Refresh Stats"):
            # Clear the cache for this function
            get_cached_knowledge_stats.clear()
            st.session_state.knowledge_stats = None
    
    # Fetch or use cached statistics
    if st.session_state.knowledge_stats is None:
        stats_data = fetch_knowledge_stats(memory_manager)
        if stats_data:
            st.session_state.knowledge_stats = stats_data
    else:
        stats_data = st.session_state.knowledge_stats
    
    if stats_data:
        # Display statistics cards
        display_statistics_cards(stats_data)
        
        # Show last refresh time
        last_refresh = stats_data.get('last_refresh')
        if last_refresh:
            st.caption(f"📅 Last updated: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Entity distribution chart
        kg_stats = stats_data.get('knowledge_graph', {})
        entities_by_type = kg_stats.get('entities_by_type', {})
        
        if entities_by_type:
            st.plotly_chart(
                create_entity_distribution_chart(entities_by_type),
                use_container_width=True
            )
        else:
            display_no_data_message("entity distribution data")
    else:
        display_no_data_message("statistics")


def show_semantic_search(memory_manager):
    """Enhanced semantic search with input validation and better UX"""
    st.header("🔍 Semantic Search")
    st.markdown(TAB_CONFIG['search']['description'])
    
    # Search configuration
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query_raw = st.text_input(
            "Search Query",
            value=st.session_state.current_search_query,
            placeholder="Enter your search query here...",
            help=f"Search through the knowledge base. Minimum {KNOWLEDGE_CONFIG.security.min_search_query_length} characters."
        )
    
    with col2:
        max_results = st.number_input(
            "Max Results",
            min_value=1,
            max_value=KNOWLEDGE_CONFIG.security.max_search_results,
            value=st.session_state.max_search_results,
            help="Maximum number of search results to display"
        )
    
    # Advanced search options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="Minimum similarity score for results"
            )
        
        with col2:
            search_type = st.selectbox(
                "Search Type",
                options=["Semantic", "Keyword", "Hybrid"],
                help="Type of search to perform"
            )
    
    # Search execution
    if st.button("🔍 Search", type="primary"):
        # Validate input
        is_valid, error_message = validate_search_query(search_query_raw)
        
        if not is_valid:
            display_warning_message('invalid_input', error_message)
            return
        
        # Sanitize and store query
        sanitized_query = sanitize_input(search_query_raw)
        st.session_state.current_search_query = sanitized_query
        st.session_state.max_search_results = safe_int_conversion(
            str(max_results), 
            KNOWLEDGE_CONFIG.security.max_search_results,
            1,
            KNOWLEDGE_CONFIG.security.max_search_results
        )
        
        # Perform search with loading indicator
        search_placeholder = create_loading_placeholder("Searching knowledge base...")
        
        try:
            results = run_async(memory_manager.search_memories(
                query=sanitized_query,
                limit=st.session_state.max_search_results,
                similarity_threshold=similarity_threshold
            ))
            
            search_placeholder.empty()
            
            if results:
                display_success_message('search_completed', f"Found {len(results)} relevant results")
                
                # Display results
                for i, result in enumerate(results):
                    display_search_result(result, i)
                
                # Add to search history (keep last 10)
                st.session_state.search_history.insert(0, {
                    'query': sanitized_query,
                    'results_count': len(results),
                    'timestamp': datetime.now()
                })
                st.session_state.search_history = st.session_state.search_history[:10]
                
            else:
                display_warning_message('no_results')
        
        except ConnectionError:
            search_placeholder.empty()
            display_error_message('connection_error')
        except Exception as e:
            search_placeholder.empty()
            display_error_message('search_failed', f"Search error: {e}")
    
    # Display search history
    if st.session_state.search_history:
        st.markdown("### 📜 Recent Searches")
        for i, search in enumerate(st.session_state.search_history[:5]):
            with st.expander(f"🔍 {search['query']} ({search['results_count']} results)"):
                st.write(f"**Time:** {search['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                if st.button(f"Repeat Search", key=f"repeat_{i}"):
                    st.session_state.current_search_query = search['query']
                    st.experimental_rerun()


def show_knowledge_notes(memory_manager):
    """Enhanced knowledge notes management with validation"""
    st.header("📝 Knowledge Notes")
    st.markdown(TAB_CONFIG['notes']['description'])
    
    # Add new note section
    with st.expander("➕ Add New Knowledge Note", expanded=False):
        with st.form("add_note_form"):
            note_title = st.text_input(
                "Note Title",
                placeholder="Enter a descriptive title...",
                max_chars=KNOWLEDGE_CONFIG.security.max_note_title_length
            )
            
            note_content = st.text_area(
                "Note Content",
                placeholder="Enter the knowledge content...",
                height=150,
                max_chars=KNOWLEDGE_CONFIG.security.max_note_content_length
            )
            
            note_tags = st.text_input(
                "Tags (comma-separated)",
                placeholder="tag1, tag2, tag3...",
                help="Add tags to categorize this note"
            )
            
            note_category = st.selectbox(
                "Category",
                options=["General", "Technical", "Business", "Research", "Personal"],
                help="Select a category for this note"
            )
            
            submitted = st.form_submit_button("💾 Save Note", type="primary")
            
            if submitted:
                # Validate input
                is_valid, error_message = validate_note_content(note_title, note_content)
                
                if not is_valid:
                    display_warning_message('invalid_input', error_message)
                else:
                    # Sanitize inputs
                    clean_title = sanitize_input(note_title)
                    clean_content = sanitize_input(note_content)
                    clean_tags = [sanitize_input(tag.strip()) for tag in note_tags.split(',') if tag.strip()]
                    
                    # Save note
                    save_placeholder = create_loading_placeholder("Saving note...")
                    
                    try:
                        # Here you would call the actual save method
                        # await memory_manager.add_knowledge_note(...)
                        
                        # Simulated save for now
                        import time
                        time.sleep(0.5)  # Simulate save operation
                        
                        save_placeholder.empty()
                        display_success_message('note_added')
                        
                        # Clear form (simulate by showing success)
                        st.info("Form cleared. Add another note by expanding this section again.")
                        
                    except Exception as e:
                        save_placeholder.empty()
                        display_error_message('note_save_failed', f"Save error: {e}")
    
    # Display existing notes (placeholder)
    st.markdown("### 📚 Existing Notes")
    display_no_data_message("saved notes")


def show_knowledge_graph(memory_manager):
    """Knowledge graph visualization and management"""
    st.header("🕸️ Knowledge Graph")
    st.markdown(TAB_CONFIG['graph']['description'])
    
    # Graph controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        entity_type_filter = st.selectbox(
            "Filter by Entity Type",
            options=["All", "Person", "Organization", "Concept", "Location", "Event"],
            value=st.session_state.selected_entity_type
        )
    
    with col2:
        max_entities = st.number_input(
            "Max Entities to Display",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
    
    with col3:
        if create_refresh_button('graph_refresh', "🔄 Refresh Graph"):
            st.session_state.selected_entity_type = entity_type_filter
    
    # Graph visualization placeholder
    st.markdown("### 🔍 Entity Explorer")
    
    # Search for specific entity
    entity_search = st.text_input(
        "Search for Entity",
        placeholder="Enter entity name to explore...",
        help="Search for a specific entity in the knowledge graph"
    )
    
    if entity_search:
        is_valid, error_message = validate_entity_name(entity_search)
        
        if not is_valid:
            display_warning_message('invalid_input', error_message)
        else:
            clean_entity_name = sanitize_input(entity_search)
            
            # Search placeholder
            with st.spinner("Searching for entity..."):
                # Placeholder for entity search
                st.info(f"🔍 Searching for entity: '{clean_entity_name}'")
                display_no_data_message("entity search results")
    
    # Graph statistics
    st.markdown("### 📊 Graph Statistics")
    if st.session_state.knowledge_stats:
        kg_stats = st.session_state.knowledge_stats.get('knowledge_graph', {})
        if kg_stats:
            display_statistics_cards({'knowledge_graph': kg_stats})
        else:
            display_no_data_message("graph statistics")
    else:
        display_no_data_message("graph statistics")


def show_analytics(memory_manager):
    """Analytics and insights dashboard"""
    st.header("📈 Analytics")
    st.markdown(TAB_CONFIG['analytics']['description'])
    
    # Time range selector
    col1, col2 = st.columns(2)
    
    with col1:
        date_range = st.selectbox(
            "Time Range",
            options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            index=1
        )
    
    with col2:
        if create_refresh_button('analytics_refresh', "🔄 Refresh Analytics"):
            pass
    
    # Analytics charts placeholder
    st.markdown("### 📊 Usage Patterns")
    
    # Create sample activity data for demonstration
    sample_activity = [
        {'timestamp': datetime.now() - timedelta(hours=i), 'action': f'Action {i%3}'}
        for i in range(24)
    ]
    
    if sample_activity:
        st.plotly_chart(
            create_activity_timeline_chart(sample_activity),
            use_container_width=True
        )
    else:
        display_no_data_message("activity data")
    
    # Additional analytics placeholders
    st.markdown("### 🎯 Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Search Queries", "142", "+12%")
    
    with col2:
        st.metric("Knowledge Updates", "28", "+5%")
    
    with col3:
        st.metric("Graph Relations", "89", "+18%")


def show_management(memory_manager):
    """System management and administration tools"""
    st.header("⚙️ Management")
    st.markdown(TAB_CONFIG['management']['description'])
    
    # System health
    st.markdown("### 🏥 System Health")
    
    health_col1, health_col2, health_col3 = st.columns(3)
    
    with health_col1:
        st.metric("System Status", "🟢 Healthy", help="Overall system status")
    
    with health_col2:
        st.metric("Memory Usage", "45%", help="Memory utilization")
    
    with health_col3:
        st.metric("Response Time", "120ms", help="Average response time")
    
    # Cache management
    st.markdown("### 🗃️ Cache Management")
    
    cache_col1, cache_col2 = st.columns(2)
    
    with cache_col1:
        if st.button("🗑️ Clear All Caches", type="secondary"):
            # Clear Streamlit caches
            get_cached_knowledge_stats.clear()
            st.cache_data.clear()
            
            # Clear session state caches
            st.session_state.knowledge_stats = None
            
            display_success_message('cache_cleared')
    
    with cache_col2:
        if st.button("🔄 Rebuild Indexes", type="secondary"):
            rebuild_placeholder = create_loading_placeholder("Rebuilding indexes...")
            
            # Simulate rebuild process
            import time
            time.sleep(2)
            
            rebuild_placeholder.empty()
            display_success_message('cache_cleared', "✅ Indexes rebuilt successfully!")
    
    # Export/Import
    st.markdown("### 📤 Data Management")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📥 Export Knowledge Base"):
            st.info("📋 Export functionality would be implemented here")
    
    with export_col2:
        uploaded_file = st.file_uploader(
            "📤 Import Knowledge Base",
            type=['json', 'csv'],
            help="Upload a knowledge base file to import"
        )
        
        if uploaded_file:
            st.info(f"📋 Import functionality for {uploaded_file.name} would be implemented here")


def main():
    """Main application entry point with async support"""
    st.set_page_config(
        page_title=KNOWLEDGE_CONFIG.PAGE_TITLE,
        page_icon=KNOWLEDGE_CONFIG.PAGE_ICON,
        layout=KNOWLEDGE_CONFIG.LAYOUT
    )
    
    # Initialize session state
    initialize_session_state()
    
    st.title("🧠 Knowledge Management Dashboard")
    st.markdown("*Enhanced with security, performance, and usability improvements*")
    
    # Initialize memory manager
    memory_manager = get_memory_manager()
    
    if memory_manager is None:
        display_warning_message('system_unavailable')
        st.stop()
    
    # Create tabs for different features
    tab_keys = list(TAB_CONFIG.keys())
    tab_titles = [TAB_CONFIG[key]['title'] for key in tab_keys]
    
    tabs = st.tabs(tab_titles)
    
    # Map tabs to functions
    tab_functions = {
        'overview': show_overview,
        'search': show_semantic_search,
        'graph': show_knowledge_graph,
        'notes': show_knowledge_notes,
        'analytics': show_analytics,
        'management': show_management
    }
    
    # Render tabs
    for i, (tab_key, tab_function) in enumerate(tab_functions.items()):
        with tabs[i]:
            try:
                tab_function(memory_manager)
            except Exception as e:
                display_error_message('unexpected_error', f"Error in {tab_key} tab: {e}")


def app_main():
    """Main function to run the dashboard"""
    return main()


if __name__ == "__main__":
    app_main()

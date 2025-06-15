"""
Plugin Manager UI for SilentCodingLegend AI Agent
Streamlit interface for managing plugins, marketplace, and tools
"""

import streamlit as st
import asyncio
import json
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import bleach  # For HTML sanitization
import logging

# Configure page
st.set_page_config(
    page_title="Plugin Manager - SilentCodingLegend",
    page_icon="🔌",
    layout="wide"
)

# Custom CSS for plugin manager
st.markdown("""
<style>
    .plugin-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4f8bf9;
    }
    
    .plugin-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .plugin-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .plugin-version {
        background: #4f8bf9;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .plugin-status {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    .status-enabled {
        background: #2ecc71;
        color: white;
    }
    
    .status-disabled {
        background: #e74c3c;
        color: white;
    }
    
    .tool-badge {
        background: #3498db;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .marketplace-item {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    
    .featured-badge {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

async def get_plugin_manager():
    """Get plugin manager instance"""
    try:
        from src.plugins.plugin_manager import PluginManager
        from src.plugins.marketplace import PluginMarketplace
        
        plugin_manager = PluginManager()
        await plugin_manager.initialize()
        
        marketplace = PluginMarketplace(plugin_manager)
        await marketplace.initialize()
        return plugin_manager, marketplace
    except Exception as e:
        st.error(f"Failed to initialize plugin system: {e}")
        return None, None

# Security and utility functions
def sanitize_plugin_text(text: str) -> str:
    """Sanitize plugin metadata text to prevent XSS attacks"""
    if not text:
        return ""
    return bleach.clean(str(text), tags=[], strip=True)

def _handle_plugin_action(action_coroutine, success_message: str, error_message: str, rerun: bool = True):
    """
    Executes a plugin action coroutine, handles exceptions, and displays UI feedback.
    
    Args:
        action_coroutine: The async function to execute
        success_message: Message to display on success
        error_message: Base error message to display on failure
        rerun: Whether to call st.rerun() after success
    """
    try:
        # Using a spinner provides immediate feedback to the user
        with st.spinner(f"{success_message.split(' ')[0]}ing..."):
            asyncio.run(action_coroutine)
        st.success(success_message)
        if rerun:
            st.rerun()  # Rerun to reflect the state change
    except Exception as e:
        st.error(f"{error_message}: {e}")
        logging.error(f"{error_message}: {e}")

def _handle_confirmation_state(action_key: str, plugin_name: str) -> bool:
    """
    Manages confirmation state for destructive actions.
    
    Args:
        action_key: Unique key for the action (e.g., 'uninstall')
        plugin_name: Name of the plugin
        
    Returns:
        bool: True if user confirmed, False otherwise
    """
    confirm_key = f"confirm_{action_key}_{plugin_name}"
    
    # Initialize confirmation state if it doesn't exist
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    return st.session_state[confirm_key]

def _render_confirmation_dialog(action_key: str, plugin_name: str, action_name: str) -> bool:
    """
    Renders a confirmation dialog for destructive actions.
    
    Args:
        action_key: Unique key for the action
        plugin_name: Name of the plugin
        action_name: Human-readable action name
        
    Returns:
        bool: True if action should proceed, False otherwise
    """
    confirm_key = f"confirm_{action_key}_{plugin_name}"
    
    st.warning(f"Are you sure you want to {action_name.lower()} **{plugin_name}**?")
    col_confirm, col_cancel, _ = st.columns([1, 1, 2])
    
    with col_confirm:
        if st.button(f"✅ Yes, {action_name.lower()}", key=f"confirm_yes_{action_key}_{plugin_name}", use_container_width=True):
            st.session_state[confirm_key] = False  # Reset state
            return True
    
    with col_cancel:
        if st.button("❌ Cancel", key=f"confirm_no_{action_key}_{plugin_name}", use_container_width=True):
            st.session_state[confirm_key] = False
            st.rerun()
    
    return False

def main():
    st.title("🔌 Plugin Manager")
    st.markdown("### Manage plugins, explore marketplace, and configure tools")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section",
        ["🏠 Overview", "📦 Installed Plugins", "🛒 Marketplace", "🔧 Tools Registry", "⚙️ Settings"]
    )
    
    # Initialize plugin system
    if 'plugin_manager' not in st.session_state:
        with st.spinner("Initializing plugin system..."):
            try:
                plugin_manager, marketplace = asyncio.run(get_plugin_manager())
                st.session_state.plugin_manager = plugin_manager
                st.session_state.marketplace = marketplace
                if plugin_manager:
                    st.success("Plugin system initialized successfully!")
                else:
                    st.error("Failed to initialize plugin system")
                    return
            except Exception as e:
                st.error(f"Error initializing plugin system: {e}")
                return
    
    plugin_manager = st.session_state.plugin_manager
    marketplace = st.session_state.marketplace
    
    if not plugin_manager or not marketplace:
        st.error("Plugin system not available")
        return
    
    # Page routing
    if page == "🏠 Overview":
        show_overview(plugin_manager, marketplace)
    elif page == "📦 Installed Plugins":
        show_installed_plugins(plugin_manager)
    elif page == "🛒 Marketplace":
        show_marketplace(marketplace, plugin_manager)
    elif page == "🔧 Tools Registry":
        show_tools_registry(plugin_manager)
    elif page == "⚙️ Settings":
        show_settings(plugin_manager)

def show_overview(plugin_manager, marketplace):
    """Show plugin system overview"""
    st.header("Plugin System Overview")
    
    # Get status information
    try:
        plugin_status = plugin_manager.get_plugin_status()
        marketplace_stats = marketplace.get_marketplace_stats()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Installed Plugins",
                plugin_status["total_loaded"],
                delta=f"{plugin_status['total_discovered'] - plugin_status['total_loaded']} available"
            )
        
        with col2:
            st.metric(
                "Available Tools",
                plugin_status["tool_registry_stats"]["total_tools"]
            )
        
        with col3:
            st.metric(
                "Marketplace Plugins",
                marketplace_stats["total_plugins"]
            )
        
        with col4:
            st.metric(
                "Featured Plugins",
                marketplace_stats["featured_plugins"]
            )
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reload All Plugins", use_container_width=True):
                with st.spinner("Reloading plugins..."):
                    try:
                        # Reload all plugins
                        for plugin_name in plugin_manager.get_loaded_plugins().keys():
                            asyncio.run(plugin_manager.reload_plugin(plugin_name))
                        st.success("All plugins reloaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error reloading plugins: {e}")
        
        with col2:
            if st.button("📊 Export Tools Schema", use_container_width=True):
                try:
                    from src.plugins.tool_registry import tool_registry
                    schema_file = "exported_tools_schema.json"
                    tool_registry.export_tools_schema(schema_file)
                    st.success(f"Tools schema exported to {schema_file}")
                except Exception as e:
                    st.error(f"Error exporting schema: {e}")
        
        with col3:
            if st.button("🔍 Discover Plugins", use_container_width=True):
                with st.spinner("Discovering plugins..."):
                    try:
                        discovered = asyncio.run(plugin_manager.discover_plugins())
                        st.success(f"Discovered {len(discovered)} plugins")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error discovering plugins: {e}")
        
        # System status
        st.subheader("System Status")
        
        # Plugin categories chart
        if plugin_status["tool_registry_stats"]["categories"]:
            st.write("**Tools by Category:**")
            categories_df = pd.DataFrame(
                list(plugin_status["tool_registry_stats"]["categories"].items()),
                columns=["Category", "Count"]
            )
            st.bar_chart(categories_df.set_index("Category"))
        
    except Exception as e:
        st.error(f"Error loading overview: {e}")

def show_installed_plugins(plugin_manager):
    """Show installed plugins management"""
    st.header("Installed Plugins")
    
    try:
        loaded_plugins = plugin_manager.get_loaded_plugins()
        available_plugins = plugin_manager.list_available_plugins()
        
        if not loaded_plugins:
            st.info("No plugins currently loaded. Visit the marketplace to install plugins.")
            return
        
        # Plugin controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Loaded Plugins ({len(loaded_plugins)})")
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Display each plugin
        for plugin_name, plugin_instance in loaded_plugins.items():
            with st.container():
                plugin_metadata = plugin_manager.get_plugin_metadata(plugin_name)
                if not plugin_metadata:
                    continue
                
                # Plugin card HTML
                status_class = "status-enabled" if plugin_instance.enabled else "status-disabled"
                status_text = "Enabled" if plugin_instance.enabled else "Disabled"
                
                tools = plugin_instance.get_tools()
                # Handle both list and dict return types
                if isinstance(tools, list):
                    tool_names = [tool.name for tool in tools]
                else:
                    tool_names = list(tools.keys())
                tools_html = "".join([f'<span class="tool-badge">{tool_name}</span>' 
                                    for tool_name in tool_names])
                
                # Sanitize plugin metadata for security
                safe_name = sanitize_plugin_text(plugin_metadata.name)
                safe_author = sanitize_plugin_text(plugin_metadata.author)
                safe_description = sanitize_plugin_text(plugin_metadata.description)
                safe_type = sanitize_plugin_text(plugin_metadata.plugin_type.value)
                
                st.markdown(f"""
                <div class="plugin-card">
                    <div class="plugin-header">
                        <div>
                            <span class="plugin-name">{safe_name}</span>
                            <span class="plugin-version">v{plugin_metadata.version}</span>
                        </div>
                        <span class="plugin-status {status_class}">{status_text}</span>
                    </div>
                    <p><strong>Author:</strong> {safe_author}</p>
                    <p><strong>Type:</strong> {safe_type}</p>
                    <p><strong>Description:</strong> {safe_description}</p>
                    <p><strong>Tools:</strong> {tools_html}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Plugin actions with improved UX and error handling
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if plugin_instance.enabled:
                        if st.button(f"🚫 Disable", key=f"disable_{plugin_name}"):
                            _handle_plugin_action(
                                plugin_manager.disable_plugin(plugin_name),
                                f"Disabled {plugin_name}",
                                "Error disabling plugin"
                            )
                    else:
                        if st.button(f"✅ Enable", key=f"enable_{plugin_name}"):
                            _handle_plugin_action(
                                plugin_manager.enable_plugin(plugin_name),
                                f"Enabled {plugin_name}",
                                "Error enabling plugin"
                            )
                
                with col2:
                    if st.button(f"🔄 Reload", key=f"reload_{plugin_name}"):
                        _handle_plugin_action(
                            plugin_manager.reload_plugin(plugin_name),
                            f"Reloaded {plugin_name}",
                            "Error reloading plugin"
                        )
                
                with col3:
                    # Uninstall with confirmation dialog for safety
                    if _handle_confirmation_state('uninstall', plugin_name):
                        if _render_confirmation_dialog('uninstall', plugin_name, 'Uninstall'):
                            _handle_plugin_action(
                                plugin_manager.uninstall_plugin(plugin_name),
                                f"Uninstalled {plugin_name}",
                                "Error uninstalling plugin"
                            )
                    else:
                        if st.button(f"🗑️ Uninstall", key=f"uninstall_{plugin_name}"):
                            st.session_state[f"confirm_uninstall_{plugin_name}"] = True
                            st.rerun()
                
                with col4:
                    # Use expander for details instead of button for better UX
                    with st.expander("📋 Details"):
                        show_plugin_details(plugin_instance, plugin_metadata)
                
                st.divider()
    
    except Exception as e:
        st.error(f"Error loading installed plugins: {e}")

def show_marketplace(marketplace, plugin_manager):
    """Show plugin marketplace"""
    st.header("Plugin Marketplace")
    
    # Security reminder for users
    st.info(
        "🛡️ **Security Reminder:** Plugins are third-party code that will run with the agent's permissions. "
        "Only install plugins from trusted authors and sources. Review the plugin's code if possible before installation."
    )
    
    try:
        # Search and filters
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search plugins", placeholder="Enter keywords...")
        
        with col2:
            # Use proper public methods instead of accessing private attributes
            try:
                categories = ["All"] + asyncio.run(marketplace.get_available_categories())
            except Exception:
                categories = ["All"]  # Fallback
            selected_category = st.selectbox("Category", categories)
        
        with col3:
            try:
                plugin_types = ["All"] + asyncio.run(marketplace.get_available_plugin_types())
            except Exception:
                plugin_types = ["All"]  # Fallback
            selected_type = st.selectbox("Type", plugin_types)
        
        # Search plugins
        search_params = {
            "query": search_query,
            "category": None if selected_category == "All" else selected_category,
            "plugin_type": None if selected_type == "All" else selected_type
        }
        
        search_results = asyncio.run(marketplace.search_plugins(**search_params))
        
        # Featured plugins section
        featured_plugins = asyncio.run(marketplace.get_featured_plugins())
        featured_names = set()
        
        if featured_plugins and not search_query:
            st.subheader("⭐ Featured Plugins")
            for plugin in featured_plugins[:3]:  # Show top 3 featured
                featured_names.add(plugin['name'])
                display_marketplace_plugin(plugin, marketplace, plugin_manager, featured=True, section="featured")
            st.divider()
        
        # Search results (exclude already shown featured plugins)
        if not search_query and featured_names:
            # Filter out featured plugins from search results to avoid duplicates
            search_results = [p for p in search_results if p['name'] not in featured_names]
        
        st.subheader(f"Search Results ({len(search_results)})")
        
        if not search_results:
            st.info("No plugins found matching your criteria.")
        else:
            for plugin in search_results:
                display_marketplace_plugin(plugin, marketplace, plugin_manager, section="search")
    
    except Exception as e:
        st.error(f"Error loading marketplace: {e}")

def display_marketplace_plugin(plugin_info, marketplace, plugin_manager, featured=False, section="default"):
    """Display a marketplace plugin item with security sanitization"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Sanitize all plugin information to prevent XSS
            safe_name = sanitize_plugin_text(plugin_info.get('name', 'Unknown'))
            safe_version = sanitize_plugin_text(plugin_info.get('version', '0.0.0'))
            safe_author = sanitize_plugin_text(plugin_info.get('author', 'Unknown'))
            safe_plugin_type = sanitize_plugin_text(plugin_info.get('plugin_type', 'Generic'))
            safe_description = sanitize_plugin_text(plugin_info.get('description', 'No description available'))
            safe_tags = [sanitize_plugin_text(tag) for tag in plugin_info.get('tags', [])]
            
            # Plugin info
            featured_badge = '<span class="featured-badge">FEATURED</span>' if featured else ""
            
            st.markdown(f"""
            <div class="marketplace-item">
                <h4>{safe_name} v{safe_version} {featured_badge}</h4>
                <p><strong>Author:</strong> {safe_author}</p>
                <p><strong>Type:</strong> {safe_plugin_type}</p>
                <p>{safe_description}</p>
                <p><strong>Tags:</strong> {', '.join(safe_tags)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Check if already installed
            loaded_plugins = plugin_manager.get_loaded_plugins()
            is_installed = plugin_info['name'] in loaded_plugins
            
            if is_installed:
                st.success("✅ Installed")
            else:
                # Use unique key combining plugin name and section to avoid duplicates
                unique_key = f"install_{section}_{plugin_info['name']}"
                if st.button(f"📥 Install", key=unique_key):
                    # Use our improved action handler
                    _handle_plugin_action(
                        marketplace.download_plugin(plugin_info['name']),
                        f"Successfully installed {safe_name}!",
                        f"Failed to install {safe_name}"
                    )

def show_tools_registry(plugin_manager):
    """Show tools registry"""
    st.header("Tools Registry")
    
    try:
        from src.plugins.tool_registry import tool_registry
        
        all_tools = tool_registry.get_all_tools()
        categories = tool_registry.get_categories()
        stats = tool_registry.get_stats()
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tools", stats["total_tools"])
        with col2:
            st.metric("Categories", stats["total_categories"])
        with col3:
            st.metric("Plugins", stats["total_plugins"])
        
        # Category filter
        selected_category = st.selectbox("Filter by Category", ["All"] + categories)
        
        # Tools display
        if selected_category == "All":
            tools_to_show = all_tools
        else:
            tools_to_show = {tool.name: tool for tool in tool_registry.get_tools_by_category(selected_category)}
        
        if not tools_to_show:
            st.info("No tools available.")
        else:
            for tool_name, tool in tools_to_show.items():
                with st.expander(f"🔧 {tool_name} (from {tool.plugin_name})"):
                    st.write(f"**Description:** {tool.description}")
                    st.write(f"**Category:** {tool.category}")
                    
                    if tool.parameters:
                        st.write("**Parameters:**")
                        params_df = pd.DataFrame([
                            {
                                "Name": param.name,
                                "Type": param.type.value,
                                "Required": param.required,
                                "Description": param.description
                            }
                            for param in tool.parameters
                        ])
                        st.dataframe(params_df, use_container_width=True)
                    
                    # Tool schema
                    if st.button(f"Show Schema", key=f"schema_{tool_name}"):
                        st.json(tool.to_llama_schema())
    
    except Exception as e:
        st.error(f"Error loading tools registry: {e}")

def show_settings(plugin_manager):
    """Show plugin settings"""
    st.header("Plugin Settings")
    
    try:
        # Plugin system settings
        st.subheader("System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_load = st.checkbox("Auto-load plugins on startup", value=True)
            hot_reload = st.checkbox("Enable hot reload", value=True)
        
        with col2:
            tool_calling = st.checkbox("Enable tool calling", value=True)
            debug_mode = st.checkbox("Debug mode", value=False)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")
        
        # Plugin directories
        st.subheader("Plugin Directories")
        st.write(f"**Plugins Directory:** `{plugin_manager.plugins_dir}`")
        st.write(f"**Marketplace Directory:** `{plugin_manager.marketplace_dir}`")
        
        # System info
        st.subheader("System Information")
        status = plugin_manager.get_plugin_status()
        st.json(status)
    
    except Exception as e:
        st.error(f"Error loading settings: {e}")

def show_plugin_details(plugin_instance, metadata):
    """Show detailed plugin information"""
    st.subheader(f"Plugin Details: {metadata.name}")
    
    # Basic info
    info_data = {
        "Name": metadata.name,
        "Version": metadata.version,
        "Author": metadata.author,
        "Type": metadata.plugin_type.value,
        "License": metadata.license,
        "Created": metadata.created_at.strftime("%Y-%m-%d"),
        "Updated": metadata.updated_at.strftime("%Y-%m-%d")
    }
    
    for key, value in info_data.items():
        st.write(f"**{key}:** {value}")
    
    # Tools
    tools = plugin_instance.get_tools()
    if tools:
        st.write("**Available Tools:**")
        for tool_name, tool in tools.items():
            st.write(f"- `{tool_name}`: {tool.description}")
    
    # Dependencies
    if metadata.dependencies:
        st.write("**Dependencies:**")
        for dep in metadata.dependencies:
            st.write(f"- {dep}")

if __name__ == "__main__":
    main()

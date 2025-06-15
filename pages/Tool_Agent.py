"""
Tool Agent - Interactive Tool Testing and Execution Interface
"""
import streamlit as st
import asyncio
import json
import threading
from typing import Dict, Any, List
from datetime import datetime
import traceback

def run_async_safely(coro):
    """Run async coroutine safely in Streamlit context"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop in thread if current loop is running
            result = None
            exception = None
            
            def run_in_thread():
                nonlocal result, exception
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            return result
        else:
            # Can run directly
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)

# Configure page
st.set_page_config(
    page_title="Tool Agent - SilentCodingLegend",
    page_icon="🛠️",
    layout="wide"
)

# Custom CSS for tool agent
st.markdown("""
<style>
    /* Dark theme styling */
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    .tool-card {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #00D4AA;
        color: #FFFFFF;
    }
    
    .tool-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .tool-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #00D4AA;
    }
    
    .tool-plugin {
        background: #0099CC;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .parameter-input {
        background-color: #2D3748;
        color: #FFFFFF;
        border: 1px solid #4A5568;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .execution-result {
        background: linear-gradient(135deg, #1A202C, #2D3748);
        border: 1px solid #4A5568;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #FFFFFF;
    }
    
    .success-result {
        border-left: 4px solid #2ecc71;
    }
    
    .error-result {
        border-left: 4px solid #e74c3c;
    }
    
    /* Backup management specific styles */
    .backup-card {
        background: linear-gradient(135deg, #1A365D, #2D3748);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3182CE;
        color: #FFFFFF;
    }
    
    .backup-status-running {
        border-left-color: #38A169;
    }
    
    .backup-status-stopped {
        border-left-color: #E53E3E;
    }
    
    .backup-metric {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
        color: #FFFFFF;
    }
    
    .backup-metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00D4AA;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_agent():
    """Get agent instance"""
    try:
        from src.core.agent import SilentCodingLegendAgent
        return SilentCodingLegendAgent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None

async def initialize_agent(agent):
    """Initialize agent and plugin system properly"""
    try:
        if not getattr(agent, 'plugins_initialized', False):
            st.info("🔄 Initializing plugins...")
            # Use the agent's proper initialization method
            success = await agent.initialize_plugins()
            if success:
                st.success("✅ Plugins initialized successfully")
            else:
                st.error("❌ Plugin initialization failed")
            return success
        else:
            st.info("✅ Plugins already initialized")
        return True
    except Exception as e:
        st.error(f"Failed to initialize plugins: {e}")
        st.exception(e)
        return False

def display_tool_interface(tool, agent):
    """Display interactive interface for a tool"""
    with st.container():
        st.markdown(f"""
        <div class="tool-card">
            <div class="tool-header">
                <div>
                    <span class="tool-name">{tool.name}</span>
                </div>
                <span class="tool-plugin">from {tool.plugin_name}</span>
            </div>
            <p><strong>Description:</strong> {tool.description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Parameter inputs
        parameters = {}
        if tool.parameters:
            st.write("**Parameters:**")
            
            for param in tool.parameters:
                param_key = f"{tool.name}_{param.name}"
                
                if param.type.value == "string":
                    default_val = param.default if param.default is not None else ""
                    value = st.text_input(
                        f"{param.name} {'*' if param.required else ''}",
                        value=default_val,
                        help=param.description,
                        key=param_key
                    )
                    if value or not param.required:
                        parameters[param.name] = value
                        
                elif param.type.value == "boolean":
                    default_val = param.default if param.default is not None else False
                    value = st.checkbox(
                        f"{param.name} {'*' if param.required else ''}",
                        value=default_val,
                        help=param.description,
                        key=param_key
                    )
                    parameters[param.name] = value
                    
                elif param.type.value == "integer":
                    default_val = param.default if param.default is not None else 0
                    value = st.number_input(
                        f"{param.name} {'*' if param.required else ''}",
                        value=default_val,
                        help=param.description,
                        key=param_key,
                        step=1
                    )
                    parameters[param.name] = int(value)
                    
                elif param.type.value == "number":
                    default_val = param.default if param.default is not None else 0.0
                    value = st.number_input(
                        f"{param.name} {'*' if param.required else ''}",
                        value=default_val,
                        help=param.description,
                        key=param_key
                    )
                    parameters[param.name] = value
        
        # Execute button
        execute_key = f"execute_{tool.name}"
        if st.button(f"🚀 Execute {tool.name}", key=execute_key, use_container_width=True):
            
            # Validate required parameters
            missing_params = []
            for param in tool.parameters:
                if param.required and (param.name not in parameters or parameters[param.name] == ""):
                    missing_params.append(param.name)
            
            if missing_params:
                st.error(f"Missing required parameters: {', '.join(missing_params)}")
            else:
                # Execute tool
                with st.spinner(f"Executing {tool.name}..."):
                    try:
                        # Execute the tool using the agent's tool registry to handle async properly
                        if hasattr(agent, 'tool_registry') and hasattr(agent.tool_registry, 'execute_tool'):
                            result = run_async_safely(agent.tool_registry.execute_tool(tool.name, parameters))
                        else:
                            # Fallback to direct execution
                            if asyncio.iscoroutinefunction(tool.function):
                                result = run_async_safely(tool.function(**parameters))
                            else:
                                result = tool.function(**parameters)
                        
                        # Display result
                        st.markdown(f"""
                        <div class="execution-result success-result">
                            <h4>✅ Execution Result</h4>
                            <p><strong>Tool:</strong> {tool.name}</p>
                            <p><strong>Executed at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show result data
                        if isinstance(result, dict):
                            st.json(result)
                        elif isinstance(result, list):
                            st.json(result)
                        else:
                            st.code(str(result))
                            
                    except Exception as e:
                        st.markdown(f"""
                        <div class="execution-result error-result">
                            <h4>❌ Execution Error</h4>
                            <p><strong>Tool:</strong> {tool.name}</p>
                            <p><strong>Error:</strong> {str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())

async def display_backup_management():
    """Display backup management interface"""
    st.header("🔄 Backup Management")
    
    # Get agent
    agent = get_agent()
    if not agent:
        st.error("Agent not available")
        return
        
    # Initialize agent if needed
    if not await initialize_agent(agent):
        st.error("Failed to initialize agent")
        return
    
    # Check if BackupManager plugin is available
    backup_tools = {name: tool for name, tool in agent.tool_registry.get_all_tools().items() 
                   if tool.plugin_name == "BackupManager"}
    
    if not backup_tools:
        st.warning("BackupManager plugin not available. Please ensure it's installed and enabled.")
        return
    
    # Create tabs for different backup operations
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Status", "📦 Create Backup", "📋 Manage Backups", "⚙️ Configuration"])
    
    with tab1:
        st.subheader("Backup System Status")
        
        if st.button("Refresh Status"):
            try:
                status_result = await agent.tool_registry.execute_tool("backup_status", {})
                
                if status_result.get("success"):
                    status_data = status_result.get("status", {})
                    stats_data = status_result.get("statistics", {})
                    
                    # Display status metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Auto Backup", 
                                "✅ Enabled" if status_data.get("auto_backup_enabled") else "❌ Disabled")
                    
                    with col2:
                        st.metric("Backup Status", 
                                "🔄 Running" if status_data.get("auto_backup_running") else "⏸️ Stopped")
                    
                    with col3:
                        st.metric("Total Backups", stats_data.get("total_backups", 0))
                    
                    with col4:
                        st.metric("Total Size", f"{stats_data.get('total_size_mb', 0):.1f} MB")
                    
                    # Display recent backup info
                    recent_backup = stats_data.get("recent_backup")
                    if recent_backup:
                        st.subheader("Most Recent Backup")
                        st.json(recent_backup)
                    
                    # Display backup types distribution
                    backup_types = stats_data.get("backup_types", {})
                    if backup_types:
                        st.subheader("Backup Types Distribution")
                        st.bar_chart(backup_types)
                        
                else:
                    st.error(f"Failed to get backup status: {status_result.get('error')}")
                    
            except Exception as e:
                st.error(f"Error getting backup status: {e}")
    
    with tab2:
        st.subheader("Create New Backup")
        
        backup_type = st.selectbox(
            "Backup Type",
            ["full", "incremental", "configuration", "data", "plugins"],
            index=0
        )
        
        custom_name = st.text_input("Custom Name (optional)", "")
        
        if st.button("Create Backup"):
            with st.spinner("Creating backup..."):
                try:
                    backup_params = {"backup_type": backup_type}
                    if custom_name:
                        backup_params["custom_name"] = custom_name
                        
                    result = await agent.tool_registry.execute_tool("create_backup", backup_params)
                    
                    if result.get("success"):
                        st.success(f"✅ Backup created successfully!")
                        st.json(result)
                    else:
                        st.error(f"❌ Failed to create backup: {result.get('error')}")
                        
                except Exception as e:
                    st.error(f"Error creating backup: {e}")
    
    with tab3:
        st.subheader("Manage Existing Backups")
        
        if st.button("List All Backups"):
            try:
                result = await agent.tool_registry.execute_tool("list_backups", {})
                
                if result.get("success"):
                    backups = result.get("backups", [])
                    
                    if backups:
                        st.write(f"Found {len(backups)} backups:")
                        
                        for backup in backups:
                            with st.expander(f"📦 {backup.get('name', 'Unknown')} - {backup.get('type', 'unknown')}"):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.json(backup)
                                
                                with col2:
                                    if st.button(f"Restore", key=f"restore_{backup.get('name')}"):
                                        try:
                                            restore_result = await agent.tool_registry.execute_tool(
                                                "restore_backup", 
                                                {"backup_name": backup.get('name')}
                                            )
                                            
                                            if restore_result.get("success"):
                                                st.success("✅ Backup restored successfully!")
                                            else:
                                                st.error(f"❌ Failed to restore: {restore_result.get('error')}")
                                                
                                        except Exception as e:
                                            st.error(f"Error restoring backup: {e}")
                    else:
                        st.info("No backups found.")
                else:
                    st.error(f"Failed to list backups: {result.get('error')}")
                    
            except Exception as e:
                st.error(f"Error listing backups: {e}")
    
    with tab4:
        st.subheader("Backup Configuration")
        
        # Get current configuration
        if st.button("Load Current Configuration"):
            try:
                result = await agent.tool_registry.execute_tool("get_backup_config", {})
                
                if result.get("success"):
                    config = result.get("config", {})
                    st.session_state.backup_config = config
                    st.success("✅ Configuration loaded!")
                    st.json(config)
                else:
                    st.error(f"Failed to get configuration: {result.get('error')}")
                    
            except Exception as e:
                st.error(f"Error getting configuration: {e}")
        
        # Configuration editor
        if "backup_config" in st.session_state:
            st.subheader("Edit Configuration")
            
            config = st.session_state.backup_config
            
            # Basic settings
            enabled = st.checkbox("Enable Automatic Backups", value=config.get("enabled", True))
            interval = st.selectbox("Backup Interval", 
                                   ["hourly", "daily", "weekly"], 
                                   index=["hourly", "daily", "weekly"].index(config.get("auto_backup_interval", "daily")))
            max_backups = st.number_input("Maximum Backups to Keep", 
                                        value=config.get("max_backups", 30), 
                                        min_value=1, max_value=100)
            compress = st.checkbox("Compress Backups", value=config.get("compress", True))
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                include_patterns = st.text_area("Include Patterns (one per line)", 
                                               value="\n".join(config.get("include_patterns", [])))
                exclude_patterns = st.text_area("Exclude Patterns (one per line)", 
                                               value="\n".join(config.get("exclude_patterns", [])))
            
            if st.button("Update Configuration"):
                try:
                    new_config = {
                        "enabled": enabled,
                        "auto_backup_interval": interval,
                        "max_backups": max_backups,
                        "compress": compress,
                        "include_patterns": include_patterns.split("\n") if include_patterns else [],
                        "exclude_patterns": exclude_patterns.split("\n") if exclude_patterns else []
                    }
                    
                    result = await agent.tool_registry.execute_tool(
                        "update_backup_config", 
                        {"config": json.dumps(new_config)}
                    )
                    
                    if result.get("success"):
                        st.success("✅ Configuration updated successfully!")
                        st.session_state.backup_config = new_config
                    else:
                        st.error(f"❌ Failed to update configuration: {result.get('error')}")
                        
                except Exception as e:
                    st.error(f"Error updating configuration: {e}")
        
        # Auto backup controls
        st.subheader("Auto Backup Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Auto Backup"):
                try:
                    result = await agent.tool_registry.execute_tool("start_auto_backup", {})
                    
                    if result.get("success"):
                        st.success("✅ Auto backup started!")
                    else:
                        st.error(f"❌ Failed to start: {result.get('error')}")
                        
                except Exception as e:
                    st.error(f"Error starting auto backup: {e}")
        
        with col2:
            if st.button("⏹️ Stop Auto Backup"):
                try:
                    result = await agent.tool_registry.execute_tool("stop_auto_backup", {})
                    
                    if result.get("success"):
                        st.success("✅ Auto backup stopped!")
                    else:
                        st.error(f"❌ Failed to stop: {result.get('error')}")
                        
                except Exception as e:
                    st.error(f"Error stopping auto backup: {e}")

def main():
    """Main tool agent interface"""
    st.title("🛠️ Tool Agent - Interactive Tool Testing")
    st.markdown("Test and execute tools from loaded plugins interactively.")
    
    # Simple error handling and graceful degradation
    try:
        # Initialize agent
        agent = get_agent()
        if not agent:
            st.error("Failed to initialize agent. Please check the configuration.")
            st.info("This could be due to missing dependencies or configuration issues.")
            return

        # Show basic agent info
        st.success("✅ Agent initialized successfully!")
        
        # Add simple tabs for now
        main_tab, status_tab = st.tabs(["🛠️ Tool Testing", "� System Status"])
        
        with main_tab:
            original_main_content(agent)
        
        with status_tab:
            display_system_status(agent)
            
    except Exception as e:
        st.error(f"Error in Tool Agent: {e}")
        st.info("Please check the logs for more details.")
        
        with st.expander("Error Details"):
            st.code(str(e))


def display_system_status(agent):
    """Display basic system status without complex async operations"""
    st.header("📊 System Status")
    
    # Add reload controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reload Page Cache", help="Clear cached agent and force reload"):
            st.cache_resource.clear()
            st.rerun()
    
    with col2:
        if st.button("🔄 Reinitialize Plugins", help="Force plugin reinitialization"):
            if agent:
                try:
                    # Reset initialization state
                    agent.plugins_initialized = False
                    success = run_async_safely(agent.initialize_plugins())
                    if success:
                        st.success("✅ Plugins reinitialized successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Plugin reinitialization failed")
                except Exception as e:
                    st.error(f"Error reinitializing plugins: {e}")
    
    try:
        # Debug agent structure
        st.subheader("🔍 Agent Debug Information")
        
        agent_attrs = [attr for attr in dir(agent) if not attr.startswith('_')]
        st.write(f"**Agent attributes:** {', '.join(agent_attrs[:10])}...")
        
        # Check if plugin manager is available
        if hasattr(agent, 'plugin_manager'):
            st.success("✅ Plugin Manager: Available")
            
            # Debug plugin manager
            pm_attrs = [attr for attr in dir(agent.plugin_manager) if not attr.startswith('_')]
            st.write(f"**Plugin Manager attributes:** {', '.join(pm_attrs[:10])}...")
            
            # Try to get basic plugin info
            try:
                if hasattr(agent.plugin_manager, 'get_loaded_plugins'):
                    plugins = agent.plugin_manager.get_loaded_plugins()
                    st.metric("Loaded Plugins", len(plugins))
                    
                    if plugins:
                        st.subheader("Plugin List")
                        for name, plugin in plugins.items():
                            if hasattr(plugin, 'metadata'):
                                st.write(f"• **{name}**: {plugin.metadata.description}")
                            else:
                                st.write(f"• **{name}**: (no metadata)")
                    else:
                        st.info("No plugins are currently loaded.")
                elif hasattr(agent.plugin_manager, '_loaded_plugins'):
                    plugins = agent.plugin_manager._loaded_plugins
                    st.metric("Loaded Plugins", len(plugins))
                    
                    if plugins:
                        st.subheader("Plugin List")
                        for name, plugin in plugins.items():
                            if hasattr(plugin, 'metadata'):
                                st.write(f"• **{name}**: {plugin.metadata.description}")
                            else:
                                st.write(f"• **{name}**: (no metadata)")
                    else:
                        st.info("No plugins are currently loaded.")
                else:
                    st.warning("Plugin manager has no accessible plugins attribute")
                        
            except Exception as e:
                st.warning(f"Cannot access plugin details: {e}")
        else:
            st.warning("⚠️ Plugin Manager: Not Available")
            
        # Check if tool registry is available
        if hasattr(agent, 'tool_registry'):
            st.success("✅ Tool Registry: Available")
            
            try:
                tools = agent.tool_registry.get_all_tools()
                st.metric("Available Tools", len(tools))
                
                if tools:
                    st.subheader("Tool Registry Tools")
                    for name, tool in list(tools.items())[:5]:  # Show first 5
                        st.write(f"• **{name}**: {tool.description}")
                        
            except Exception as e:
                st.warning(f"Cannot access tool registry: {e}")
        else:
            st.warning("⚠️ Tool Registry: Not Available")
            
        # Check plugin manager tool registry
        if hasattr(agent, 'plugin_manager') and hasattr(agent.plugin_manager, 'tool_registry'):
            st.success("✅ Plugin Manager Tool Registry: Available")
            
            try:
                pm_tools = agent.plugin_manager.tool_registry.get_all_tools()
                st.metric("Plugin Manager Tools", len(pm_tools))
                
                if pm_tools:
                    st.subheader("Plugin Manager Tools")
                    for name, tool in list(pm_tools.items())[:5]:  # Show first 5
                        st.write(f"• **{name}**: {tool.description}")
                        
            except Exception as e:
                st.warning(f"Cannot access plugin manager tool registry: {e}")
        else:
            st.warning("⚠️ Plugin Manager Tool Registry: Not Available")
            
    except Exception as e:
        st.error(f"Error checking system status: {e}")
        
        with st.expander("Debug Exception Details"):
            import traceback
            st.code(traceback.format_exc())

def original_main_content(agent):
    """Unified main content for tool testing using Plugin Manager's tool registry"""
    # Ensure plugins are initialized
    with st.spinner("Initializing plugin system..."):
        try:
            if hasattr(agent, 'initialize_plugins') and not getattr(agent, 'plugins_initialized', False):
                # Use async utilities for safe initialization
                success = run_async_safely(agent.initialize_plugins())
                if success:
                    st.success("✅ Plugin system initialized successfully!")
                else:
                    st.warning("⚠️ Plugin initialization completed with warnings")
            else:
                st.success("✅ Plugin system ready!")
        except Exception as e:
            st.error(f"Plugin initialization failed: {e}")
            st.info("Some features may not be available.")
            return

    # Always use the plugin manager's tool registry as the unified source
    tools = {}
    try:
        if hasattr(agent, 'plugin_manager') and hasattr(agent.plugin_manager, 'tool_registry'):
            tools = agent.plugin_manager.tool_registry.get_all_tools()
            st.success(f"✅ Loaded {len(tools)} tools from Plugin Manager's tool registry")
        else:
            st.warning("⚠️ Plugin Manager or its tool registry not available")
            return
    except Exception as e:
        st.error(f"Failed to load tools: {e}")
        return

    if not tools:
        st.warning("No tools are currently available.")
        st.info("Please ensure plugins are properly configured and loaded.")
        return

    st.header("Available Tools")
    tool_names = list(tools.keys())
    selected_tool_name = st.selectbox("Select a tool:", ["Select a tool..."] + tool_names)
    if selected_tool_name and selected_tool_name != "Select a tool...":
        selected_tool = tools[selected_tool_name]
        st.subheader(f"🛠️ {selected_tool.name}")
        st.write(f"**Description:** {selected_tool.description}")
        st.write(f"**Plugin:** {selected_tool.plugin_name}")
        st.write(f"**Category:** {selected_tool.category}")
        st.write("**Parameters:**")
        parameters = {}
        if hasattr(selected_tool, 'parameters') and selected_tool.parameters:
            for param in selected_tool.parameters:
                param_type = getattr(param.type, 'value', 'string')
                param_label = f"{param.name} {'(required)' if param.required else '(optional)'}"
                if param_type == "string":
                    value = st.text_input(param_label, help=param.description)
                    if value or not param.required:
                        parameters[param.name] = value
                elif param_type == "boolean":
                    value = st.checkbox(param_label, help=param.description)
                    parameters[param.name] = value
                elif param_type in ["integer", "number"]:
                    value = st.number_input(param_label, help=param.description)
                    parameters[param.name] = value
                else:
                    value = st.text_input(param_label, help=param.description)
                    if value or not param.required:
                        parameters[param.name] = value
            if st.button(f"🚀 Execute {selected_tool.name}", use_container_width=True):
                with st.spinner(f"Executing {selected_tool.name}..."):
                    try:
                        # Use the plugin manager's tool execution method if available
                        result = None
                        if hasattr(agent, 'plugin_manager') and hasattr(agent.plugin_manager, 'tool_registry'):
                            exec_method = getattr(agent.plugin_manager.tool_registry, 'execute_tool', None)
                            if callable(exec_method):
                                # Use local async utilities for safe execution
                                result = run_async_safely(exec_method(selected_tool.name, parameters))
                            else:
                                # Fallback to direct function call
                                result = selected_tool.function(**parameters)
                        else:
                            result = selected_tool.function(**parameters)
                        st.success("✅ Tool executed successfully!")
                        if result is not None:
                            if isinstance(result, (dict, list)):
                                st.json(result)
                            else:
                                st.code(str(result))
                        else:
                            st.info("Tool executed but returned no result.")
                    except Exception as e:
                        st.error(f"❌ Tool execution failed: {e}")
                        with st.expander("Error Details"):
                            import traceback
                            st.code(traceback.format_exc())
        else:
            st.info("This tool has no parameters.")
            if st.button(f"🚀 Execute {selected_tool.name}", use_container_width=True):
                with st.spinner(f"Executing {selected_tool.name}..."):
                    try:
                        result = None
                        if hasattr(agent, 'plugin_manager') and hasattr(agent.plugin_manager, 'tool_registry'):
                            exec_method = getattr(agent.plugin_manager.tool_registry, 'execute_tool', None)
                            if callable(exec_method):
                                result = run_async_safely(exec_method(selected_tool.name, {}))
                            else:
                                result = selected_tool.function()
                        else:
                            result = selected_tool.function()
                        st.success("✅ Tool executed successfully!")
                        if result is not None:
                            if isinstance(result, (dict, list)):
                                st.json(result)
                            else:
                                st.code(str(result))
                        else:
                            st.info("Tool executed but returned no result.")
                    except Exception as e:
                        st.error(f"❌ Tool execution failed: {e}")
                        with st.expander("Error Details"):
                            import traceback
                            st.code(traceback.format_exc())

# Execute the main function when the script is run
if __name__ == "__main__":
    main()
else:
    # For Streamlit pages, execute main directly in Streamlit context
    main()

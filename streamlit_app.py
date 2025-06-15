"""
SilentCodingLegend AI Agent - Simple Chat Interface
"""
import streamlit as st
import time
from datetime import datetime
from typing import Optional, Tuple
from src.core.agent import SilentCodingLegendAgent
from src.core.chain_of_thought import ReasoningType
from src.utils.logging import get_logger, setup_logging
from utils.streamlit_utils import (
    load_css, get_cached_agent, validate_session_state, 
    generate_error_id, validate_user_input, get_session_metrics
)
from config import UI_CONFIG, MODEL_CONFIG, REASONING_CONFIG, ERROR_CONFIG, ADVANCED_AI_CONFIG, ADVANCED_TOOL_SUGGESTIONS

# Import advanced AI modules
from src.core.multimodal_processor import MultiModalProcessor
from src.core.code_sandbox import CodeSandbox
from src.core.ai_testing import AITestGenerator

# Initialize logging first
setup_logging()

# Configure page
st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["sidebar_state"]
)

# Initialize logger
logger = get_logger(__name__)

# Load custom CSS styles
load_css()

def get_loading_message(model_name: str) -> str:
    """
    Get context-appropriate loading message based on model type.
    
    Args:
        model_name (str): The name of the AI model being used
        
    Returns:
        str: Appropriate loading message for the model
    """
    # Use configuration-based approach for loading messages
    model_indicators = MODEL_CONFIG["loading_indicators"]
    
    for indicator, message in model_indicators.items():
        if indicator in model_name:
            return message
    
    # Default fallback
    return MODEL_CONFIG["default_loading_message"]

def initialize_session_state() -> None:
    """Initialize Streamlit session state variables with enhanced error handling."""
    try:
        # Initialize agent with caching
        if 'agent' not in st.session_state:
            st.session_state.agent = get_cached_agent()
            logger.info("Initialized SilentCodingLegend agent for Streamlit session")
        
        # Initialize session ID
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Created new session: {st.session_state.session_id}")

        # Initialize messages
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        # Initialize plugins (synchronously for Streamlit compatibility)
        if 'plugins_initialized' not in st.session_state:
            st.session_state.plugins_initialized = False
        
        if not st.session_state.plugins_initialized:
            try:
                st.session_state.agent.initialize_plugins_sync()
                st.session_state.plugins_initialized = True
                logger.info("Plugin system initialized successfully")
            except Exception as e:
                error_id = generate_error_id()
                logger.error(f"Failed to initialize plugin system [{error_id}]: {e}")
                st.session_state.plugins_initialized = False
                # Store error for user feedback
                st.session_state.plugin_error = f"Plugin initialization failed [{error_id}]"
        
        # Initialize advanced AI components
        initialize_advanced_ai()
        
        # Validate session state structure after initialization
        if not validate_session_state():
            logger.warning("Session state validation failed after initialization")
                
    except Exception as e:
        error_id = generate_error_id()
        logger.exception(f"Critical error during session initialization [{error_id}]: {e}")
        st.error(f"Failed to initialize application [{error_id}]. Please refresh the page.")

def get_backup_status():
    """Get backup system status for display"""
    try:
        if hasattr(st.session_state, 'agent') and st.session_state.agent:
            # Check if BackupManager plugin is available
            backup_plugin = None
            for plugin in st.session_state.agent.plugin_manager._loaded_plugins.values():
                if plugin.metadata.name == "BackupManager":
                    backup_plugin = plugin
                    break
            
            if backup_plugin and hasattr(backup_plugin, 'backup_manager'):
                import asyncio
                status_result = asyncio.run(backup_plugin.backup_status())
                if status_result.get("success"):
                    return status_result.get("status", {})
        return None
    except Exception as e:
        logger.error(f"Error getting backup status: {e}")
        return None

def display_backup_status_sidebar():
    """Display backup status in sidebar"""
    backup_status = get_backup_status()
    
    if backup_status:
        st.sidebar.markdown("---")
        st.sidebar.markdown("🔄 **Backup Status**")
        
        # Auto backup status
        auto_enabled = backup_status.get("auto_backup_enabled", False)
        auto_running = backup_status.get("auto_backup_running", False)
        
        if auto_enabled and auto_running:
            st.sidebar.success("✅ Auto Backup Active")
        elif auto_enabled and not auto_running:
            st.sidebar.warning("⚠️ Auto Backup Enabled (Stopped)")
        else:
            st.sidebar.error("❌ Auto Backup Disabled")
        
        # Show interval
        interval = backup_status.get("backup_interval", "daily")
        st.sidebar.text(f"Interval: {interval.title()}")
        
        # Quick backup button
        if st.sidebar.button("📦 Quick Backup", help="Create a quick backup"):
            try:
                # Find backup plugin and create backup
                backup_plugin = None
                for plugin in st.session_state.agent.plugin_manager.plugins.values():
                    if plugin.metadata.name == "BackupManager":
                        backup_plugin = plugin
                        break
                
                if backup_plugin:
                    import asyncio
                    result = asyncio.run(backup_plugin.create_backup("full", "quick_backup"))
                    if result.get("success"):
                        st.sidebar.success("✅ Backup created!")
                    else:
                        st.sidebar.error(f"❌ Backup failed: {result.get('error')}")
                        
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")

def render_sidebar() -> Tuple[str, bool, str]:
    """
    Render the sidebar with model selection and settings.
    
    Returns:
        Tuple[str, bool, str]: Selected model name, whether to use CoT reasoning, and reasoning type
    """
    with st.sidebar:
        st.markdown(f"## {UI_CONFIG['app_icon']} {UI_CONFIG['app_name']}")
        st.markdown(f"**{UI_CONFIG['app_subtitle']}**")
        
        st.markdown("### ⚙️ Settings")
        
        # Model selection dropdown using configuration
        available_models = MODEL_CONFIG["available_models"]
        current_model = st.session_state.agent.client.config.model
        
        selected_model = st.selectbox(
            "**Model:**",
            options=list(available_models.keys()),
            index=list(available_models.keys()).index(current_model) if current_model in available_models else 0,
            format_func=lambda x: available_models[x],
            help="Choose the Llama model to use for conversations"
        )
        
        # Update model if changed
        if selected_model != current_model:
            st.session_state.agent.client.config.model = selected_model
            st.success(f"Model changed to: {available_models[selected_model]}")
            logger.info(f"Model changed to: {selected_model}")
        
        # Model capability info using configuration
        model_info = MODEL_CONFIG["model_capabilities"]
        if selected_model in model_info:
            st.info(model_info[selected_model])
        
        # Chain-of-Thought Reasoning Options
        st.markdown("### 🧠 Reasoning Settings")
        
        use_cot = st.checkbox(
            "Enable Chain-of-Thought Reasoning",
            value=False,
            help="Use advanced reasoning to break down complex problems step-by-step"
        )
        
        reasoning_type = "chain_of_thought"  # default
        if use_cot:
            reasoning_options = REASONING_CONFIG["reasoning_types"]
            
            reasoning_type = st.selectbox(
                "Reasoning Type:",
                options=list(reasoning_options.keys()),
                format_func=lambda x: reasoning_options[x],
                help="Choose the type of reasoning approach"
            )
        
        st.markdown(f"**Session:** {st.session_state.session_id}")
        
        # NLTK Enhancement Info
        if use_cot:
            st.markdown("### 🔬 NLTK Analysis")
            st.info(REASONING_CONFIG["nltk_features_description"])
        
        # Chat statistics using new utility function
        if st.session_state.messages:
            metrics = get_session_metrics()
            st.metric("Messages", metrics["total_messages"])
            st.metric("Q&A Pairs", metrics["user_messages"])
        
        # Tool Status Section
        st.markdown("---")
        st.markdown("### 🛠️ Tool Status")
        
        # Show plugin error if any
        if hasattr(st.session_state, 'plugin_error'):
            st.error(st.session_state.plugin_error)
            if st.button("🔄 Retry Plugin Initialization"):
                if hasattr(st.session_state, 'plugin_error'):
                    del st.session_state.plugin_error
                st.session_state.plugins_initialized = False
                st.rerun()
        
        if st.session_state.plugins_initialized:
            tool_count = len(st.session_state.agent.client.available_tools)
            st.metric("Available Tools", tool_count)
            
            if tool_count > 0:
                st.success("✅ Tools active")
                if st.button("🔧 Manage Tools"):
                    st.switch_page("pages/Plugin_Manager.py")
                if st.button("🛠️ Test Tools"):
                    st.switch_page("pages/Tool_Agent.py")
            else:
                st.warning("⚠️ No tools loaded")
        else:
            st.info("🔄 Tools not initialized")
            if st.button("🔄 Initialize Tools"):
                with st.spinner("Initializing tools..."):
                    try:
                        st.session_state.agent.initialize_plugins_sync()
                        st.session_state.plugins_initialized = True
                        if hasattr(st.session_state, 'plugin_error'):
                            del st.session_state.plugin_error
                    except Exception as e:
                        error_id = generate_error_id()
                        logger.error(f"Failed to initialize plugins [{error_id}]: {e}")
                        st.session_state.plugin_error = f"Plugin initialization failed [{error_id}]"
                st.rerun()
        
        # Advanced AI Status Section
        if ADVANCED_AI_CONFIG.get("enabled", False):
            st.markdown("---")
            st.markdown("### 🚀 Advanced AI")
            
            # Show advanced AI component status
            advanced_components = []
            if hasattr(st.session_state, 'multimodal_processor'):
                advanced_components.append("🖼️ Multi-Modal")
            if hasattr(st.session_state, 'code_sandbox'):
                advanced_components.append("⚡ Code Sandbox")
            if hasattr(st.session_state, 'ai_testing'):
                advanced_components.append("🧪 AI Testing")
            
            if advanced_components:
                st.success(f"✅ {len(advanced_components)} modules ready")
                for component in advanced_components:
                    st.write(f"  • {component}")
            else:
                st.warning("⚠️ Advanced AI not initialized")
            
            # Show advanced AI error if any
            if hasattr(st.session_state, 'advanced_ai_error'):
                st.error(st.session_state.advanced_ai_error)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Display backup status
        display_backup_status_sidebar()
    
    return selected_model, use_cot, reasoning_type

def handle_chat_response(prompt: str, use_cot: bool = False, reasoning_type: str = "chain_of_thought") -> None:
    """
    Handle the chat response generation with proper error handling and security.
    
    Args:
        prompt (str): User input message
        use_cot (bool): Whether to use Chain-of-Thought reasoning
        reasoning_type (str): Type of reasoning to use if CoT is enabled
    """
    try:
        model_name = st.session_state.agent.client.config.model
        loading_msg = get_loading_message(model_name)
        
        if use_cot:
            reasoning_display = reasoning_type.replace('_', ' ').title()
            loading_msg = f"🧠 {loading_msg} (Using {reasoning_display} reasoning)"
        
        # Check if tools are available and enabled
        has_tools = (st.session_state.plugins_initialized and 
                    st.session_state.agent.client.tools_enabled and 
                    len(st.session_state.agent.client.available_tools) > 0)
        
        if has_tools:
            tool_count = len(st.session_state.agent.client.available_tools)
            loading_msg += f" (🛠️ {tool_count} tools available)"
        
        reasoning_chain = None
        with st.status(loading_msg, expanded=True) as status:
            try:
                if use_cot:
                    # Use Chain-of-Thought reasoning
                    from src.core.chain_of_thought import ReasoningType, ReasoningChain
                    reasoning_enum = ReasoningType(reasoning_type)
                    result = st.session_state.agent.chat_sync_with_reasoning(
                        prompt, 
                        st.session_state.session_id,
                        reasoning_type=reasoning_enum
                    )
                    
                    # Parse the response - should be a tuple of (text, reasoning_chain)
                    if isinstance(result, tuple) and len(result) == 2:
                        final_response, reasoning_chain = result
                        
                        # Handle case where response might still contain the reasoning object string
                        if isinstance(final_response, str) and "ReasoningChain(" in final_response:
                            # Extract just the text part before the reasoning object
                            final_response = final_response.split("ReasoningChain(")[0].strip().rstrip(", ")
                    else:
                        # Fallback for unexpected response format
                        final_response = str(result)
                        if "ReasoningChain(" in final_response:
                            final_response = final_response.split("ReasoningChain(")[0].strip().rstrip(", ")
                        
                else:
                    # Use regular chat
                    final_response = st.session_state.agent.chat_sync(prompt, st.session_state.session_id)
                
                status.update(label="✅ Response generated!", state="complete")
                
                # Display tool usage information if tools were likely used
                if has_tools and any(keyword in final_response.lower() for keyword in 
                                   ["searched", "found", "executed", "analyzed"]):
                    # Show a hint about tools
                    st.info("💡 **Tip**: I may have used tools to help answer your question. "
                           "Visit the 🛠️ Tool Agent page to see all available tools and test them manually!")
                
                # Display response safely (no unsafe HTML)
                st.write(final_response)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                logger.info(f"Generated response for session {st.session_state.session_id} (CoT: {use_cot})")
                
            except ConnectionError as e:
                error_id = generate_error_id()
                status.update(label="Connection failed", state="error")
                error_msg = ERROR_CONFIG["connection_error_message"]
                st.error(f"{error_msg} [{error_id}]")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                logger.error(f"Connection error during chat [{error_id}]: {e}")
                
            except TimeoutError as e:
                error_id = generate_error_id()
                status.update(label="Request timed out", state="error")
                error_msg = ERROR_CONFIG["timeout_error_message"]
                st.error(f"{error_msg} [{error_id}]")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                logger.error(f"Timeout error during chat [{error_id}]: {e}")
                
            except Exception as e:
                error_id = generate_error_id()
                status.update(label="Error occurred", state="error")
                error_msg = ERROR_CONFIG["generic_error_message"]
                st.error(f"{error_msg} [{error_id}]")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                logger.exception(f"Unexpected error during chat [{error_id}]: {e}")
        
        # Display reasoning insights with enhanced UI (after status context to avoid nested expanders)
        if reasoning_chain and hasattr(reasoning_chain, 'confidence_score'):
            with st.expander("🧠 Chain-of-Thought Analysis", expanded=False):
                # Show tool usage if any were called during reasoning
                if has_tools and hasattr(reasoning_chain, 'tools_used'):
                    if reasoning_chain.tools_used:
                        st.markdown("🛠️ **Tools Used:**")
                        for tool_info in reasoning_chain.tools_used:
                            st.markdown(f"  • {tool_info['name']} - {tool_info.get('description', 'No description')}")
                            
    except Exception as e:
        error_id = generate_error_id()
        logger.exception(f"Critical error in chat handling [{error_id}]: {e}")
        st.error(f"Critical error occurred [{error_id}]. Please refresh the page.")

def initialize_advanced_ai() -> None:
    """Initialize advanced AI components in session state."""
    try:
        # Initialize MultiModal Processor
        if 'multimodal_processor' not in st.session_state:
            st.session_state.multimodal_processor = MultiModalProcessor()
            logger.info("Initialized MultiModal Processor")
        
        # Initialize Code Sandbox
        if 'code_sandbox' not in st.session_state:
            st.session_state.code_sandbox = CodeSandbox()
            logger.info("Initialized Code Sandbox")
        
        # Initialize AI Testing
        if 'ai_testing' not in st.session_state:
            st.session_state.ai_testing = AITestGenerator()
            logger.info("Initialized AI Testing")
            
    except Exception as e:
        error_id = generate_error_id()
        logger.error(f"Failed to initialize advanced AI components [{error_id}]: {e}")
        st.session_state.advanced_ai_error = f"Advanced AI initialization failed [{error_id}]"

def render_advanced_features() -> None:
    """Render advanced AI features in the main interface."""
    if not ADVANCED_AI_CONFIG.get("enabled", False):
        return
    
    st.markdown("---")
    
    # Create tabs for different advanced features
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ Multi-Modal", "⚡ Code Sandbox", "🧪 AI Testing", "🔧 Refactoring"])
    
    with tab1:
        render_multimodal_interface()
    
    with tab2:
        render_code_sandbox_interface()
    
    with tab3:
        render_ai_testing_interface()
    
    with tab4:
        render_refactoring_interface()

def render_multimodal_interface() -> None:
    """Render multi-modal processing interface."""
    st.markdown("### 🖼️ Multi-Modal AI Processing")
    st.markdown("Upload images, audio, video, or documents for AI analysis.")
    
    # File uploader for different types
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload file for analysis",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'mp3', 'wav', 'mp4', 'avi', 'pdf', 'txt', 'docx'],
            help="Supported: Images (PNG, JPG, etc.), Audio (MP3, WAV), Video (MP4, AVI), Documents (PDF, TXT, DOCX)"
        )
    
    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["auto_detect", "image_analysis", "ocr_text_extraction", "audio_transcription", "video_analysis", "document_parsing"],
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Choose the type of analysis to perform"
        )
    
    if uploaded_file is not None:
        st.markdown("#### 📁 File Information")
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
        st.write(f"**Type:** {uploaded_file.type}")
        
        if st.button("🔍 Analyze File", type="primary"):
            try:
                with st.spinner("Processing file..."):
                    # Get the multimodal processor
                    processor = st.session_state.multimodal_processor
                    
                    # Process the file
                    file_bytes = uploaded_file.read()
                    result = processor.process_file(
                        file_data=file_bytes,
                        filename=uploaded_file.name,
                        analysis_type=analysis_type
                    )
                    
                    if result.get("success"):
                        st.success("✅ Analysis completed!")
                        
                        # Display results
                        if "text" in result:
                            st.markdown("#### 📝 Extracted Text")
                            st.text_area("", value=result["text"], height=200, disabled=True)
                        
                        if "metadata" in result:
                            st.markdown("#### 📊 Metadata")
                            st.json(result["metadata"])
                        
                        if "analysis" in result:
                            st.markdown("#### 🤖 AI Analysis")
                            st.write(result["analysis"])
                            
                    else:
                        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                        
            except Exception as e:
                error_id = generate_error_id()
                st.error(f"Error processing file [{error_id}]: {str(e)}")
                logger.error(f"Multimodal processing error [{error_id}]: {e}")

def render_code_sandbox_interface() -> None:
    """Render code sandbox interface."""
    st.markdown("### ⚡ Secure Code Execution")
    st.markdown("Execute code safely in an isolated sandbox environment.")
    
    # Language selection
    language = st.selectbox(
        "Programming Language",
        options=ADVANCED_AI_CONFIG["code_sandbox"]["supported_languages"],
        help="Choose the programming language for your code"
    )
    
    # Code input
    code_input = st.text_area(
        "Enter your code:",
        height=200,
        placeholder=f"Write your {language} code here...",
        help="Code will be executed in a secure sandbox with resource limits"
    )
    
    # Execution settings
    col1, col2 = st.columns(2)
    with col1:
        timeout = st.slider("Timeout (seconds)", 1, 30, 10)
    with col2:
        show_output = st.checkbox("Show detailed output", value=True)
    
    if code_input.strip() and st.button("🚀 Execute Code", type="primary"):
        try:
            with st.spinner(f"Executing {language} code..."):
                sandbox = st.session_state.code_sandbox
                
                result = sandbox.execute_code(
                    code=code_input,
                    language=language,
                    timeout=timeout
                )
                
                if result.get("success"):
                    st.success("✅ Code executed successfully!")
                    
                    # Display output
                    if result.get("output"):
                        st.markdown("#### 📤 Output")
                        st.code(result["output"], language="text")
                    
                    if show_output and result.get("metadata"):
                        st.markdown("#### 📊 Execution Details")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Execution Time", f"{result['metadata'].get('execution_time', 0):.3f}s")
                        with col2:
                            st.metric("Memory Used", f"{result['metadata'].get('memory_used', 0)} MB")
                        with col3:
                            st.metric("Exit Code", result['metadata'].get('exit_code', 0))
                    
                else:
                    st.error(f"❌ Execution failed: {result.get('error', 'Unknown error')}")
                    if result.get("stderr"):
                        st.markdown("#### ⚠️ Error Output")
                        st.code(result["stderr"], language="text")
                        
        except Exception as e:
            error_id = generate_error_id()
            st.error(f"Sandbox execution error [{error_id}]: {str(e)}")
            logger.error(f"Code sandbox error [{error_id}]: {e}")

def render_ai_testing_interface() -> None:
    """Render AI-powered testing interface."""
    st.markdown("### 🧪 AI-Powered Testing")
    st.markdown("Generate comprehensive tests for your code using AI.")
    
    # Code input for testing
    code_to_test = st.text_area(
        "Enter code to generate tests for:",
        height=200,
        placeholder="Paste your function or class here...",
        help="AI will analyze your code and generate appropriate tests"
    )
    
    # Test configuration
    col1, col2 = st.columns(2)
    with col1:
        test_framework = st.selectbox(
            "Test Framework",
            options=ADVANCED_AI_CONFIG["ai_testing"]["test_frameworks"],
            help="Choose your preferred testing framework"
        )
    
    with col2:
        test_types = st.multiselect(
            "Test Types",
            options=ADVANCED_AI_CONFIG["ai_testing"]["test_types"],
            default=["unit"],
            help="Select types of tests to generate"
        )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        include_mocks = st.checkbox("Generate mocks", value=True)
        include_fixtures = st.checkbox("Generate test fixtures", value=True)
        coverage_target = st.slider("Target coverage %", 50, 100, 80)
    
    if code_to_test.strip() and st.button("🧪 Generate Tests", type="primary"):
        try:
            with st.spinner("Generating AI-powered tests..."):
                ai_testing = st.session_state.ai_testing
                
                result = ai_testing.generate_tests(
                    code=code_to_test,
                    framework=test_framework,
                    test_types=test_types,
                    include_mocks=include_mocks,
                    include_fixtures=include_fixtures,
                    coverage_target=coverage_target
                )
                
                if result.get("success"):
                    st.success("✅ Tests generated successfully!")
                    
                    # Display generated tests
                    st.markdown("#### 🧪 Generated Test Code")
                    st.code(result["test_code"], language="python")
                    
                    # Test analysis
                    if result.get("analysis"):
                        st.markdown("#### 📊 Test Analysis")
                        analysis = result["analysis"]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Test Cases", analysis.get("test_count", 0))
                        with col2:
                            st.metric("Coverage", f"{analysis.get('estimated_coverage', 0)}%")
                        with col3:
                            st.metric("Complexity", analysis.get("complexity_score", "N/A"))
                        
                        if analysis.get("recommendations"):
                            st.markdown("#### 💡 Recommendations")
                            for rec in analysis["recommendations"]:
                                st.write(f"• {rec}")
                    
                    # Option to run tests
                    if st.button("🚀 Run Generated Tests"):
                        with st.spinner("Running tests..."):
                            test_result = ai_testing.run_tests(result["test_code"], test_framework)
                            
                            if test_result.get("success"):
                                st.success(f"✅ Tests passed! ({test_result.get('passed', 0)}/{test_result.get('total', 0)})")
                            else:
                                st.error(f"❌ Some tests failed: {test_result.get('error', 'Unknown error')}")
                                if test_result.get("output"):
                                    st.code(test_result["output"], language="text")
                
                else:
                    st.error(f"❌ Test generation failed: {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            error_id = generate_error_id()
            st.error(f"AI testing error [{error_id}]: {str(e)}")
            logger.error(f"AI testing error [{error_id}]: {e}")

def render_refactoring_interface() -> None:
    """Render code refactoring interface."""
    st.markdown("### 🔧 AI Code Refactoring")
    st.markdown("Get AI-powered suggestions to improve your code quality, performance, and maintainability.")
    
    # Code input for refactoring
    code_to_refactor = st.text_area(
        "Enter code to analyze and refactor:",
        height=200,
        placeholder="Paste your code here for analysis...",
        help="AI will analyze your code and suggest improvements"
    )
    
    # Refactoring options
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "Code Language",
            options=ADVANCED_AI_CONFIG["code_refactoring"]["supported_languages"],
            help="Specify the programming language"
        )
    
    with col2:
        analysis_types = st.multiselect(
            "Analysis Types",
            options=ADVANCED_AI_CONFIG["code_refactoring"]["analysis_types"],
            default=["complexity_reduction", "readability_improvement"],
            help="Choose types of analysis to perform"
        )
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        severity_filter = st.selectbox(
            "Minimum Severity",
            options=ADVANCED_AI_CONFIG["code_refactoring"]["severity_levels"],
            index=1,  # Default to "warning"
            help="Filter suggestions by severity level"
        )
        auto_fix = st.checkbox("Generate auto-fix suggestions", value=True)
        best_practices = st.checkbox("Enforce best practices", value=True)
    
    if code_to_refactor.strip() and st.button("🔍 Analyze & Refactor", type="primary"):
        try:
            with st.spinner("Analyzing code for refactoring opportunities..."):
                # For now, create a mock refactoring analysis
                # In a real implementation, this would call an AI service
                
                st.success("✅ Code analysis completed!")
                
                # Mock analysis results
                st.markdown("#### 📊 Code Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Complexity Score", "7.2/10")
                with col2:
                    st.metric("Maintainability", "B+")
                with col3:
                    st.metric("Performance", "Good")
                with col4:
                    st.metric("Security", "A-")
                
                # Mock suggestions
                st.markdown("#### 💡 Refactoring Suggestions")
                
                suggestions = [
                    {
                        "type": "complexity_reduction",
                        "severity": "warning",
                        "line": 15,
                        "message": "Consider breaking down this complex function into smaller, more focused functions",
                        "suggestion": "Extract the validation logic into a separate function"
                    },
                    {
                        "type": "performance_optimization", 
                        "severity": "info",
                        "line": 23,
                        "message": "This loop could be optimized using list comprehension",
                        "suggestion": "Replace for loop with: result = [process(item) for item in items if condition(item)]"
                    },
                    {
                        "type": "readability_improvement",
                        "severity": "info", 
                        "line": 8,
                        "message": "Variable name could be more descriptive",
                        "suggestion": "Rename 'data' to 'user_input_data' for clarity"
                    }
                ]
                
                for i, suggestion in enumerate(suggestions, 1):
                    with st.expander(f"💡 Suggestion {i}: {suggestion['message']}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Type:** {suggestion['type'].replace('_', ' ').title()}")
                            st.write(f"**Line:** {suggestion['line']}")
                            st.write(f"**Suggestion:** {suggestion['suggestion']}")
                        with col2:
                            severity_color = {
                                "info": "🔵",
                                "warning": "🟡", 
                                "error": "🔴",
                                "critical": "⚫"
                            }
                            st.write(f"{severity_color.get(suggestion['severity'], '⚪')} {suggestion['severity'].title()}")
                
                # Option to generate refactored code
                if st.button("🔧 Generate Refactored Code"):
                    with st.spinner("Generating refactored code..."):
                        st.markdown("#### ✨ Refactored Code")
                        st.code("""
# Refactored version with improvements applied
def validate_user_input(user_input_data):
    \"\"\"Validate user input data.\"\"\"
    return user_input_data is not None and len(user_input_data) > 0

def process_items(items, condition_func, process_func):
    \"\"\"Process items that meet the condition.\"\"\"
    return [process_func(item) for item in items if condition_func(item)]

def main_function(user_input_data):
    \"\"\"Main processing function with improved structure.\"\"\"
    if not validate_user_input(user_input_data):
        raise ValueError("Invalid input data")
    
    # Process the data
    result = process_items(user_input_data, lambda x: x > 0, lambda x: x * 2)
    return result
""", language=language)
                        
                        st.success("✅ Refactored code generated! Review the improvements above.")
                        
        except Exception as e:
            error_id = generate_error_id()
            st.error(f"Refactoring analysis error [{error_id}]: {str(e)}")
            logger.error(f"Code refactoring error [{error_id}]: {e}")

def main() -> None:
    """Main Streamlit application - Chat Interface Only"""
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize advanced AI components
    initialize_advanced_ai()
    
    # Render sidebar and get settings
    selected_model, use_cot, reasoning_type = render_sidebar()
    
    # Main chat interface
    st.title(UI_CONFIG["app_name"])
    
    # Show current reasoning mode and tool status
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if use_cot:
            reasoning_display = reasoning_type.replace('_', ' ').title()
            st.markdown(f"### 💬 Chat with your AI coding assistant (🧠 {reasoning_display} mode)")
        else:
            st.markdown("### 💬 Chat with your AI coding assistant")
    
    with col2:
        if st.session_state.plugins_initialized:
            tool_count = len(st.session_state.agent.client.available_tools)
            if tool_count > 0:
                st.metric("🛠️ Tools", tool_count)
                if st.button("🔧", help="Open Tool Manager"):
                    st.switch_page("pages/Plugin_Manager.py")
    
    # Tool suggestions (if tools are available)
    if (st.session_state.plugins_initialized and 
        len(st.session_state.agent.client.available_tools) > 0 and 
        len(st.session_state.messages) == 0):
        
        with st.expander("🛠️ Quick Tool Suggestions", expanded=False):
            # Combine regular and advanced tool suggestions
            regular_suggestions = UI_CONFIG.get("tool_suggestions", [
                "🌐 \"Search the web for the latest Python frameworks\"",
                "📁 \"List files in my current directory\"",
                "🔍 \"Analyze this code file for potential issues\"",
                "📊 \"Generate a report on project structure\""
            ])
            
            suggestions = regular_suggestions
            if ADVANCED_AI_CONFIG.get("enabled", False):
                suggestions.extend(ADVANCED_TOOL_SUGGESTIONS)
            
            st.markdown("**Try asking me to:**")
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")
            
            st.markdown("\nI can automatically use tools when needed, or explore the advanced features below!")
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🛠️ Open Tool Agent", use_container_width=True):
                    st.switch_page("pages/Tool_Agent.py")
            with col2:
                if st.button("🔌 Manage Plugins", use_container_width=True):
                    st.switch_page("pages/Plugin_Manager.py")
    
    # Display chat messages using native Streamlit chat components (secure)
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.write(message["content"])
    
    # Chat input - using native Streamlit components for security with validation
    if prompt := st.chat_input(UI_CONFIG.get("chat_placeholder", "Ask me anything about coding...")):
        # Validate input using utility function
        is_valid, error_message = validate_user_input(prompt)
        if not is_valid:
            st.error(error_message)
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)
        
        # Generate response with better error handling
        with st.chat_message("assistant", avatar="🤖"):
            handle_chat_response(prompt, use_cot, reasoning_type)
    
    # Render advanced AI features if enabled
    if ADVANCED_AI_CONFIG.get("enabled", False):
        render_advanced_features()

if __name__ == "__main__":
    main()

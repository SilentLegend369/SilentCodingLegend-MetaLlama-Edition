"""
Reusable UI components for Knowledge Management Dashboard
Following DRY principles and consistent design patterns
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.config.knowledge_config import KNOWLEDGE_CONFIG, CHART_CONFIG


def display_search_result(result: Dict[str, Any], index: int) -> None:
    """
    Render a single search result in an expander.
    
    Args:
        result: Search result data
        index: Result index for display
    """
    score = result.get('relevance_score', 0)
    title = f"Result {index + 1} - Relevance: {score:.3f}"
    
    with st.expander(title, expanded=(index == 0)):  # Expand first result by default
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("**Content:**")
            content = result.get('content', 'No content available')
            st.text_area("", content, height=100, disabled=True, key=f"content_{index}")
            
        with col2:
            st.markdown("**Metadata:**")
            session_id = result.get('session_id', 'Unknown')
            timestamp = result.get('timestamp', 'Unknown')
            
            st.caption(f"**Session:** {session_id}")
            st.caption(f"**Time:** {timestamp}")
            
            if result.get('metadata'):
                with st.expander("Additional Info"):
                    st.json(result['metadata'])


def display_entity_card(entity: Dict[str, Any]) -> None:
    """
    Display an entity in a card format.
    
    Args:
        entity: Entity data
    """
    name = entity.get('name', 'Unknown')
    entity_type = entity.get('type', 'Unknown')
    
    with st.container():
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px 0;">
                <h4 style="margin: 0; color: #1f77b4;">{name}</h4>
                <p style="margin: 5px 0; color: #666;">Type: {entity_type}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def display_statistics_cards(stats: Dict[str, Any]) -> None:
    """
    Display statistics in a card layout.
    
    Args:
        stats: Statistics data
    """
    if not stats:
        st.warning("No statistics available")
        return
    
    # Extract stats with safe defaults
    kg_stats = stats.get('knowledge_graph', {})
    vector_stats = stats.get('vector_database', {})
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        entities_count = kg_stats.get('total_entities', 0)
        st.metric(
            label="🏷️ Total Entities",
            value=f"{entities_count:,}",
            help="Number of entities in the knowledge graph"
        )
    
    with col2:
        relations_count = kg_stats.get('total_relations', 0)
        st.metric(
            label="🔗 Relations",
            value=f"{relations_count:,}",
            help="Number of relationships between entities"
        )
    
    with col3:
        vectors_count = vector_stats.get('total_vectors', 0)
        st.metric(
            label="🧮 Vectors",
            value=f"{vectors_count:,}",
            help="Number of vectors in the database"
        )
    
    with col4:
        last_update = stats.get('last_refresh', datetime.now())
        if isinstance(last_update, datetime):
            update_time = last_update.strftime('%H:%M:%S')
        else:
            update_time = str(last_update)
        
        st.metric(
            label="🔄 Last Update",
            value=update_time,
            help="Last time statistics were refreshed"
        )


def create_entity_distribution_chart(entities_by_type: Dict[str, int]) -> go.Figure:
    """
    Create a pie chart showing entity distribution by type.
    
    Args:
        entities_by_type: Dictionary mapping entity types to counts
        
    Returns:
        Plotly figure
    """
    if not entities_by_type:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle'
        )
    
    fig = px.pie(
        values=list(entities_by_type.values()),
        names=list(entities_by_type.keys()),
        title="Entity Distribution by Type",
        color_discrete_sequence=CHART_CONFIG['color_palette']
    )
    
    fig.update_layout(
        height=CHART_CONFIG['default_height'],
        template=CHART_CONFIG['theme']
    )
    
    return fig


def create_activity_timeline_chart(activity_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a timeline chart showing knowledge base activity.
    
    Args:
        activity_data: List of activity events
        
    Returns:
        Plotly figure
    """
    if not activity_data:
        return go.Figure().add_annotation(
            text="No activity data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle'
        )
    
    # Extract data for plotting
    timestamps = [item.get('timestamp', datetime.now()) for item in activity_data]
    actions = [item.get('action', 'Unknown') for item in activity_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=actions,
        mode='markers+lines',
        name='Activity',
        marker=dict(size=8, color=CHART_CONFIG['color_palette'][0]),
        line=dict(color=CHART_CONFIG['color_palette'][0])
    ))
    
    fig.update_layout(
        title="Knowledge Base Activity Timeline",
        xaxis_title="Time",
        yaxis_title="Activity Type",
        height=CHART_CONFIG['default_height'],
        template=CHART_CONFIG['theme']
    )
    
    return fig


def display_error_message(error_type: str, custom_message: Optional[str] = None) -> None:
    """
    Display standardized error messages.
    
    Args:
        error_type: Type of error from KNOWLEDGE_CONFIG.ERROR_MESSAGES
        custom_message: Optional custom error message
    """
    if custom_message:
        st.error(custom_message)
    else:
        message = KNOWLEDGE_CONFIG.ERROR_MESSAGES.get(
            error_type, 
            KNOWLEDGE_CONFIG.ERROR_MESSAGES['unexpected_error']
        )
        st.error(message)


def display_success_message(success_type: str, custom_message: Optional[str] = None) -> None:
    """
    Display standardized success messages.
    
    Args:
        success_type: Type of success from KNOWLEDGE_CONFIG.SUCCESS_MESSAGES
        custom_message: Optional custom success message
    """
    if custom_message:
        st.success(custom_message)
        st.toast(custom_message, icon="🎉")
    else:
        message = KNOWLEDGE_CONFIG.SUCCESS_MESSAGES.get(
            success_type,
            "✅ Operation completed successfully!"
        )
        st.success(message)
        st.toast(message, icon="🎉")


def display_warning_message(warning_type: str, custom_message: Optional[str] = None) -> None:
    """
    Display standardized warning messages.
    
    Args:
        warning_type: Type of warning from KNOWLEDGE_CONFIG.WARNING_MESSAGES
        custom_message: Optional custom warning message
    """
    if custom_message:
        st.warning(custom_message)
    else:
        message = KNOWLEDGE_CONFIG.WARNING_MESSAGES.get(
            warning_type,
            "⚠️ Please check your input and try again."
        )
        st.warning(message)


def create_loading_placeholder(message: str = "Loading..."):
    """
    Create a loading placeholder with spinner.
    
    Args:
        message: Loading message to display
        
    Returns:
        Streamlit empty placeholder
    """
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner(message):
            st.write("Please wait...")
    return placeholder


def display_no_data_message(context: str = "data") -> None:
    """
    Display a consistent no-data message.
    
    Args:
        context: Context for what data is missing
    """
    st.info(f"ℹ️ No {context} available at this time.")


def create_refresh_button(key: str, label: str = "🔄 Refresh Data") -> bool:
    """
    Create a standardized refresh button.
    
    Args:
        key: Unique key for the button
        label: Button label
        
    Returns:
        True if button was clicked
    """
    return st.button(label, key=key, help="Click to refresh data from the knowledge base")


class KnowledgeUIComponents:
    """Enhanced collection of reusable UI components for the Knowledge Management Dashboard"""
    
    def __init__(self):
        self.config = KNOWLEDGE_CONFIG
        self.chart_config = CHART_CONFIG
    
    def display_page_header(self, title: str, description: str, icon: str = "🧠") -> None:
        """Display a consistent page header"""
        st.title(f"{icon} {title}")
        if description:
            st.markdown(f"*{description}*")
        st.divider()
    
    def display_metrics_row(self, metrics: List[Dict[str, Any]], columns: int = 4) -> None:
        """Display a row of metrics using Streamlit columns"""
        cols = st.columns(columns)
        
        for i, metric in enumerate(metrics):
            col_index = i % columns
            with cols[col_index]:
                st.metric(
                    label=metric.get('label', 'Metric'),
                    value=metric.get('value', 0),
                    delta=metric.get('delta'),
                    help=metric.get('help', '')
                )
    
    def create_form_section(self, title: str, fields: List[Dict[str, Any]], 
                           form_key: str, submit_label: str = "Submit") -> Optional[Dict[str, Any]]:
        """Create a form section with validation"""
        st.subheader(title)
        
        with st.form(form_key):
            form_data = {}
            
            for field in fields:
                field_type = field.get('type', 'text')
                field_key = field.get('key', 'field')
                field_label = field.get('label', 'Field')
                field_help = field.get('help', '')
                
                if field_type == 'text':
                    form_data[field_key] = st.text_input(
                        field_label,
                        placeholder=field.get('placeholder', ''),
                        help=field_help,
                        max_chars=field.get('max_chars', None)
                    )
                elif field_type == 'textarea':
                    form_data[field_key] = st.text_area(
                        field_label,
                        placeholder=field.get('placeholder', ''),
                        help=field_help,
                        height=field.get('height', 150),
                        max_chars=field.get('max_chars', None)
                    )
                elif field_type == 'select':
                    form_data[field_key] = st.selectbox(
                        field_label,
                        options=field.get('options', []),
                        help=field_help
                    )
                elif field_type == 'multiselect':
                    form_data[field_key] = st.multiselect(
                        field_label,
                        options=field.get('options', []),
                        default=field.get('default', []),
                        help=field_help
                    )
                elif field_type == 'slider':
                    form_data[field_key] = st.slider(
                        field_label,
                        min_value=field.get('min_value', 1),
                        max_value=field.get('max_value', 100),
                        value=field.get('default', 10),
                        help=field_help
                    )
                elif field_type == 'checkbox':
                    form_data[field_key] = st.checkbox(
                        field_label,
                        value=field.get('default', False),
                        help=field_help
                    )
            
            submitted = st.form_submit_button(submit_label, type="primary")
            
            if submitted:
                # Basic validation
                errors = []
                for field in fields:
                    if field.get('required', False):
                        field_key = field.get('key', 'field')
                        if not form_data.get(field_key):
                            errors.append(f"{field.get('label', 'Field')} is required")
                
                if errors:
                    for error in errors:
                        st.error(error)
                    return None
                
                return form_data
        
        return None
    
    def create_safe_search_interface(self, placeholder: str = "Enter search query...",
                                   max_results_default: int = 10) -> tuple:
        """Create a safe search interface with validation"""
        from src.utils.knowledge_validators import knowledge_validator
        
        # Search input
        search_query = st.text_input(
            "Search Query:",
            placeholder=placeholder,
            max_chars=self.config.security.max_search_query_length,
            help="Use natural language to search the knowledge base"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            max_results = st.slider(
                "Maximum results",
                1, 
                self.config.security.max_search_results,
                max_results_default
            )
        
        with col2:
            session_filter = st.text_input(
                "Session ID (optional)",
                placeholder="session_123",
                help="Filter results by session ID"
            )
        
        with col3:
            search_button = st.button("🔍 Search", type="primary")
        
        # Validate inputs if search was triggered
        if search_button and search_query:
            query_result = knowledge_validator.validate_search_query(search_query)
            if not query_result.is_valid:
                st.error(query_result.error_message)
                return None, None, None, False
            
            if session_filter:
                session_result = knowledge_validator.validate_session_id(session_filter)
                if not session_result.is_valid:
                    st.error(session_result.error_message)
                    return None, None, None, False
                session_filter = session_result.cleaned_value
            
            return query_result.cleaned_value, max_results, session_filter, True
        
        return search_query, max_results, session_filter, False
    
    def display_knowledge_note_form(self, form_key: str = "knowledge_note_form") -> Optional[Dict[str, Any]]:
        """Create a knowledge note form with validation"""
        fields = [
            {
                'type': 'text',
                'key': 'title',
                'label': 'Note Title*',
                'placeholder': "e.g., 'Python Best Practices'",
                'required': True,
                'max_chars': self.config.security.max_note_title_length
            },
            {
                'type': 'textarea',
                'key': 'content',
                'label': 'Note Content*',
                'placeholder': 'Enter detailed content about the topic...',
                'required': True,
                'height': 150,
                'max_chars': self.config.security.max_note_content_length
            },
            {
                'type': 'select',
                'key': 'category',
                'label': 'Category',
                'options': self.config.note_categories,
                'help': 'Select the most appropriate category'
            },
            {
                'type': 'text',
                'key': 'tags',
                'label': 'Tags (comma-separated)',
                'placeholder': 'e.g., python, web, api',
                'help': 'Add relevant tags to help with searching'
            }
        ]
        
        return self.create_form_section(
            "➕ Add New Knowledge Note",
            fields,
            form_key,
            "💾 Save Note"
        )


# Global UI components instance
ui_components = KnowledgeUIComponents()


def create_knowledge_note_form(form_key: str = "knowledge_note_form") -> Optional[Dict[str, Any]]:
    """Convenience function to create a knowledge note form"""
    return ui_components.display_knowledge_note_form(form_key)


def create_safe_search_interface(placeholder: str = "Enter search query...") -> tuple:
    """Convenience function to create safe search interface"""
    return ui_components.create_safe_search_interface(placeholder)

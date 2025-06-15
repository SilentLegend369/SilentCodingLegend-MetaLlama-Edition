"""
Enhanced Analytics View - Professional Token & Model Analytics Dashboard
SilentCodingLegend AI Agent Analytics with Security, Performance & Maintainability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import logging
import json

# Enhanced imports with proper error handling
try:
    from utils.enhanced_analytics import EnhancedAnalyticsProcessor
    from utils.analytics_models import AnalyticsResult, PerformanceInsight
    from config.analytics_config import ANALYTICS_CONFIG
except ImportError as e:
    st.error(f"🔴 Import Error: {e}")
    st.error("Please ensure all required modules are properly installed and configured.")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page with enhanced settings
st.set_page_config(
    page_title="Analytics Dashboard - SilentCodingLegend",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with improved security and maintainability
DASHBOARD_CSS = """
<style>
    /* Main dashboard styles */
    .analytics-header {
        text-align: center;
        color: #4f8bf9;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Metric cards with improved accessibility */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #4f8bf9, #8e44ad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 1.8rem;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #4f8bf9;
        padding-bottom: 0.5rem;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Enhanced status boxes */
    .status-success {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #155724;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #ffc107, #fd7e14);
        color: #212529;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #856404;
    }
    
    .status-error {
        background: linear-gradient(135deg, #dc3545, #e83e8c);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #721c24;
    }
    
    .status-info {
        background: linear-gradient(135deg, #17a2b8, #6f42c1);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #0c5460;
    }
    
    /* Filter panel */
    .filter-panel {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    
    /* Loading spinner */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
</style>
"""

def safe_create_metric_card(value: str, label: str) -> str:
    """
    Create metric card HTML safely (avoiding XSS)
    """
    # Sanitize inputs to prevent XSS
    safe_value = str(value).replace('<', '&lt;').replace('>', '&gt;')
    safe_label = str(label).replace('<', '&lt;').replace('>', '&gt;')
    
    return f"""
    <div class="metric-card">
        <p class="metric-value">{safe_value}</p>
        <p class="metric-label">{safe_label}</p>
    </div>
    """

def render_performance_insights(insights: List[PerformanceInsight]):
    """Render performance insights with proper status styling"""
    if not insights:
        st.info("🔍 No specific performance insights available at this time.")
        return
    
    st.markdown('<div class="section-header">🎯 Performance Insights</div>', unsafe_allow_html=True)
    
    for insight in insights:
        # Use Streamlit's built-in status components for safety
        if insight.severity == "success":
            st.success(insight.message)
        elif insight.severity == "warning":
            st.warning(insight.message)
        elif insight.severity == "error":
            st.error(insight.message)
        else:
            st.info(insight.message)

def create_enhanced_charts(analysis: AnalyticsResult) -> Tuple[go.Figure, go.Figure, go.Figure]:
    """Create enhanced interactive charts with better styling"""
    
    # 1. Model Usage Pie Chart
    if analysis.model_usage:
        model_fig = px.pie(
            values=list(analysis.model_usage.values()),
            names=list(analysis.model_usage.keys()),
            title="🤖 Model Usage Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        model_fig.update_layout(
            title_font_size=18,
            title_x=0.5,
            showlegend=True,
            height=400
        )
    else:
        model_fig = go.Figure()
        model_fig.add_annotation(
            text="No model usage data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # 2. Daily Usage Trends
    if analysis.daily_usage:
        dates = sorted(analysis.daily_usage.keys())
        values = [analysis.daily_usage[date] for date in dates]
        
        daily_fig = px.line(
            x=dates, y=values,
            title="📈 Daily Usage Trends",
            labels={'x': 'Date', 'y': 'Conversations'},
            line_shape='spline'
        )
        daily_fig.update_traces(
            line=dict(color='#4f8bf9', width=3),
            marker=dict(size=8, color='#764ba2')
        )
        daily_fig.update_layout(
            title_font_size=18,
            title_x=0.5,
            xaxis_title="Date",
            yaxis_title="Number of Conversations",
            height=400,
            hovermode='x unified'
        )
    else:
        daily_fig = go.Figure()
        daily_fig.add_annotation(
            text="No daily usage data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # 3. Token Distribution Chart
    token_data = {
        'Type': ['User Tokens', 'Assistant Tokens'],
        'Count': [analysis.user_tokens, analysis.assistant_tokens],
        'Color': ['#4f8bf9', '#764ba2']
    }
    
    token_fig = px.bar(
        x=token_data['Type'],
        y=token_data['Count'],
        title="💬 Token Distribution",
        color=token_data['Type'],
        color_discrete_map={'User Tokens': '#4f8bf9', 'Assistant Tokens': '#764ba2'}
    )
    token_fig.update_layout(
        title_font_size=18,
        title_x=0.5,
        xaxis_title="Token Type",
        yaxis_title="Token Count",
        height=400,
        showlegend=False
    )
    
    return model_fig, daily_fig, token_fig

def create_date_filter(analysis: AnalyticsResult) -> Tuple[datetime, datetime]:
    """Create date range filter for analytics"""
    if not analysis.daily_usage:
        # Default to last 30 days if no data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date
    
    dates = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in analysis.daily_usage.keys()]
    min_date = min(dates)
    max_date = max(dates)
    
    # Sidebar date filter
    st.sidebar.markdown("### 📅 Date Range Filter")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
        help="Filter analytics data for the selected date range"
    )
    
    if len(date_range) == 2:
        return datetime.combine(date_range[0], datetime.min.time()), \
               datetime.combine(date_range[1], datetime.max.time())
    else:
        return min_date, max_date

def main():
    """Main dashboard function with enhanced functionality"""
    
    # Apply CSS
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="analytics-header">📊 SilentCodingLegend Analytics Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize enhanced analytics processor
    try:
        with st.spinner("🔧 Initializing analytics processor..."):
            analytics = EnhancedAnalyticsProcessor()
    except Exception as e:
        st.error(f"🔴 Failed to initialize analytics processor: {e}")
        st.stop()
    
    # Load and analyze data with enhanced error handling
    try:
        with st.spinner("🔍 Loading and analyzing conversation data..."):
            conversations = analytics.load_conversation_data()
            
            if not conversations:
                st.warning("📭 No conversation data found. Please check your data directory.")
                st.info(f"Expected data directory: {analytics.data_dir}")
                return
            
            # Convert to tuple for caching
            conversations_tuple = tuple(conversations)
            analysis = analytics.analyze_conversations(conversations_tuple)
            
    except Exception as e:
        st.error(f"🔴 Error during data analysis: {e}")
        logger.error(f"Analysis error: {e}")
        return
    
    # Sidebar filters and controls
    st.sidebar.markdown("## 🎛️ Dashboard Controls")
    
    # Date range filter
    try:
        start_date, end_date = create_date_filter(analysis)
        st.sidebar.success(f"📊 Analyzing {len(conversations)} conversations")
    except Exception as e:
        st.sidebar.error(f"Date filter error: {e}")
        start_date = end_date = datetime.now()
    
    # Additional filters
    st.sidebar.markdown("### 🔧 Advanced Options")
    show_raw_data = st.sidebar.checkbox("Show Raw Data", help="Display raw conversation data")
    show_debug_info = st.sidebar.checkbox("Show Debug Info", help="Display debugging information")
    
    # Main metrics display
    st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
    
    # Create metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(safe_create_metric_card(
            f"{analysis.total_conversations:,}", 
            "Total Conversations"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(safe_create_metric_card(
            f"{analysis.total_tokens:,}", 
            "Total Tokens"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(safe_create_metric_card(
            f"${analysis.estimated_cost:.2f}", 
            "Estimated Cost"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(safe_create_metric_card(
            f"{analysis.avg_conversation_length:.1f}", 
            "Avg Conv Length"
        ), unsafe_allow_html=True)
    
    # Secondary metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("User Tokens", f"{analysis.user_tokens:,}")
    
    with col6:
        st.metric("Assistant Tokens", f"{analysis.assistant_tokens:,}")
    
    with col7:
        confidence_display = f"{analysis.avg_confidence:.2f}" if analysis.avg_confidence > 0 else "N/A"
        st.metric("Avg Confidence", confidence_display)
    
    with col8:
        enhancement_rate = (analysis.nltk_enhancements / analysis.total_conversations * 100) if analysis.total_conversations > 0 else 0
        st.metric("Enhancement Rate", f"{enhancement_rate:.1f}%")
    
    # Performance insights
    try:
        insights = analytics.generate_insights(analysis)
        render_performance_insights(insights)
    except Exception as e:
        st.error(f"Error generating insights: {e}")
    
    # Charts section
    st.markdown('<div class="section-header">📊 Analytics Charts</div>', unsafe_allow_html=True)
    
    try:
        model_fig, daily_fig, token_fig = create_enhanced_charts(analysis)
        
        # Display charts in columns
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.plotly_chart(model_fig, use_container_width=True)
            st.plotly_chart(token_fig, use_container_width=True)
        
        with chart_col2:
            st.plotly_chart(daily_fig, use_container_width=True)
            
            # Additional metrics chart
            if analysis.reasoning_usage:
                reasoning_fig = px.bar(
                    x=list(analysis.reasoning_usage.keys()),
                    y=list(analysis.reasoning_usage.values()),
                    title="🧠 Reasoning Types Usage",
                    color_discrete_sequence=['#8e44ad']
                )
                reasoning_fig.update_layout(
                    title_font_size=16,
                    title_x=0.5,
                    height=300
                )
                st.plotly_chart(reasoning_fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error creating charts: {e}")
        logger.error(f"Chart creation error: {e}")
    
    # Raw data section (if enabled)
    if show_raw_data:
        st.markdown('<div class="section-header">🗄️ Raw Data</div>', unsafe_allow_html=True)
        
        if conversations:
            # Create DataFrame for better display
            df_data = []
            for conv in conversations[:100]:  # Limit to first 100 for performance
                df_data.append({
                    'Source File': conv.get('source_file', 'Unknown'),
                    'Timestamp': conv.get('timestamp', 'N/A'),
                    'Messages': len(analytics._extract_messages(conv)),
                    'Model': analytics._extract_model(conv) or 'Unknown'
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Download option
            if st.button("📥 Download Full Dataset"):
                csv = pd.DataFrame(conversations).to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"conversation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Debug information (if enabled)
    if show_debug_info:
        st.markdown('<div class="section-header">🐛 Debug Information</div>', unsafe_allow_html=True)
        
        debug_info = {
            "Configuration": {
                "Data Directory": str(analytics.data_dir),
                "Max Files": analytics.config.max_files_to_process,
                "Token Ratio": analytics.config.token_estimation_ratio
            },
            "Analysis Results": {
                "Error Rate": f"{analysis.error_rate:.2%}",
                "Processing Time": "N/A",  # Could add timing
                "Memory Usage": "N/A"      # Could add memory tracking
            }
        }
        
        st.json(debug_info)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🤖 **SilentCodingLegend Analytics Dashboard** - "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Data processed: {len(conversations)} conversations"
    )

if __name__ == "__main__":
    main()

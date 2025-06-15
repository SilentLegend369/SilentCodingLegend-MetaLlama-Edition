"""
Coding Assistant Styles
Centralized CSS styles for the coding assistant interface
"""

CODING_ASSISTANT_CSS = """
<style>
    /* Main app background */
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #00D4AA;
        padding: 1rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #00D4AA, #0099CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Code container */
    .code-container {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Result styling */
    .result-container {
        background: linear-gradient(135deg, #1A202C, #2D3748);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #00D4AA;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Feature card */
    .feature-card {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    /* Processing indicator */
    .processing-indicator {
        background: linear-gradient(90deg, #00D4AA, #0099CC);
        padding: 1rem;
        border-radius: 0.8rem;
        text-align: center;
        color: #000;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #00D4AA, #0099CC);
        color: #FFFFFF;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
    }
    
    /* Metrics styling */
    .metric-container {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1rem;
        border-radius: 0.8rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Language badge */
    .language-badge {
        background: linear-gradient(90deg, #0099CC, #00D4AA);
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
        display: inline-block;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #38A169, #48BB78);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Error message */
    .error-message {
        background: linear-gradient(135deg, #E53E3E, #F56565);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Warning message */
    .warning-message {
        background: linear-gradient(135deg, #DD6B20, #ED8936);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Info message */
    .info-message {
        background: linear-gradient(135deg, #3182CE, #4299E1);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(90deg, #00D4AA, #0099CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        border-radius: 0.8rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00D4AA, #0099CC);
        color: #000000;
        font-weight: bold;
    }
    
    /* Session history styling */
    .session-item {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        border-left: 3px solid #00D4AA;
    }
    
    .session-timestamp {
        color: #00D4AA;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    .session-type {
        color: #0099CC;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: #1A202C !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.8rem !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #2D3748, #4A5568) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        border-radius: 0.5rem !important;
    }
    
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, #2D3748, #4A5568) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        border-radius: 0.5rem !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #2D3748, #4A5568) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.5rem !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background: linear-gradient(135deg, #2D3748, #4A5568) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.5rem !important;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #FFFFFF !important;
    }
    
    /* Radio button styling */
    .stRadio > label {
        color: #FFFFFF !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00D4AA, #0099CC) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #2D3748, #4A5568) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.5rem !important;
        color: #FFFFFF !important;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #1A202C, #2D3748) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0 0 0.5rem 0.5rem !important;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .code-container, .result-container {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .stButton > button {
            width: 100%;
            margin: 0.2rem 0;
        }
        
        .feature-card {
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
        
        .session-item {
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
    }
    
    /* Dark theme scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1A202C;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #0099CC, #00D4AA);
    }
</style>
"""


def get_coding_assistant_styles() -> str:
    """Get the CSS styles for the coding assistant"""
    return CODING_ASSISTANT_CSS

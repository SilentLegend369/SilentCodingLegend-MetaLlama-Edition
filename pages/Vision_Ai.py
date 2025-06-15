"""
Vision AI - Image Understanding and Analysis
SilentCodingLegend AI Agent with Computer Vision Capabilities
"""
import streamlit as st
import cv2
import numpy as np
import base64
import io
import os
from PIL import Image
from datetime import datetime
from src.core.agent import SilentCodingLegendAgent
from src.utils.logging import get_logger
import json
import pathlib
from typing import Dict, List, Optional, Union

# Configure page
st.set_page_config(
    page_title="Vision AI - SilentCodingLegend",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger(__name__)

# --- Configuration ---
APP_DIR = pathlib.Path(__file__).parent
DATA_DIR = APP_DIR / "data" / "conversations"
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'webp', 'bmp']
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MULTIMODAL_MODELS = {
    "Llama-4-Scout-17B-16E-Instruct-FP8": "Llama 4 Scout (Multimodal)",
    "Llama-4-Maverick-17B-128E-Instruct-FP8": "Llama 4 Maverick (Advanced)"
}
DEFAULT_MODEL = "Llama-4-Scout-17B-16E-Instruct-FP8"

# Feature card data for better maintainability
FEATURE_CARDS = [
    {
        "title": "General Analysis",
        "description": "Comprehensive image understanding",
        "icon": "🔍"
    },
    {
        "title": "Code Analysis", 
        "description": "Analyze code from screenshots",
        "icon": "💻"
    },
    {
        "title": "Design Review",
        "description": "UI/UX critique and suggestions", 
        "icon": "🎨"
    },
    {
        "title": "Object Detection",
        "description": "Identify and locate objects",
        "icon": "📦"
    },
    {
        "title": "Technical Analysis",
        "description": "CV metrics and image properties",
        "icon": "🔬"
    },
    {
        "title": "Creative Description", 
        "description": "Artistic image interpretation",
        "icon": "✨"
    }
]

# Custom CSS for Vision AI page
st.markdown("""
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
    
    /* Image container */
    .image-container {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Analysis result styling */
    .analysis-result {
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
        font-weight: bold;
        width: 100%;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .image-container, .analysis-result {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .main-header {
            font-size: 1.5rem;
            padding: 0.5rem 0;
        }
        
        .feature-card {
            padding: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def render_feature_card(title: str, description: str, icon: str = "👁️"):
    """Renders a styled feature card using Streamlit markdown."""
    st.markdown(f"""
    <div class="feature-card">
        <h4>{icon} {title}</h4>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def render_feature_cards():
    """Renders all feature cards in a 3-column layout using configuration."""
    col1, col2, col3 = st.columns(3)
    
    # Distribute cards across columns
    columns = [col1, col2, col3]
    
    for i, card in enumerate(FEATURE_CARDS):
        with columns[i % 3]:
            render_feature_card(
                card["title"],
                card["description"], 
                card["icon"]
            )

def display_error(message: str, error_type: str = "❌", log_message: Optional[str] = None):
    """Displays a consistent error message and optionally logs it."""
    st.error(f"{error_type} {message}")
    if log_message:
        logger.error(log_message)
    elif message:
        logger.error(message)

def display_success(message: str, success_type: str = "✅"):
    """Displays a consistent success message."""
    st.success(f"{success_type} {message}")

def display_info(message: str, info_type: str = "ℹ️"):
    """Displays a consistent info message."""
    st.info(f"{info_type} {message}")

def display_metadata(metadata_dict: Dict[str, str], title: Optional[str] = None):
    """Displays metadata in a consistent format."""
    if title:
        st.markdown(f"**{title}**")
    
    for key, value in metadata_dict.items():
        st.write(f"**{key}:** {value}")

def display_image_info(uploaded_file, image, opencv_data: Optional[Dict] = None):
    """Displays comprehensive image information including technical metrics."""
    # Basic image metadata
    basic_info = {
        "File": uploaded_file.name,
        "Size": f"{uploaded_file.size / 1024:.1f} KB",
        "Dimensions": f"{image.size[0]} x {image.size[1]}",
        "Format": image.format,
        "Mode": image.mode
    }
    
    display_metadata(basic_info, "📷 Image Information")
    
    # Technical analysis if available
    if opencv_data:
        technical_info = {
            "Brightness": f"{opencv_data['brightness']:.1f}",
            "Edge Density": f"{opencv_data['edge_density']:.3f}",
            "Blur Score": f"{opencv_data['blur_score']:.1f}",
            "Quality": '🔍 Sharp' if not opencv_data['is_blurry'] else '😵 Blurry'
        }
        
        display_metadata(technical_info, "🔬 Technical Analysis")

def initialize_session():
    """Initializes all necessary Streamlit session state variables."""
    if 'vision_agent' not in st.session_state:
        st.session_state.vision_agent = SilentCodingLegendAgent()
        logger.info("Initialized Vision AI agent")
    
    if 'vision_session_id' not in st.session_state:
        st.session_state.vision_session_id = f"vision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'vision_history' not in st.session_state:
        st.session_state.vision_history = load_vision_analysis_history()
    
    # Force a multimodal model if a non-vision model is somehow selected
    current_model = st.session_state.vision_agent.client.config.model
    if current_model not in MULTIMODAL_MODELS:
        st.session_state.vision_agent.client.config.model = DEFAULT_MODEL

def validate_uploaded_image(uploaded_file) -> Union[Image.Image, None]:
    """
    Validate and process uploaded image file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        PIL Image object if valid, None if invalid
    """
    try:
        # Verify the file is a valid image before proceeding
        image = Image.open(uploaded_file)
        image.verify()  # Verifies integrity without loading full image data
        
        # Re-open after verification (verify() closes the file)
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        
        # Additional validation - check file size
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            display_error(f"File too large! Maximum size is {MAX_FILE_SIZE_MB}MB")
            return None
            
        # Check format
        if image.format.lower() not in [fmt.upper() for fmt in SUPPORTED_FORMATS]:
            display_error(f"Unsupported format! Supported formats: {', '.join(SUPPORTED_FORMATS)}")
            return None
            
        return image
        
    except (IOError, SyntaxError) as e:
        display_error("Invalid or corrupted image file", log_message=f"User uploaded an invalid image file: {uploaded_file.name} - {e}")
        return None
    except Exception as e:
        display_error("Unexpected error processing image", log_message=f"Unexpected error validating image: {e}")
        return None

class VisionAI:
    def __init__(self):
        self.supported_formats = SUPPORTED_FORMATS
        self.max_file_size = MAX_FILE_SIZE_BYTES
        
    def encode_image_to_base64(self, image) -> str:
        """Convert PIL Image to base64 string for API"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def process_with_opencv(self, image: Image.Image) -> dict:
        """Basic OpenCV image analysis"""
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Get basic image properties
        height, width = img_cv.shape[:2]
        
        # Color analysis
        avg_color = np.mean(img_cv, axis=(0, 1))
        
        # Edge detection
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (height * width)
        
        # Brightness analysis
        brightness = np.mean(gray)
        
        # Detect if image is blurry (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return {
            'dimensions': f"{width} x {height}",
            'avg_color_bgr': avg_color.tolist(),
            'brightness': float(brightness),
            'edge_density': float(edge_density),
            'blur_score': float(blur_score),
            'is_blurry': blur_score < 100
        }
    
    def get_analysis_prompt(self, analysis_type: str, opencv_data: dict = None) -> str:
        """Generate appropriate prompt based on analysis type"""
        base_prompt = "Analyze this image and provide detailed insights. "
        
        if analysis_type == "General Analysis":
            return base_prompt + "Describe what you see, including objects, people, scenes, colors, and any interesting details."
        
        elif analysis_type == "Code Analysis":
            return base_prompt + "If this image contains code, programming interfaces, or technical content, analyze the code quality, identify the programming language, suggest improvements, and explain what the code does."
        
        elif analysis_type == "Design Review":
            return base_prompt + "Analyze this from a design perspective. Comment on layout, color scheme, typography, user experience, and suggest improvements."
        
        elif analysis_type == "Object Detection":
            return base_prompt + "Identify and list all objects, people, and elements you can see in this image. Provide their approximate locations and relationships."
        
        elif analysis_type == "Technical Analysis":
            opencv_info = f"\n\nTechnical data from OpenCV analysis:\n- Dimensions: {opencv_data.get('dimensions', 'N/A')}\n- Brightness: {opencv_data.get('brightness', 'N/A'):.1f}\n- Edge density: {opencv_data.get('edge_density', 'N/A'):.3f}\n- Blur score: {opencv_data.get('blur_score', 'N/A'):.1f} ({'Blurry' if opencv_data.get('is_blurry', False) else 'Sharp'})"
            return base_prompt + f"Provide technical analysis including image quality, composition, and technical properties.{opencv_info}"
        
        elif analysis_type == "Creative Description":
            return base_prompt + "Write a creative, detailed description of this image as if you're a poet or storyteller. Focus on mood, atmosphere, and artistic elements."
        
        return base_prompt

def save_vision_analysis_backup(analysis_record: dict, session_id: str) -> str | None:
    """Save vision analysis results to the data directory."""
    try:
        # Ensure the backup directory exists (using the DATA_DIR constant)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"vision_{session_id}_{timestamp}.json"
        backup_path = DATA_DIR / backup_filename
        
        backup_data = {
            "session_id": session_id,
            "backup_timestamp": datetime.now().isoformat(),
            "analysis_record": analysis_record
        }
        
        with backup_path.open('w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Vision analysis backed up to {backup_path}")
        return str(backup_path)
        
    # Catch specific exceptions
    except (IOError, OSError, json.JSONDecodeError) as e:
        logger.error(f"Failed to backup vision analysis: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"An unexpected error occurred during backup: {e}")
        return None

def load_vision_analysis_history() -> list:
    """Load all vision analysis history from backups."""
    if not DATA_DIR.exists():
        return []

    vision_history = []
    for file_path in DATA_DIR.glob("vision_*.json"):
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
                # Check for the expected structure before appending
                if isinstance(data, dict) and "analysis_record" in data:
                    vision_history.append(data["analysis_record"])
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not load or parse backup file {file_path.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {file_path.name}: {e}")
            
    # Sort history by timestamp from newest to oldest
    vision_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return vision_history

def export_vision_analysis_data():
    """Export all vision analysis data as JSON"""
    try:
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "export_type": "vision_analysis_complete",
            "session_data": st.session_state.vision_history,
            "backup_files": load_vision_analysis_history(),
            "total_analyses": len(st.session_state.vision_history),
            "export_format_version": "1.0"
        }
        
        export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
        return export_json
        
    except Exception as e:
        logger.error(f"Error exporting vision analysis data: {e}")
        return None

def main():
    """Main Vision AI application"""
    
    # Initialize session
    initialize_session()
    
    vision_ai = VisionAI()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## 👁️ Vision AI Settings")
        
        # Model selection - only multimodal models
        current_model = st.session_state.vision_agent.client.config.model
        
        # Force multimodal model if not already selected
        if current_model not in MULTIMODAL_MODELS:
            current_model = DEFAULT_MODEL
            st.session_state.vision_agent.client.config.model = current_model
        
        selected_model = st.selectbox(
            "**Vision Model:**",
            options=list(MULTIMODAL_MODELS.keys()),
            index=list(MULTIMODAL_MODELS.keys()).index(current_model),
            format_func=lambda x: MULTIMODAL_MODELS[x],
            help="Only multimodal models support image analysis"
        )
        
        if selected_model != current_model:
            st.session_state.vision_agent.client.config.model = selected_model
            st.success(f"Switched to {MULTIMODAL_MODELS[selected_model]}")
        
        st.info("🖼️ **Multimodal AI Ready**\nUpload images for AI analysis")
        
        # Analysis type
        analysis_types = [
            "General Analysis",
            "Code Analysis", 
            "Design Review",
            "Object Detection",
            "Technical Analysis",
            "Creative Description"
        ]
        
        analysis_type = st.selectbox(
            "**Analysis Type:**",
            options=analysis_types,
            help="Choose the type of analysis to perform"
        )
        
        # OpenCV features
        st.markdown("### 🔬 Computer Vision")
        use_opencv = st.checkbox("Enable OpenCV Analysis", value=True)
        
        if use_opencv:
            st.info("📊 **Technical Analysis**\n- Image properties\n- Edge detection\n- Blur analysis\n- Color analysis")
        
        # Session info
        st.markdown("### 📊 Session Info")
        st.metric("Analyses", len(st.session_state.vision_history))
        
        # Backup management
        st.markdown("### 💾 Backup Management")
        backup_dir = DATA_DIR
        vision_backup_files = []
        if os.path.exists(backup_dir):
            vision_backup_files = [f for f in os.listdir(backup_dir) if f.startswith('vision_') and f.endswith('.json')]
        
        st.metric("Backup Files", len(vision_backup_files))
        
        if st.button("🔄 Reload from Backups"):
            st.session_state.vision_history = load_vision_analysis_history()
            st.success(f"Loaded {len(st.session_state.vision_history)} analyses from backups!")
        
        # Export functionality
        if st.session_state.vision_history:
            export_data = export_vision_analysis_data()
            if export_data:
                st.download_button(
                    label="📥 Export Analysis Data",
                    data=export_data,
                    file_name=f"vision_analysis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    help="Download all vision analysis data as JSON"
                )
        
        if st.button("🗑️ Clear History"):
            st.session_state.vision_history = []
            st.success("History cleared!")
    
    # Main content
    st.markdown('<h1 class="main-header">👁️ Vision AI - Image Understanding</h1>', unsafe_allow_html=True)
    st.markdown("### 🖼️ Upload and analyze images with AI-powered computer vision")
    
    # File upload
    uploaded_file = st.file_uploader(
        "**Choose an image file**",
        type=vision_ai.supported_formats,
        help=f"Supported formats: {', '.join(vision_ai.supported_formats).upper()}\nMax size: 10MB"
    )
    
    if uploaded_file is not None:
        # Validate file size
        if uploaded_file.size > vision_ai.max_file_size:
            st.error(f"File too large! Maximum size is {vision_ai.max_file_size / (1024*1024):.1f}MB")
            return
        
        # Display uploaded image
        try:
            image = validate_uploaded_image(uploaded_file)
            if image is None:
                return
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(image, caption=f"📁 {uploaded_file.name}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Get OpenCV data first if needed
                opencv_data = None
                if use_opencv:
                    opencv_data = vision_ai.process_with_opencv(image)
                
                # Display comprehensive image info including technical analysis
                display_image_info(uploaded_file, image, opencv_data)
            
            # Analysis controls
            st.markdown("### 🤖 AI Analysis")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                custom_prompt = st.text_input(
                    "Custom prompt (optional):",
                    placeholder="Ask something specific about this image...",
                    help="Leave empty to use the selected analysis type"
                )
            
            with col2:
                analyze_button = st.button("🔍 Analyze Image", type="primary")
            
            # Perform analysis
            if analyze_button:
                with st.spinner("🖼️ Analyzing image with AI..."):
                    try:
                        # Prepare the prompt
                        if custom_prompt.strip():
                            prompt = custom_prompt
                        else:
                            opencv_data = vision_ai.process_with_opencv(image) if use_opencv else {}
                            prompt = vision_ai.get_analysis_prompt(analysis_type, opencv_data)
                        
                        # Encode image for API
                        image_b64 = vision_ai.encode_image_to_base64(image)
                        
                        # Create message with image
                        message_with_image = {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                            ]
                        }
                        
                        # Get AI analysis
                        response = st.session_state.vision_agent.chat_sync(
                            message_with_image, 
                            st.session_state.vision_session_id
                        )
                        
                        # Display results
                        st.markdown('<div class="analysis-result">', unsafe_allow_html=True)
                        st.markdown("### 🎯 AI Analysis Results")
                        st.write(response)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Save to history
                        analysis_record = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'filename': uploaded_file.name,
                            'analysis_type': analysis_type if not custom_prompt.strip() else "Custom",
                            'prompt': prompt,
                            'response': response,
                            'model': selected_model,
                            'opencv_data': opencv_data,
                            'image_size': f"{image.width}x{image.height}",
                            'file_size': uploaded_file.size
                        }
                        st.session_state.vision_history.append(analysis_record)
                        
                        # Automatic backup to data directory
                        backup_path = save_vision_analysis_backup(analysis_record, st.session_state.vision_session_id)
                        
                        logger.info(f"Vision analysis completed for {uploaded_file.name}")
                        
                        # Success feedback with backup info
                        if backup_path:
                            st.success(f"✅ Analysis completed and backed up to `{os.path.basename(backup_path)}`")
                        else:
                            st.success("✅ Analysis completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        logger.error(f"Vision analysis error: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            logger.error(f"Image loading error: {str(e)}")
    
    else:
        # Show features when no image is uploaded
        st.markdown("### 🌟 Vision AI Capabilities")
        
        # Render all feature cards using helper function
        render_feature_cards()
    
    # Analysis history
    if st.session_state.vision_history:
        st.markdown("### 📚 Analysis History")
        
        for i, record in enumerate(reversed(st.session_state.vision_history[-5:])):  # Show last 5
            with st.expander(f"📷 {record['filename']} - {record['analysis_type']} ({record['timestamp']})"):
                # Display record metadata using helper function
                record_metadata = {
                    "Model": record['model'],
                    "Prompt": f"{record['prompt'][:100]}...",
                    "Response": f"{record['response'][:200]}..."
                }
                display_metadata(record_metadata)
                
                if st.button(f"📥 Export Analysis", key=f"export_{i}"):
                    export_data = json.dumps(record, indent=2)
                    st.download_button(
                        "💾 Download JSON",
                        data=export_data,
                        file_name=f"vision_analysis_{record['timestamp'].replace(' ', '_').replace(':', '')}.json",
                        mime="application/json"
                    )
    
    # Export all vision analysis data
    st.markdown("### 📦 Export Vision Analysis Data")
    if st.button("Export All Vision Analysis Data"):
        export_json = export_vision_analysis_data()
        if export_json:
            st.download_button(
                "💾 Download Complete Vision Analysis Data",
                data=export_json,
                file_name=f"vision_analysis_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.error("Failed to export vision analysis data.")

if __name__ == "__main__":
    main()

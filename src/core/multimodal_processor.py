"""
Multi-modal AI processing utilities for handling images, audio, video, and documents
"""
import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import base64
import mimetypes
from datetime import datetime

# Import libraries for different media types
try:
    from PIL import Image, ImageEnhance
    import pytesseract
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logging.warning("Vision processing libraries not available. Install: pip install Pillow pytesseract")

try:
    import speech_recognition as sr
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio processing libraries not available. Install: pip install SpeechRecognition librosa")

try:
    import cv2
    import numpy as np
    import moviepy as mp
    from moviepy import VideoFileClip, AudioFileClip
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    logging.warning("Video processing libraries not available. Install: pip install opencv-python moviepy")

from config import ADVANCED_AI_CONFIG

logger = logging.getLogger(__name__)

class MultiModalProcessor:
    """Advanced multi-modal AI processor for handling various media types"""
    
    def __init__(self):
        self.config = ADVANCED_AI_CONFIG["multimodal"]
        self.supported_formats = self.config["supported_formats"]
        self.max_file_size = self.config["max_file_size_mb"] * 1024 * 1024  # Convert to bytes
        
    def validate_file(self, file_path: str) -> Tuple[bool, str, str]:
        """
        Validate if file is supported and safe to process
        
        Returns:
            Tuple[bool, str, str]: (is_valid, file_type, error_message)
        """
        if not os.path.exists(file_path):
            return False, "", "File not found"
        
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            return False, "", f"File too large. Maximum size: {self.config['max_file_size_mb']}MB"
        
        file_ext = Path(file_path).suffix.lower()
        
        # Determine file type
        for media_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return True, media_type, ""
        
        return False, "", f"Unsupported file format: {file_ext}"
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process image file with various AI analysis techniques
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing analysis results
        """
        if not VISION_AVAILABLE:
            return {"error": "Vision processing libraries not available"}
        
        try:
            # Load and analyze image
            image = Image.open(image_path)
            
            # Basic image information
            info = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "has_transparency": image.mode in ("RGBA", "LA") or "transparency" in image.info
            }
            
            # Extract text using OCR
            extracted_text = ""
            try:
                # Enhance image for better OCR
                enhanced_image = ImageEnhance.Contrast(image).enhance(2.0)
                extracted_text = pytesseract.image_to_string(enhanced_image)
            except Exception as e:
                logger.warning(f"OCR failed: {e}")
            
            # Detect potential code in the image
            code_patterns = self._detect_code_patterns(extracted_text)
            
            # Generate image description
            description = self._generate_image_description(image)
            
            return {
                "success": True,
                "type": "image",
                "info": info,
                "extracted_text": extracted_text.strip(),
                "code_detected": code_patterns,
                "description": description,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {"error": f"Image processing failed: {str(e)}"}
    
    def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Process audio file for speech-to-text and analysis
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dict containing analysis results
        """
        if not AUDIO_AVAILABLE:
            return {"error": "Audio processing libraries not available"}
        
        try:
            # Initialize speech recognizer
            recognizer = sr.Recognizer()
            
            # Load audio file
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
            
            # Speech-to-text conversion
            try:
                transcript = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                transcript = "Could not understand audio"
            except sr.RequestError as e:
                transcript = f"Speech recognition service error: {e}"
            
            # Audio analysis using librosa
            try:
                y, sr_rate = librosa.load(audio_path)
                duration = librosa.get_duration(y=y, sr=sr_rate)
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr_rate)
                
                audio_features = {
                    "duration": duration,
                    "sample_rate": sr_rate,
                    "tempo": float(tempo),
                    "beats_count": len(beats)
                }
            except Exception as e:
                logger.warning(f"Audio feature extraction failed: {e}")
                audio_features = {}
            
            return {
                "success": True,
                "type": "audio",
                "transcript": transcript,
                "features": audio_features,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return {"error": f"Audio processing failed: {str(e)}"}
    
    def process_video(self, video_path: str, frame_interval: int = 30) -> Dict[str, Any]:
        """
        Process video file by extracting frames and analyzing content
        
        Args:
            video_path: Path to the video file
            frame_interval: Extract every nth frame
            
        Returns:
            Dict containing analysis results
        """
        if not VIDEO_AVAILABLE:
            return {"error": "Video processing libraries not available"}
        
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Extract frames at intervals
            extracted_frames = []
            frame_analyses = []
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    # Save frame to temporary file for analysis
                    temp_frame_path = tempfile.mktemp(suffix='.jpg')
                    cv2.imwrite(temp_frame_path, frame)
                    
                    # Analyze frame as image
                    frame_analysis = self.process_image(temp_frame_path)
                    frame_analysis["timestamp"] = frame_idx / fps if fps > 0 else 0
                    frame_analyses.append(frame_analysis)
                    
                    # Clean up temporary file
                    os.unlink(temp_frame_path)
                    
                    extracted_frames.append({
                        "frame_index": frame_idx,
                        "timestamp": frame_idx / fps if fps > 0 else 0
                    })
                
                frame_idx += 1
            
            cap.release()
            
            return {
                "success": True,
                "type": "video",
                "properties": {
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration": duration,
                    "resolution": f"{width}x{height}"
                },
                "extracted_frames": extracted_frames,
                "frame_analyses": frame_analyses,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return {"error": f"Video processing failed: {str(e)}"}
    
    def process_document(self, doc_path: str) -> Dict[str, Any]:
        """
        Process document files (PDF, DOCX, etc.)
        
        Args:
            doc_path: Path to the document file
            
        Returns:
            Dict containing extracted content and analysis
        """
        try:
            file_ext = Path(doc_path).suffix.lower()
            extracted_text = ""
            
            if file_ext == '.txt' or file_ext == '.md':
                # Simple text files
                with open(doc_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            
            elif file_ext == '.pdf':
                # PDF processing (requires PyPDF2 or similar)
                try:
                    import PyPDF2
                    with open(doc_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            extracted_text += page.extract_text() + "\n"
                except ImportError:
                    return {"error": "PDF processing requires PyPDF2: pip install PyPDF2"}
            
            elif file_ext == '.docx':
                # DOCX processing (requires python-docx)
                try:
                    from docx import Document
                    doc = Document(doc_path)
                    for paragraph in doc.paragraphs:
                        extracted_text += paragraph.text + "\n"
                except ImportError:
                    return {"error": "DOCX processing requires python-docx: pip install python-docx"}
            
            # Analyze extracted text for code patterns
            code_patterns = self._detect_code_patterns(extracted_text)
            
            return {
                "success": True,
                "type": "document",
                "format": file_ext,
                "extracted_text": extracted_text.strip(),
                "code_detected": code_patterns,
                "word_count": len(extracted_text.split()),
                "line_count": len(extracted_text.splitlines()),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {"error": f"Document processing failed: {str(e)}"}
    
    def _detect_code_patterns(self, text: str) -> Dict[str, Any]:
        """Detect programming code patterns in text"""
        code_indicators = {
            "python": ["def ", "import ", "class ", "if __name__", "print(", "return "],
            "javascript": ["function ", "const ", "let ", "var ", "console.log", "=> "],
            "html": ["<html", "<div", "<script", "<!DOCTYPE"],
            "css": ["{", "}", ":", ";", "px", "%"],
            "sql": ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE"]
        }
        
        detected_languages = []
        total_indicators = 0
        
        for language, indicators in code_indicators.items():
            count = sum(1 for indicator in indicators if indicator in text)
            if count > 0:
                detected_languages.append({
                    "language": language,
                    "confidence": count / len(indicators),
                    "indicators_found": count
                })
                total_indicators += count
        
        return {
            "has_code": total_indicators > 0,
            "detected_languages": sorted(detected_languages, key=lambda x: x["confidence"], reverse=True),
            "total_code_indicators": total_indicators
        }
    
    def _generate_image_description(self, image: Image.Image) -> str:
        """Generate a basic description of the image"""
        width, height = image.size
        aspect_ratio = width / height
        
        # Basic color analysis
        colors = image.getcolors(maxcolors=256)
        dominant_color = "unknown"
        if colors:
            dominant_color = "light" if max(colors)[1] > 128 else "dark"
        
        # Basic scene classification
        if aspect_ratio > 1.5:
            orientation = "wide landscape"
        elif aspect_ratio < 0.7:
            orientation = "portrait"
        else:
            orientation = "square or balanced"
        
        return f"A {dominant_color} {orientation} image with dimensions {width}x{height} pixels"

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main processing function that determines file type and processes accordingly
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dict containing processing results
        """
        # Validate file first
        is_valid, file_type, error_msg = self.validate_file(file_path)
        if not is_valid:
            return {"error": error_msg}
        
        # Process based on file type
        if file_type == "images":
            return self.process_image(file_path)
        elif file_type == "audio":
            return self.process_audio(file_path)
        elif file_type == "video":
            return self.process_video(file_path)
        elif file_type == "documents":
            return self.process_document(file_path)
        else:
            return {"error": f"Processing not implemented for file type: {file_type}"}

#!/usr/bin/env python3
"""
Installation validation script for SilentCodingLegend AI Agent
"""
import sys

def check_imports():
    """Check if all critical dependencies can be imported"""
    import sys
    failed_imports = []
    
    # Critical dependencies
    dependencies = [
        'streamlit',
        'httpx', 
        'requests',
        'pydantic',
        'cv2',  # opencv-python
        'PIL',  # Pillow
        'numpy',
        'pandas',
        'sklearn',  # scikit-learn
        'matplotlib',
        'nltk',
        'plotly',
        'bleach',
        'aiohttp',
        'bs4',  # beautifulsoup4
    ]
    
    print("🔍 Checking critical dependencies...")
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError as e:
            print(f"❌ {dep}: {e}")
            failed_imports.append(dep)
    
    # Optional dependencies (don't fail if missing)
    optional_deps = [
        'torch',
        'transformers', 
        'chromadb',
        'langchain',
    ]
    
    print("\n🔍 Checking optional dependencies...")
    
    for dep in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"⚠️  {dep} (optional)")
    
    if failed_imports:
        print(f"\n❌ Installation incomplete. Failed imports: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n🎉 All critical dependencies installed successfully!")
        return True

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)

"""
Coding Assistant Configuration Module
Centralized configuration for the coding assistant application
"""
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from datetime import datetime

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "conversations"

# Available AI models for coding assistance
AVAILABLE_MODELS = {
    "Llama-3.3-70B-Instruct": "Llama 3.3 70B (Recommended - Text only)",
    "Llama-3.3-8B-Instruct": "Llama 3.3 8B (Fast - Text only)", 
    "Llama-4-Scout-17B-16E-Instruct-FP8": "Llama 4 Scout (Multimodal - Text + Images)",
    "Llama-4-Maverick-17B-128E-Instruct-FP8": "Llama 4 Maverick (Advanced - Text only)",
    "Llama-3.2-90B-Vision-Instruct": "Llama 3.2 90B Vision (Multimodal - Text + Images)",
    "Llama-3.2-11B-Vision-Instruct": "Llama 3.2 11B Vision (Compact Multimodal)",
    "Llama-3.1-405B-Instruct": "Llama 3.1 405B (Flagship - Text only)",
    "Llama-3.1-70B-Instruct": "Llama 3.1 70B (Balanced - Text only)",
    "Llama-3.1-8B-Instruct": "Llama 3.1 8B (Fast - Text only)"
}

# Supported programming languages
SUPPORTED_LANGUAGES = [
    "python", "javascript", "typescript", "java", "cpp", "c", "csharp",
    "go", "rust", "php", "ruby", "swift", "kotlin", "scala", "r",
    "sql", "html", "css", "bash", "yaml", "json", "xml", "markdown"
]

# Coding templates for quick start
CODING_TEMPLATES = {
    "API Endpoint": "Create a REST API endpoint",
    "Data Analysis": "Analyze and visualize data",
    "Algorithm": "Implement a specific algorithm",
    "Database Query": "Write SQL queries for data retrieval",
    "Unit Tests": "Create comprehensive unit tests",
    "Class Design": "Design object-oriented classes",
    "Function": "Create a specific function",
    "Bug Fix": "Fix a specific bug or issue",
    "Optimization": "Optimize existing code for performance",
    "Documentation": "Add documentation to existing code"
}

# Code review aspects
REVIEW_ASPECTS = [
    "Code Quality", "Security", "Performance", "Best Practices",
    "Documentation", "Testing", "Maintainability", "Design Patterns",
    "Error Handling", "Type Safety", "Resource Management", "Scalability"
]

# Data science templates
DATA_SCIENCE_TEMPLATES = {
    "Data Cleaning": "Clean and preprocess raw data",
    "Exploratory Analysis": "Perform exploratory data analysis",
    "Machine Learning": "Build and train ML models",
    "Data Visualization": "Create data visualizations",
    "Statistical Analysis": "Perform statistical analysis",
    "Feature Engineering": "Engineer features for ML",
    "Model Evaluation": "Evaluate model performance",
    "Time Series": "Analyze time series data"
}

# Data science examples for quick start
DATA_SCIENCE_EXAMPLES = {
    "pandas": "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())",
    "matplotlib": "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3], [4, 5, 6])\nplt.show()",
    "sklearn": "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)",
    "numpy": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nprint(arr.mean())",
    "seaborn": "import seaborn as sns\nsns.scatterplot(data=df, x='x', y='y')"
}

@dataclass
class SessionData:
    """Data structure for coding session information"""
    timestamp: str
    type: str
    language: str
    session_id: str
    response: Optional[str] = None
    description: Optional[str] = None
    code_input: Optional[str] = None
    review_aspects: List[str] = field(default_factory=list)
    templates: List[str] = field(default_factory=list)
    complexity: Optional[str] = None
    features: List[str] = field(default_factory=list)
    reasoning_type: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

def get_language_info(language: str) -> Dict[str, str]:
    """Get language-specific information and features"""
    language_info = {
        "python": {
            "extension": ".py",
            "comment": "#",
            "description": "Versatile programming language for data science and web development",
            "features": ["Object-Oriented", "Dynamic Typing", "Rich Libraries", "Data Science"],
            "use_cases": ["Web Development", "Data Science", "AI/ML", "Automation"],
            "icon": "🐍"
        },
        "javascript": {
            "extension": ".js",
            "comment": "//",
            "description": "Dynamic language for web development and modern applications",
            "features": ["Dynamic", "Event-Driven", "Asynchronous", "Functional"],
            "use_cases": ["Web Development", "Frontend", "Backend (Node.js)", "Mobile Apps"],
            "icon": "📄"
        },
        "typescript": {
            "extension": ".ts",
            "comment": "//",
            "description": "Statically typed superset of JavaScript for large applications",
            "features": ["Static Typing", "Modern ES Features", "Object-Oriented", "Compiled"],
            "use_cases": ["Large Applications", "Enterprise", "Angular", "React"],
            "icon": "🔷"
        },
        "java": {
            "extension": ".java",
            "comment": "//",
            "description": "Enterprise-grade object-oriented programming language",
            "features": ["Object-Oriented", "Platform Independent", "Strong Typing", "Enterprise"],
            "use_cases": ["Enterprise Applications", "Android", "Backend Services", "Desktop Apps"],
            "icon": "☕"
        },
        "cpp": {
            "extension": ".cpp",
            "comment": "//",
            "description": "High-performance systems programming language",
            "features": ["High Performance", "System Programming", "Object-Oriented", "Low-Level"],
            "use_cases": ["System Programming", "Game Development", "Embedded", "Performance Critical"],
            "icon": "⚡"
        },
        "c": {
            "extension": ".c",
            "comment": "//",
            "description": "Low-level procedural programming language",
            "features": ["Procedural", "Low-Level", "Fast", "Portable"],
            "use_cases": ["System Programming", "Embedded", "Operating Systems", "Drivers"],
            "icon": "🔧"
        },
        "csharp": {
            "extension": ".cs",
            "comment": "//",
            "description": "Microsoft's object-oriented programming language",
            "features": ["Object-Oriented", "Type Safe", ".NET Framework", "Garbage Collection"],
            "use_cases": ["Windows Applications", "Web Development", "Games", "Enterprise"],
            "icon": "🔷"
        },
        "go": {
            "extension": ".go",
            "comment": "//",
            "description": "Simple and efficient language for cloud and network services",
            "features": ["Concurrent", "Simple", "Fast Compilation", "Static Typing"],
            "use_cases": ["Microservices", "Cloud Native", "Backend Services", "DevOps Tools"],
            "icon": "🔵"
        },
        "rust": {
            "extension": ".rs",
            "comment": "//",
            "description": "Memory-safe systems programming language",
            "features": ["Memory Safety", "Zero-Cost Abstractions", "Performance", "Concurrent"],
            "use_cases": ["System Programming", "WebAssembly", "Blockchain", "Performance Critical"],
            "icon": "🦀"
        },
        "php": {
            "extension": ".php",
            "comment": "//",
            "description": "Server-side scripting language for web development",
            "features": ["Dynamic", "Web-Focused", "Easy to Learn", "Server-Side"],
            "use_cases": ["Web Development", "Server Scripting", "CMS", "E-commerce"],
            "icon": "🐘"
        },
        "ruby": {
            "extension": ".rb",
            "comment": "#",
            "description": "Dynamic, object-oriented scripting language",
            "features": ["Object-Oriented", "Dynamic", "Expressive", "Productive"],
            "use_cases": ["Web Development", "Scripting", "Automation", "Prototyping"],
            "icon": "💎"
        },
        "swift": {
            "extension": ".swift",
            "comment": "//",
            "description": "Apple's modern programming language for iOS and macOS",
            "features": ["Safe", "Fast", "Modern", "Expressive"],
            "use_cases": ["iOS Development", "macOS Apps", "Server-Side", "Cross-Platform"],
            "icon": "🦉"
        },
        "kotlin": {
            "extension": ".kt",
            "comment": "//",
            "description": "Modern JVM language, fully interoperable with Java",
            "features": ["Concise", "Safe", "Interoperable", "Tool-Friendly"],
            "use_cases": ["Android Development", "Server-Side", "Web Development", "Desktop Apps"],
            "icon": "🟣"
        },
        "scala": {
            "extension": ".scala",
            "comment": "//",
            "description": "Functional and object-oriented language for the JVM",
            "features": ["Functional", "Object-Oriented", "Scalable", "Type Safe"],
            "use_cases": ["Big Data", "Web Services", "Distributed Systems", "Analytics"],
            "icon": "🔺"
        },
        "r": {
            "extension": ".r",
            "comment": "#",
            "description": "Statistical computing and data analysis language",
            "features": ["Statistical", "Data Analysis", "Visualization", "Functional"],
            "use_cases": ["Data Science", "Statistics", "Research", "Bioinformatics"],
            "icon": "📊"
        },
        "sql": {
            "extension": ".sql",
            "comment": "--",
            "description": "Declarative language for managing relational databases",
            "features": ["Declarative", "Set-Based", "ACID Compliance", "Relational"],
            "use_cases": ["Database Queries", "Data Analysis", "Reporting", "ETL"],
            "icon": "🗃️"
        },
        "html": {
            "extension": ".html",
            "comment": "<!--",
            "description": "Markup language for creating web pages",
            "features": ["Markup", "Web Standard", "Semantic", "Accessible"],
            "use_cases": ["Web Pages", "Documentation", "Email Templates", "UI Structure"],
            "icon": "🌐"
        },
        "css": {
            "extension": ".css",
            "comment": "/*",
            "description": "Style sheet language for describing web page presentation",
            "features": ["Styling", "Responsive", "Animations", "Layout"],
            "use_cases": ["Web Styling", "Responsive Design", "UI/UX", "Print Styles"],
            "icon": "🎨"
        },
        "bash": {
            "extension": ".sh",
            "comment": "#",
            "description": "Unix shell and command language",
            "features": ["Scripting", "System Admin", "Automation", "Command Line"],
            "use_cases": ["System Administration", "Automation", "DevOps", "Build Scripts"],
            "icon": "🐚"
        },
        "yaml": {
            "extension": ".yaml",
            "comment": "#",
            "description": "Human-readable data serialization standard",
            "features": ["Human-Readable", "Data Serialization", "Configuration", "Indentation-Based"],
            "use_cases": ["Configuration", "CI/CD", "Docker Compose", "Kubernetes"],
            "icon": "📄"
        },
        "json": {
            "extension": ".json",
            "comment": "",
            "description": "Lightweight data interchange format",
            "features": ["Lightweight", "Human-Readable", "Language Independent", "Web Standard"],
            "use_cases": ["Data Exchange", "Configuration", "APIs", "Storage"],
            "icon": "📋"
        },
        "xml": {
            "extension": ".xml",
            "comment": "<!--",
            "description": "Extensible markup language for structured data",
            "features": ["Structured", "Self-Describing", "Extensible", "Platform Independent"],
            "use_cases": ["Data Exchange", "Configuration", "Web Services", "Document Structure"],
            "icon": "📰"
        },
        "markdown": {
            "extension": ".md",
            "comment": "<!--",
            "description": "Lightweight markup language for formatting text",
            "features": ["Simple", "Readable", "Portable", "Web-Friendly"],
            "use_cases": ["Documentation", "README Files", "Blogs", "Technical Writing"],
            "icon": "📝"
        }
    }
    
    return language_info.get(language, {
        "extension": f".{language}",
        "comment": "//",
        "description": "General purpose programming language",
        "features": ["General Purpose"],
        "use_cases": ["Software Development"],
        "icon": "💻"
    })

def get_complexity_levels() -> List[str]:
    """Get available complexity levels for code generation"""
    return ["Beginner", "Intermediate", "Advanced", "Expert"]

def get_reasoning_types() -> Dict[str, str]:
    """Get available reasoning types for chain-of-thought"""
    return {
        "chain_of_thought": "🔗 Step-by-step reasoning",
        "react": "🔄 Reasoning + Acting",
        "reflection": "🪞 Self-critique and improvement",
        "tree_of_thought": "🌳 Explore multiple paths",
        "loop_of_thought": "🔄 Iterative refinement"
    }

def load_coding_history() -> List[Dict]:
    """Load coding session history from JSON files"""
    import json
    import os
    from datetime import datetime
    
    history = []
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all JSON files from conversations directory
    conversations_dir = Path(DATA_DIR)
    if conversations_dir.exists():
        for json_file in conversations_dir.glob("coding_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    history.append(session_data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                # Log error but continue loading other files
                continue
    
    # Sort by timestamp (newest first)
    history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return history

def save_coding_session(session_data: Dict, session_id: str) -> bool:
    """Save coding session data to JSON file"""
    import json
    
    try:
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = session_data.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
        filename = f"coding_{timestamp}.json"
        filepath = DATA_DIR / filename
        
        # Save session data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        # Log error but don't raise exception
        return False

def get_session_data_template(session_type: str, language: str) -> SessionData:
    """Create a SessionData template for a given session type and language"""
    return SessionData(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        type=session_type,
        language=language,
        session_id=f"{session_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

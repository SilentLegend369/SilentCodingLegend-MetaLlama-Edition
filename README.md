# SilentCodingLegend AI Agent 🤖

A powerful, multi-modal AI agent built with Streamlit, featuring advanced capabilities including vision AI, plugin system, knowledge management, and chain-of-thought reasoning.

## 🌟 Features

### Core Capabilities
- **🧠 Advanced AI Agent** - Powered by Meta Llama models with Chain-of-Thought reasoning
- **👁️ Vision AI** - Multi-modal image understanding and analysis
- **🔌 Plugin System** - Extensible architecture with web search, file operations, and more
- **📚 Knowledge Management** - Advanced memory and knowledge graph capabilities
- **🛠️ Tool Agent** - Interactive tool testing and execution interface
- **💬 Chat Interface** - Streamlit-based conversational AI interface

### Specialized Features
- **🔍 Web Search & News** - Real-time web and news search capabilities
- **📊 Analytics Dashboard** - Usage analytics and insights
- **🗂️ File Management** - Advanced file system operations
- **🔐 Security Features** - Input sanitization and security auditing
- **💾 Backup System** - Automated backup and restore functionality
- **📈 Enhanced Memory** - Semantic search and conversation management

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment recommended

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd scl-llamaapi
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** Audio processing dependencies are optional and commented out by default.
   Uncomment them in `requirements.txt` if you need audio capabilities.

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📖 Optional Dependencies

### Audio Processing
If you need audio capabilities, uncomment the audio dependencies in `requirements.txt` and install system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-dev gcc
```

**CentOS/RHEL:**
```bash
sudo yum install portaudio-devel python3-devel gcc
```

**macOS:**
```bash
brew install portaudio
```

### Development Tools
For development, uncomment the development dependencies in `requirements.txt`.

## 📖 Documentation

For detailed documentation, see the `/summaries/` directory:
- **[Installation Guide](summaries/INSTALLATION.md)** - Comprehensive setup instructions
- **[External Access Guide](summaries/EXTERNAL_ACCESS_GUIDE.md)** - Network access and deployment
- **[Knowledge Management Guide](summaries/KNOWLEDGE_MANAGEMENT_ENHANCED.md)** - Advanced knowledge features
- **[Project Architecture](summaries/COMPLETE_PROJECT_ARCHITECTURE.md)** - Technical overview
- **[Quick Reference](summaries/QUICK_REFERENCE_GUIDE.md)** - Common commands and usage

## 🏗️ Project Structure

```
scl-llamaapi/
├── 📱 streamlit_app.py          # Main Streamlit application
├── 📄 pages/                    # Streamlit pages
│   ├── Knowledge_Management.py  # Knowledge management interface
│   ├── Plugin_Manager.py        # Plugin management interface
│   ├── Tool_Agent.py           # Tool testing interface
│   ├── Vision_Ai.py            # Vision AI interface
│   ├── Analytics_View.py       # Analytics dashboard
│   └── Chat_History.py         # Chat history viewer
├── 🧠 src/                     # Core source code
│   ├── api/                    # API clients and interfaces
│   ├── core/                   # Core agent and reasoning logic
│   ├── config/                 # Configuration modules
│   ├── plugins/                # Plugin system
│   ├── ui/                     # UI components
│   └── utils/                  # Utility functions
├── 🔌 plugins/                 # Plugin implementations
│   ├── core/                   # Core plugins
│   ├── community/              # Community plugins
│   └── custom/                 # Custom plugins
├── 🧪 tests/                   # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── 📊 data/                    # Data storage
├──  marketplace/             # Plugin marketplace
├── 📋 summaries/               # Documentation and guides
├── 🔧 scripts/                 # Utility scripts
└── 📦 requirements.txt         # Dependencies
```

## 🔧 Configuration

The application uses multiple configuration approaches:

- **Environment Variables** - API keys and sensitive settings (`.env`)
- **Configuration Files** - Application settings (`config/`)
- **Plugin Configuration** - Plugin-specific settings (`plugins/config.json`)

## 🔌 Plugin System

The agent features a powerful plugin architecture:

### Core Plugins
- **WebSearch** - Web and news search capabilities
- **FileSystemTools** - File operations and management
- **ChainOfThought** - Advanced reasoning tools
- **BackupManager** - Data backup and restore

### Plugin Development
Plugins follow a standardized interface defined in `src/plugins/base_plugin.py`. See the plugin development guide for creating custom plugins.

## 🧠 AI Capabilities

### Chain-of-Thought Reasoning
Advanced reasoning capabilities including:
- Step-by-step analysis
- Problem decomposition
- Reasoning reflection
- Loop-of-thought processing

### Vision AI
Multi-modal capabilities for:
- Image analysis and understanding
- Code analysis from screenshots
- Design review and critique
- Object detection and technical analysis

### Memory Management
Enhanced memory features:
- Conversation history management
- Semantic search across interactions
- Knowledge graph construction
- Context-aware responses

## 🔒 Security Features

- **Input Sanitization** - XSS protection using bleach
- **Security Auditing** - Comprehensive security logging
- **Safe Plugin Execution** - Sandboxed plugin environment
- **Data Protection** - Secure data handling and storage

## 📊 Analytics

Built-in analytics for:
- Usage patterns and trends
- Plugin performance metrics
- User interaction insights
- System health monitoring

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage
python -m pytest --cov=src tests/
```

## 📚 Documentation

- [Installation Guide](summaries/INSTALLATION.md) - Detailed setup instructions
- [External Access Guide](summaries/EXTERNAL_ACCESS_GUIDE.md) - Network configuration
- [Complete Documentation](summaries/) - Full documentation index
- [Project Architecture](summaries/COMPLETE_PROJECT_ARCHITECTURE.md) - Technical overview

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Project Repository**: [GitHub](https://github.com/your-username/scl-llamaapi)
- **Documentation**: [Docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/scl-llamaapi/issues)

## 🙏 Acknowledgments

- Meta AI for the Llama model architecture
- Streamlit for the web application framework
- The open-source community for various dependencies

---

**Built with ❤️ by SilentCodingLegend**

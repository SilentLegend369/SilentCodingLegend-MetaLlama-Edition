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
![Screenshot From 2025-06-15 11-07-11](https://github.com/user-attachments/assets/ac4e1d1b-dc91-44d1-97c1-fd001e2f0010)
![Screenshot From 2025-06-15 11-07-08](https://github.com/user-attachments/assets/6c21a816-c53d-421c-8cf4-02221bda986d)
![Screenshot From 2025-06-15 11-07-01](https://github.com/user-attachments/assets/e6201eb5-4af5-427b-9274-f2ba88d72013)
![Screenshot From 2025-06-15 11-06-54](https://github.com/user-attachments/assets/0ac526c3-82de-4ccd-90e5-24dbf6c6df1b)
![Screenshot From 2025-06-15 11-06-45](https://github.com/user-attachments/assets/0cfdc163-50b0-4bf6-b8c0-e9872d2dae16)
![Screenshot From 2025-06-15 11-06-34](https://github.com/user-attachments/assets/547dcb20-e5e1-489e-8b9b-9a23d27dd0c7)
![Screenshot From 2025-06-15 11-06-22](https://github.com/user-attachments/assets/2b8045dc-4f5d-4e3a-b279-44df8e9236f8)
![Screenshot From 2025-06-15 11-06-18](https://github.com/user-attachments/assets/7d165113-d269-4967-806c-958c0845897b)
![Screenshot From 2025-06-15 11-06-11](https://github.com/user-attachments/assets/29dcb967-af4d-4d59-b900-3539a93fd7d9)
![Screenshot From 2025-06-15 11-06-07](https://github.com/user-attachments/assets/4734f11a-484f-485f-b934-80c9ccbe7bbf)
![Screenshot From 2025-06-15 11-06-03](https://github.com/user-attachments/assets/03a7a6c8-6780-42c0-b982-ed50f4e90a45)
![Screenshot From 2025-06-15 11-05-52](https://github.com/user-attachments/assets/c2f50437-daa0-4773-9dd0-6b89087c293e)
![Screenshot From 2025-06-15 11-05-48](https://github.com/user-attachments/assets/4cb0422c-b38c-4e76-a63a-babc7b6ebf9f)
![Screenshot From 2025-06-15 11-05-40](https://github.com/user-attachments/assets/507b568c-4431-479d-b1dc-40744343fc9b)
![Screenshot From 2025-06-15 11-05-36](https://github.com/user-attachments/assets/8d041bbc-24d7-4c74-aaf9-a1aaffe7c524)
![Screenshot From 2025-06-15 11-05-31](https://github.com/user-attachments/assets/f3f096ef-1ae2-457c-99a3-f37e93a64824)
![Screenshot From 2025-06-15 11-05-24](https://github.com/user-attachments/assets/37f026f2-a19d-4ca5-b682-994abb540903)
![Screenshot From 2025-06-15 11-05-17](https://github.com/user-attachments/assets/e1c29bba-842d-4bde-b5c3-d60943545b9d)
![Screenshot From 2025-06-15 11-04-20](https://github.com/user-attachments/assets/3a7fbb29-229d-46bc-ad9e-9942e14428ff)
![Screenshot From 2025-06-15 11-03-53](https://github.com/user-attachments/assets/1b3af561-3347-4cdf-9f01-2d38aa747848)
![Screenshot From 2025-06-15 11-03-42](https://github.com/user-attachments/assets/1aa932e3-8bea-40f1-9cbb-eab776496f9c)


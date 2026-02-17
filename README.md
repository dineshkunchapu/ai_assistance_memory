# 🤖 AI Assistant with Memory

A sophisticated conversational AI system with contextual memory management built using Python and Streamlit.

## 📋 Project Overview

This AI Assistant features persistent memory capabilities that allow it to remember user preferences, maintain conversation context, and provide personalized responses across multiple sessions. The system implements session-based state management for seamless user experience.

## ✨ Key Features

### Core Capabilities
- 💬 **Contextual Conversations**: Maintains conversation flow with context awareness
- 🧠 **Persistent Memory**: Stores important information across sessions
- 👤 **User Profiling**: Learns and remembers user preferences
- 📊 **Session Analytics**: Tracks conversation statistics and metrics
- 📤 **Export Options**: Export conversations in Markdown, JSON, or Text formats
- 🔄 **Session Management**: Save, load, and manage multiple conversation sessions

### Technical Features
- Session-based state management using Streamlit
- Modular architecture with separated concerns
- Memory categorization (short-term vs long-term)
- Intelligent memory retrieval with relevance scoring
- Conversation summarization capabilities
- File-based persistence (JSON storage)

## 🏗️ Architecture

```
ai-assistant-memory/
│
├── app.py                      # Main Streamlit application
├── memory_manager.py           # Memory storage and retrieval logic
├── conversation_handler.py     # Response generation and intent detection
├── utils.py                    # Utility functions for export/formatting
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
│
├── memory_store.json          # Long-term memory storage (auto-generated)
├── sessions/                  # Saved conversation sessions (auto-generated)
│   └── session_*.json
└── backups/                   # Session backups (auto-generated)
    └── backup_*.json
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project**
```bash
cd ai-assistant-memory
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Access the application**
   - The app will open automatically in your browser
   - Default URL: `http://localhost:8501`

## 💻 Usage Guide

### Basic Interactions

**Starting a Conversation:**
```
User: Hello!
Assistant: Hello! How can I assist you today?
```

**Storing Information:**
```
User: Remember that I prefer Python for coding projects
Assistant: Got it! I've noted your preference...
```

**Recalling Information:**
```
User: What do you know about me?
Assistant: Here's what I remember:
1. You prefer Python for coding projects
   (Stored on: 2024-XX-XX)
```

**Getting Help:**
```
User: What can you do?
Assistant: I'm an AI Assistant with Memory! Here's what I can do...
```

### Advanced Features

#### Session Management
- **New Session**: Start fresh while preserving old conversations
- **Clear Chat**: Clear current conversation
- **Export**: Download conversation history

#### Memory Browser
- View stored memories in the sidebar
- Track memory usage and statistics
- Monitor conversation metrics

#### User Profile
- Set your name for personalized responses
- View your preferences and stored information
- Track session details

## 🎯 Use Cases

1. **Personal Assistant**: Remember tasks, preferences, and important information
2. **Learning Companion**: Track topics discussed and learning progress
3. **Interview Preparation**: Practice conversations with context retention
4. **Note-Taking**: Store and recall important points from discussions
5. **Project Planning**: Maintain project context across multiple sessions

## 🧩 Core Components

### 1. Memory Manager (`memory_manager.py`)
Handles all memory operations:
- Short-term memory (current session)
- Long-term memory (persistent storage)
- Memory retrieval with relevance scoring
- Session saving and loading
- Automatic memory categorization

### 2. Conversation Handler (`conversation_handler.py`)
Manages conversation flow:
- Intent detection (greeting, memory storage, recall, etc.)
- Context-aware response generation
- User profile integration
- Template-based responses

### 3. Utilities (`utils.py`)
Helper functions for:
- Export in multiple formats (Markdown, JSON, Text)
- Session statistics calculation
- Data validation
- Backup creation

### 4. Main Application (`app.py`)
Streamlit interface providing:
- Chat interface with message history
- Sidebar controls and statistics
- Real-time session management
- Export functionality

## 📊 Features Breakdown

### Memory System
```python
# Memory types
- user_input: User messages
- assistant_response: AI responses
- preference: User preferences
- user_info: General user information
```

### Intent Detection
The system recognizes:
- Greetings
- Memory storage requests
- Memory recall queries
- Summarization requests
- Help requests
- Profile queries
- General queries

### Export Formats

**Markdown**: Formatted conversation with headers and metadata
**JSON**: Structured data with full message history
**Text**: Plain text conversation transcript

## 🔧 Customization

### Modify Response Templates
Edit `conversation_handler.py`:
```python
self.response_templates = {
    'greeting': ["Your custom greeting"],
    # Add more templates
}
```

### Adjust Memory Window
Edit `memory_manager.py`:
```python
self.context_window = 10  # Change to desired size
```

### Add New Intents
Add pattern matching in `conversation_handler.py`:
```python
def _detect_intent(self, user_input: str) -> str:
    # Add new intent patterns
    if 'your_pattern' in input_lower:
        return 'your_intent'
```

## 📈 Performance Metrics

- **Memory Efficiency**: Stores only important information in long-term memory
- **Response Time**: Instant responses for most queries
- **Scalability**: Handles hundreds of messages per session
- **Storage**: Minimal disk usage with JSON-based storage

## 🛠️ Technical Stack

- **Framework**: Streamlit 1.31.0
- **Language**: Python 3.8+
- **Storage**: JSON file-based persistence
- **Architecture**: Modular design with separation of concerns

## 🎓 Learning Outcomes

This project demonstrates:
1. ✅ Session-based state management
2. ✅ Modular architecture design
3. ✅ Memory management systems
4. ✅ Intent detection and NLP basics
5. ✅ File I/O and data persistence
6. ✅ UI/UX design with Streamlit
7. ✅ Software engineering best practices

## 🚧 Future Enhancements

Potential improvements:
- [ ] Integration with real LLM APIs (OpenAI, Anthropic)
- [ ] Vector database for semantic search
- [ ] Multi-user support with authentication
- [ ] Cloud storage integration
- [ ] Voice interaction capabilities
- [ ] Advanced analytics dashboard
- [ ] Mobile responsive design
- [ ] Docker containerization

## 📝 Project Structure Details

### Data Flow
1. User inputs message
2. Message stored in session state
3. Memory manager categorizes and stores
4. Conversation handler detects intent
5. Response generated with context
6. Response displayed and stored
7. Session persisted to disk

### Memory Hierarchy
```
Session State (RAM)
    ↓
Short-term Memory (Current Session)
    ↓
Long-term Memory (Persistent)
    ↓
JSON File Storage (Disk)
```

## 🤝 Contributing

To extend this project:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open-source and available for educational purposes.

## 👨‍💻 Author

**Dinesh Kunchapu**
- Email: chinnudinesh10@gmail.com
- LinkedIn: [linkedin.com/in/dinesh-k](https://linkedin.com/in/dinesh-k)
- GitHub: [github.com/dineshkunchapu](https://github.com/dineshkunchapu)

## 🙏 Acknowledgments

Built as a demonstration of:
- Conversational AI systems
- Memory management in AI applications
- Streamlit framework capabilities
- Python software engineering practices

---

**Note**: This is a foundational implementation. For production use, consider integrating actual LLM APIs (OpenAI GPT, Anthropic Claude, etc.) and implementing proper security measures.

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Contact via email: chinnudinesh10@gmail.com

---

*Built with ❤️ using Python and Streamlit*

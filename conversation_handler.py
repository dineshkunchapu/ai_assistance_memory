"""
Conversation Handler - Manages AI response generation
Handles context, memory retrieval, and response formatting
"""

from typing import List, Dict
from datetime import datetime
import re


class ConversationHandler:
    """Handles conversation flow and response generation"""
    
    def __init__(self):
        self.system_prompt = """You are a helpful AI assistant with memory capabilities. 
You can remember information from previous conversations and provide contextual responses.
You are friendly, professional, and always try to be helpful."""
        
        self.response_templates = {
            'greeting': [
                "Hello! How can I assist you today?",
                "Hi there! What can I help you with?",
                "Welcome back! What would you like to know?"
            ],
            'memory_query': [
                "Let me check what I remember...",
                "Based on our previous conversations...",
                "From what I recall..."
            ],
            'clarification': [
                "Could you please provide more details?",
                "I'd like to help, but I need more information.",
                "Can you clarify what you mean?"
            ]
        }
    
    def generate_response(
        self,
        user_input: str,
        conversation_history: List[Dict],
        memory_manager,
        user_profile: Dict
    ) -> str:
        """Generate AI response based on input and context"""
        
        # Detect intent
        intent = self._detect_intent(user_input)
        
        # Handle different types of queries
        if intent == 'greeting':
            return self._handle_greeting(user_profile)
        
        elif intent == 'memory_store':
            return self._handle_memory_storage(user_input, memory_manager, user_profile)
        
        elif intent == 'memory_recall':
            return self._handle_memory_recall(user_input, memory_manager, user_profile)
        
        elif intent == 'summarize':
            return self._handle_summarization(conversation_history, memory_manager)
        
        elif intent == 'help':
            return self._handle_help_request()
        
        elif intent == 'profile_query':
            return self._handle_profile_query(user_profile, memory_manager)
        
        else:
            return self._handle_general_query(user_input, conversation_history, memory_manager)
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        input_lower = user_input.lower()
        
        # Greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(pattern in input_lower for pattern in greeting_patterns):
            return 'greeting'
        
        # Memory storage patterns
        memory_store_patterns = ['remember', 'my name is', 'i prefer', 'i like', 'i am', 'i work']
        if any(pattern in input_lower for pattern in memory_store_patterns):
            return 'memory_store'
        
        # Memory recall patterns
        memory_recall_patterns = ['what do you know about me', 'what do you remember', 'do you know my', 'tell me about myself']
        if any(pattern in input_lower for pattern in memory_recall_patterns):
            return 'memory_recall'
        
        # Summarization patterns
        summarize_patterns = ['summarize', 'summary', 'recap', 'what did we discuss']
        if any(pattern in input_lower for pattern in summarize_patterns):
            return 'summarize'
        
        # Help patterns
        help_patterns = ['help', 'what can you do', 'your capabilities', 'how do you work']
        if any(pattern in input_lower for pattern in help_patterns):
            return 'help'
        
        # Profile query patterns
        profile_patterns = ['who am i', 'what are my', 'my profile', 'my preferences']
        if any(pattern in input_lower for pattern in profile_patterns):
            return 'profile_query'
        
        return 'general'
    
    def _handle_greeting(self, user_profile: Dict) -> str:
        """Handle greeting messages"""
        name = user_profile.get('name', '')
        
        if name:
            return f"Hello {name}! How can I assist you today?"
        else:
            return "Hello! How can I assist you today? Feel free to tell me your name so I can personalize our conversation."
    
    def _handle_memory_storage(self, user_input: str, memory_manager, user_profile: Dict) -> str:
        """Handle requests to remember information"""
        input_lower = user_input.lower()
        
        # Extract name if provided
        if 'my name is' in input_lower:
            name_match = re.search(r'my name is (\w+)', input_lower, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).capitalize()
                user_profile['name'] = name
                memory_manager.add_to_memory(
                    f"User's name is {name}",
                    'user_info',
                    {'preference_type': 'name'}
                )
                return f"Nice to meet you, {name}! I'll remember your name for our future conversations."
        
        # Extract preferences
        if 'prefer' in input_lower or 'like' in input_lower:
            memory_manager.add_to_memory(
                user_input,
                'preference',
                {'preference_type': 'general'}
            )
            return f"Got it! I've noted your preference: '{user_input}'. I'll keep this in mind for our future conversations."
        
        # General memory storage
        memory_manager.add_to_memory(
            user_input,
            'user_info',
            {'type': 'general_info'}
        )
        return f"I've stored this information: '{user_input}'. I'll remember it for our future interactions."
    
    def _handle_memory_recall(self, user_input: str, memory_manager, user_profile: Dict) -> str:
        """Handle requests to recall stored information"""
        relevant_memories = memory_manager.get_relevant_memories(user_input, top_k=5)
        
        if not relevant_memories:
            return "I don't have any specific information stored about that yet. As we continue our conversation, I'll learn and remember more about you!"
        
        response = "Here's what I remember:\n\n"
        for i, memory in enumerate(relevant_memories, 1):
            response += f"{i}. {memory['content']}\n"
            response += f"   (Stored on: {memory['timestamp'][:10]})\n\n"
        
        return response.strip()
    
    def _handle_summarization(self, conversation_history: List[Dict], memory_manager) -> str:
        """Handle conversation summarization requests"""
        if not conversation_history:
            return "We haven't had any conversation to summarize yet!"
        
        summary = memory_manager.summarize_session(conversation_history)
        return f"Here's a summary of our conversation:\n\n{summary}"
    
    def _handle_help_request(self) -> str:
        """Handle help and capability queries"""
        return """I'm an AI Assistant with Memory! Here's what I can do:

🧠 **Memory Capabilities:**
- Remember information you share with me
- Recall past conversations
- Learn your preferences over time

💬 **Conversation Features:**
- Answer your questions
- Provide information and assistance
- Summarize our conversations

📊 **Commands you can try:**
- "Remember that I prefer Python"
- "What do you know about me?"
- "Summarize our conversation"
- "My name is [your name]"

🎯 **Special Features:**
- Persistent memory across sessions
- Context-aware responses
- Export conversation history

Just ask me anything, and I'll do my best to help!"""
    
    def _handle_profile_query(self, user_profile: Dict, memory_manager) -> str:
        """Handle queries about user profile"""
        name = user_profile.get('name', 'Not set')
        preferences = memory_manager.get_user_preferences()
        
        response = f"""**Your Profile:**

👤 **Name:** {name}

📋 **Preferences:**
"""
        if preferences:
            for key, value in preferences.items():
                response += f"- {key.capitalize()}: {value}\n"
        else:
            response += "- No preferences stored yet\n"
        
        response += f"\n🧠 **Total Memories Stored:** {memory_manager.get_memory_count()}"
        
        return response
    
    def _handle_general_query(self, user_input: str, conversation_history: List[Dict], memory_manager) -> str:
        """Handle general queries with context"""
        input_lower = user_input.lower()
        
        # Check for context in recent conversation
        recent_context = memory_manager.get_recent_context(n=3)
        context_info = ""
        
        if recent_context:
            context_info = "Based on our recent conversation, "
        
        # Provide contextual responses for common queries
        
        # Data analysis queries
        if any(keyword in input_lower for keyword in ['data', 'analysis', 'dataset', 'statistics']):
            return f"""{context_info}I can help you with data analysis! Here are some things I can assist with:

📊 **Data Analysis Help:**
- Exploratory Data Analysis (EDA)
- Statistical analysis techniques
- Data visualization strategies
- Feature engineering approaches
- Model selection guidance

**Common Steps:**
1. Data loading and inspection
2. Data cleaning and preprocessing
3. Statistical analysis
4. Visualization
5. Insights and conclusions

What specific aspect of data analysis would you like help with?"""
        
        # Machine Learning queries
        elif any(keyword in input_lower for keyword in ['machine learning', 'ml', 'model', 'prediction']):
            return f"""{context_info}I can help with Machine Learning! Here's what I can guide you on:

🤖 **ML Topics:**
- Model selection (Classification/Regression)
- Feature engineering and selection
- Model training and evaluation
- Hyperparameter tuning
- Cross-validation strategies

**Popular ML Algorithms:**
- Linear/Logistic Regression
- Decision Trees/Random Forest
- SVM, KNN
- Neural Networks
- Ensemble methods

What ML topic would you like to explore?"""
        
        # Python/Programming queries
        elif any(keyword in input_lower for keyword in ['python', 'code', 'programming', 'function']):
            return f"""{context_info}I can help with Python programming! 

🐍 **Python Topics:**
- Syntax and best practices
- Data structures and algorithms
- Libraries (NumPy, Pandas, Scikit-learn)
- Debugging and optimization
- Code examples and explanations

What programming topic do you need help with?"""
        
        # Career/Interview queries
        elif any(keyword in input_lower for keyword in ['job', 'interview', 'career', 'resume']):
            return f"""{context_info}I can help with career-related questions!

💼 **Career Assistance:**
- Interview preparation tips
- Technical interview questions
- Resume and project guidance
- Industry insights
- Skill development paths

What aspect of your career would you like to discuss?"""
        
        # Default response for unrecognized queries
        else:
            return f"""I understand you're asking about: "{user_input}"

I'm here to help! I specialize in:
- AI and Machine Learning concepts
- Data Science and Analysis
- Python programming
- Career guidance for tech roles

Could you provide more specific details about what you'd like to know? Or try asking:
- "Help me with data analysis"
- "Explain machine learning models"
- "What are your capabilities?"
- "Remember that I prefer Python for projects"
"""

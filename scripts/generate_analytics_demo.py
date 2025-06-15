#!/usr/bin/env python3
"""
Analytics Demo Data Generator
Creates sample conversation data to demonstrate the Analytics Dashboard
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class AnalyticsDemoGenerator:
    """Generate sample analytics data for demonstration"""
    
    def __init__(self):
        self.data_dir = "data/conversations"
        self.models = [
            "Llama-3.3-70B-Instruct",
            "Llama-3.3-8B-Instruct", 
            "Llama-4-Scout-17B-16E-Instruct-FP8",
            "Llama-4-Maverick-17B-128E-Instruct-FP8",
            "Cerebras-Llama-4-Scout-17B-16E-Instruct"
        ]
        
        self.reasoning_types = [
            "chain_of_thought",
            "react", 
            "step_by_step",
            "problem_decomposition",
            "reflection"
        ]
        
        self.sample_questions = [
            "How do I optimize database performance for a web application?",
            "Debug this Python error in my Django project",
            "Design a REST API architecture for microservices",
            "Explain machine learning algorithms for beginners",
            "What's the best way to implement authentication?",
            "How to set up CI/CD pipeline with Docker?",
            "Optimize my React application for better performance",
            "Build a real-time chat application with WebSockets",
            "Implement data visualization with Python",
            "Create a scalable cloud infrastructure on AWS"
        ]
        
        self.sample_responses = [
            "Here's a comprehensive approach to optimizing database performance...",
            "I can help you debug that Python error. Let's start by analyzing...",
            "For a scalable REST API architecture, consider these patterns...",
            "Machine learning can be broken down into several key concepts...",
            "Authentication implementation depends on your specific requirements...",
            "Setting up CI/CD with Docker involves several key steps...",
            "React performance optimization can be achieved through...",
            "Building a real-time chat application requires...",
            "Data visualization in Python can be accomplished using...",
            "Creating scalable cloud infrastructure involves..."
        ]
    
    def generate_sample_conversations(self, num_conversations: int = 50) -> None:
        """Generate sample conversation data"""
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        print(f"🎯 Generating {num_conversations} sample conversations...")
        
        for i in range(num_conversations):
            conversation = self._generate_conversation(i)
            
            # Save conversation to file
            filename = f"demo_conversation_{i+1:03d}_{uuid.uuid4().hex[:8]}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated {num_conversations} conversations in {self.data_dir}")
        print("📊 You can now view the analytics dashboard!")
    
    def _generate_conversation(self, index: int) -> Dict:
        """Generate a single conversation"""
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        conversation_date = datetime.now() - timedelta(days=days_ago)
        
        # Random conversation length (2-20 messages)
        num_messages = random.randint(1, 10) * 2  # Even number for user/assistant pairs
        
        messages = []
        
        for msg_idx in range(num_messages):
            if msg_idx % 2 == 0:  # User message
                content = random.choice(self.sample_questions)
                if random.random() < 0.3:  # 30% chance of follow-up question
                    content += " Can you provide more details?"
                
                messages.append({
                    "role": "user",
                    "content": content,
                    "timestamp": (conversation_date + timedelta(minutes=msg_idx)).isoformat()
                })
            else:  # Assistant message
                content = random.choice(self.sample_responses)
                
                # Add some variation in length
                if random.random() < 0.4:  # 40% chance of longer response
                    content += " Let me elaborate on this with additional details and examples..."
                
                messages.append({
                    "role": "assistant", 
                    "content": content,
                    "timestamp": (conversation_date + timedelta(minutes=msg_idx + 1)).isoformat()
                })
        
        # Create conversation object
        conversation = {
            "conversation_id": f"demo_{uuid.uuid4().hex}",
            "session_id": f"session_{uuid.uuid4().hex[:8]}",
            "created_at": conversation_date.isoformat(),
            "model": random.choice(self.models),
            "messages": messages,
            "total_messages": len(messages),
            "conversation_length": len(messages) // 2,  # Q&A pairs
        }
        
        # Add reasoning data to some conversations (60% chance)
        if random.random() < 0.6:
            reasoning_type = random.choice(self.reasoning_types)
            conversation.update({
                "reasoning_type": reasoning_type,
                "chain_of_thought": True,
                "confidence_score": random.uniform(0.6, 0.95),
            })
            
            # Add NLTK enhancement data (40% of reasoning conversations)
            if random.random() < 0.4:
                conversation.update({
                    "nltk_analysis": True,
                    "text_analysis": {
                        "complexity": random.choice(["simple", "moderate", "complex", "very_complex"]),
                        "sentiment_score": random.uniform(-0.5, 0.8),
                        "readability_score": random.uniform(0.3, 0.9),
                        "technical_terms": random.randint(0, 8),
                        "key_concepts": random.sample([
                            "api", "database", "optimization", "authentication", "deployment",
                            "testing", "security", "performance", "scalability", "architecture"
                        ], random.randint(2, 6))
                    },
                    "enhanced_confidence": conversation["confidence_score"] + random.uniform(0.05, 0.15),
                    "question_type": random.choice([
                        "procedural", "explanatory", "troubleshooting", 
                        "design", "comparative", "definitional"
                    ])
                })
        
        return conversation
    
    def generate_token_usage_data(self) -> None:
        """Generate token usage statistics in existing conversations"""
        
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        
        for filename in json_files:
            filepath = os.path.join(self.data_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                
                # Add token usage data
                total_tokens = 0
                user_tokens = 0
                assistant_tokens = 0
                
                for message in conversation.get('messages', []):
                    content = message.get('content', '')
                    # Rough token estimation: 1 token ≈ 4 characters
                    tokens = max(1, len(content) // 4)
                    total_tokens += tokens
                    
                    if message.get('role') == 'user':
                        user_tokens += tokens
                    elif message.get('role') == 'assistant':
                        assistant_tokens += tokens
                
                conversation.update({
                    'token_usage': {
                        'total_tokens': total_tokens,
                        'user_tokens': user_tokens,
                        'assistant_tokens': assistant_tokens,
                        'estimated': True
                    }
                })
                
                # Write back to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(conversation, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                print(f"⚠️ Could not process {filename}: {e}")
                continue
        
        print("✅ Added token usage data to existing conversations")
    
    def cleanup_demo_data(self) -> None:
        """Remove demo conversation files"""
        
        if not os.path.exists(self.data_dir):
            print("ℹ️ No data directory found")
            return
            
        demo_files = [f for f in os.listdir(self.data_dir) if f.startswith('demo_conversation_')]
        
        for filename in demo_files:
            filepath = os.path.join(self.data_dir, filename)
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"⚠️ Could not remove {filename}: {e}")
        
        print(f"🗑️ Cleaned up {len(demo_files)} demo conversation files")

def main():
    """Main demo data generation"""
    
    generator = AnalyticsDemoGenerator()
    
    print("🎲 Analytics Demo Data Generator")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Generate sample conversations (50)
2. Generate sample conversations (custom amount)
3. Add token usage data to existing conversations
4. Clean up demo data
5. Generate everything

Enter choice (1-5): """).strip()
    
    if choice == "1":
        generator.generate_sample_conversations(50)
        generator.generate_token_usage_data()
        
    elif choice == "2":
        try:
            num_conv = int(input("Enter number of conversations to generate: "))
            generator.generate_sample_conversations(num_conv)
            generator.generate_token_usage_data()
        except ValueError:
            print("❌ Invalid number")
            return
            
    elif choice == "3":
        generator.generate_token_usage_data()
        
    elif choice == "4":
        generator.cleanup_demo_data()
        
    elif choice == "5":
        generator.generate_sample_conversations(75)
        generator.generate_token_usage_data()
        print("\n🎉 Demo data generation complete!")
        print("🚀 Run the Streamlit app and visit the Analytics View page to see the dashboard!")
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
NLTK Integration Demo Script
Demonstrates the enhanced NLTK capabilities in SilentCodingLegend AI Agent
"""

import asyncio
from src.core.nltk_processor import NLTKProcessor
from src.core.chain_of_thought import ChainOfThoughtReasoner
from src.utils.logging import get_logger

logger = get_logger(__name__)

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}\n")

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'🔹'} {title}")
    print("-" * 40)

async def demo_nltk_processor():
    """Demonstrate NLTK processor capabilities"""
    print_header("NLTK Processor Demo")
    
    # Initialize NLTK processor
    processor = NLTKProcessor()
    
    # Test texts with different complexities
    test_texts = [
        "How do I build a machine learning model for image classification?",
        "Why is my REST API returning 500 errors when handling large JSON payloads?",
        "Design a scalable microservices architecture for an e-commerce platform with high availability requirements.",
        "What's the weather like today?",
        "Debug this complex algorithm that processes real-time streaming data using advanced statistical methods and machine learning techniques."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print_section(f"Test {i}: {text[:50]}...")
        
        # Analyze text
        analysis = await processor.analyze_text(text)
        
        print(f"📊 Complexity: {analysis.complexity.value}")
        print(f"💭 Sentiment: {analysis.sentiment_score:.3f}")
        print(f"📚 Readability: {analysis.readability_score:.3f}")
        print(f"🎯 Question Type: {processor.detect_question_type(text)}")
        print(f"🔑 Key Concepts: {', '.join(analysis.key_terms[:5])}")
        print(f"🏷️ Technical Terms: {len(analysis.technical_terms)}")
        print(f"🧠 Reasoning Indicators: {len(analysis.reasoning_indicators)}")
        
        if analysis.named_entities:
            entities = [f"{entity[0]}({entity[1]})" for entity in analysis.named_entities[:3]]
            print(f"🏪 Named Entities: {', '.join(entities)}")

def demo_cot_integration():
    """Demonstrate Chain-of-Thought integration with NLTK"""
    print_header("Chain-of-Thought + NLTK Integration Demo")
    
    # Initialize reasoner
    reasoner = ChainOfThoughtReasoner()
    
    # Test questions
    test_questions = [
        "How do I optimize database performance for a high-traffic web application?",
        "Debug this Python error in my Django application that's causing memory leaks.",
        "Design a REST API architecture for a real-time chat application.",
        "Explain the difference between supervised and unsupervised learning algorithms."
    ]
    
    for i, question in enumerate(test_questions, 1):
        print_section(f"Question {i}: {question[:50]}...")
        
        # Test CoT decision
        should_use_cot = reasoner.should_use_cot_reasoning(question)
        reasoning_type = reasoner.select_reasoning_type(question)
        
        print(f"🤔 Should use CoT: {should_use_cot}")
        print(f"🧠 Reasoning Type: {reasoning_type.value}")
        
        # Show NLTK analysis influence
        if reasoner.nltk_processor:
            question_type = reasoner.nltk_processor.detect_question_type(question)
            key_concepts = reasoner.nltk_processor.extract_key_concepts(question, top_n=5)
            confidence = reasoner.nltk_processor.enhance_reasoning_confidence(question, 0.7)
            
            print(f"🎯 NLTK Question Type: {question_type}")
            print(f"🔑 NLTK Key Concepts: {', '.join(key_concepts)}")
            print(f"📈 Enhanced Confidence: {confidence:.3f}")

async def demo_technical_analysis():
    """Demonstrate technical term detection and analysis"""
    print_header("Technical Analysis Demo")
    
    processor = NLTKProcessor()
    
    # Technical text examples
    technical_texts = [
        "Implement a RESTful API using Flask with SQLAlchemy ORM and Redis caching for scalable microservices architecture.",
        "Configure Kubernetes deployment with Docker containers, load balancers, and auto-scaling policies for production environment.",
        "Optimize PostgreSQL queries using indexing, query planning, and connection pooling for better database performance.",
        "Set up CI/CD pipeline with Jenkins, automated testing, and deployment to AWS EC2 instances using Terraform."
    ]
    
    for i, text in enumerate(technical_texts, 1):
        print_section(f"Technical Text {i}")
        print(f"📝 Text: {text}")
        
        # Get full analysis
        analysis = await processor.analyze_text(text)
        
        # Extract technical information
        key_concepts = processor.extract_key_concepts(text, top_n=10)
        technical_terms = [term for term in key_concepts if term in processor.technical_terms]
        
        print(f"🔧 Technical Terms Found: {len(technical_terms)}")
        if technical_terms:
            print(f"🏷️ Terms: {', '.join(technical_terms[:8])}")
        
        # Complexity assessment from full analysis
        print(f"📊 Complexity Level: {analysis.complexity.value}")
        print(f"� Sentiment: {analysis.sentiment_score:.3f}")
        print(f"📚 Readability: {analysis.readability_score:.3f}")

async def main():
    """Main demo function"""
    print_header("SilentCodingLegend NLTK Integration Demonstration")
    print("This demo showcases the enhanced natural language processing capabilities")
    print("integrated into the SilentCodingLegend AI Agent using NLTK.")
    
    try:
        # Run NLTK processor demo
        await demo_nltk_processor()
        
        # Run CoT integration demo
        demo_cot_integration()
        
        # Run technical analysis demo
        await demo_technical_analysis()
        
        print_header("Demo Complete!")
        print("✅ NLTK integration is fully functional and ready for production use.")
        print("🚀 The enhanced AI agent now provides:")
        print("   - Intelligent question type detection")
        print("   - Advanced text complexity analysis")
        print("   - Enhanced confidence scoring")
        print("   - Technical term recognition")
        print("   - Improved reasoning type selection")
        print("\n🌟 Try the enhanced features in the Streamlit app!")
        print("   Run: streamlit run streamlit_app.py")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

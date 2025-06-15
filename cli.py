#!/usr/bin/env python3
"""
SilentCodingLegend AI Agent - Command Line Interface
"""
import asyncio
import argparse
import sys
import os
from typing import Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agent import SilentCodingLegendAgent
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def interactive_chat(agent: SilentCodingLegendAgent, session_id: Optional[str] = None):
    """Interactive chat mode with Chain-of-Thought reasoning support"""
    print("🤖 SilentCodingLegend AI Agent - Interactive Mode")
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Use '***COT***' to trigger Chain-of-Thought reasoning")
    print("Press Ctrl+C to exit at any time")
    print("-" * 60)
    
    # Initialize conversation history
    conversation_history = []
    
    try:
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n🤖 SilentCodingLegend: Goodbye! Happy coding!")
                    break
                
                if not user_input:
                    continue
                
                # Add user message to history
                conversation_history.append({"role": "user", "content": user_input})
                
                # Check for CoT trigger
                use_cot = "***COT***" in user_input
                if use_cot:
                    # Remove the trigger from the actual message
                    user_input = user_input.replace("***COT***", "").strip()
                
                print(f"\n🤖 SilentCodingLegend{'🧠 (Chain-of-Thought)' if use_cot else ''}: ", end="", flush=True)
                
                if use_cot:
                    # Use Chain-of-Thought reasoning
                    from src.core.chain_of_thought import ReasoningType
                    result = agent.chat_sync_with_reasoning(
                        user_input, 
                        session_id=session_id,
                        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
                    )
                    
                    if isinstance(result, tuple) and len(result) == 2:
                        final_response, reasoning_chain = result
                        
                        # Clean up response if it contains reasoning object string
                        if isinstance(final_response, str) and "ReasoningChain(" in final_response:
                            final_response = final_response.split("ReasoningChain(")[0].strip().rstrip(", ")
                        
                        print(final_response)
                        
                        # Display reasoning process
                        if reasoning_chain:
                            print("\n" + "="*60)
                            print("🔍 REASONING PROCESS:")
                            print("="*60)
                            print(f"Problem: {reasoning_chain.problem}")
                            print(f"Reasoning Type: {reasoning_chain.reasoning_type.value.replace('_', ' ').title()}")
                            print("\nReasoning Steps:")
                            
                            for i, step in enumerate(reasoning_chain.steps):
                                step_text = step.thought.strip()
                                if step_text:
                                    if any(header in step_text for header in ["Understanding:", "Analysis:", "Reasoning:", "Solution:"]):
                                        print(f"\n📋 {step_text}")
                                    else:
                                        print(f"   {step_text}")
                            print("="*60)
                    else:
                        print(result)
                    
                    # Add assistant response to history
                    conversation_history.append({"role": "assistant", "content": final_response if 'final_response' in locals() else str(result)})
                else:
                    # Regular chat without CoT
                    response = await agent.chat(user_input, session_id=session_id)
                    print(response)
                    
                    # Add assistant response to history
                    conversation_history.append({"role": "assistant", "content": response})
                
            except EOFError:
                # Handle Ctrl+D
                print("\n\n🤖 SilentCodingLegend: Goodbye! Happy coding!")
                break
            except Exception as e:
                error_msg = f"❌ Error: {e}"
                print(f"\n{error_msg}")
                logger.error(f"Chat error: {e}")
                
                # Add error to history
                conversation_history.append({"role": "assistant", "content": error_msg})
                
    except KeyboardInterrupt:
        # This will be caught by the outer try-catch in main()
        raise

async def single_query(agent: SilentCodingLegendAgent, query: str):
    """Handle a single query with CoT support"""
    try:
        # Check for CoT trigger
        use_cot = "***COT***" in query
        if use_cot:
            # Remove the trigger from the actual message
            query = query.replace("***COT***", "").strip()
            
            print(f"\n🤖 SilentCodingLegend 🧠 (Chain-of-Thought): ", end="", flush=True)
            
            # Use Chain-of-Thought reasoning
            from src.core.chain_of_thought import ReasoningType
            result = agent.chat_sync_with_reasoning(
                query,
                reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
            )
            
            if isinstance(result, tuple) and len(result) == 2:
                final_response, reasoning_chain = result
                
                # Clean up response if it contains reasoning object string
                if isinstance(final_response, str) and "ReasoningChain(" in final_response:
                    final_response = final_response.split("ReasoningChain(")[0].strip().rstrip(", ")
                
                print(final_response)
                
                # Display reasoning process
                if reasoning_chain:
                    print("\n" + "="*60)
                    print("🔍 REASONING PROCESS:")
                    print("="*60)
                    print(f"Problem: {reasoning_chain.problem}")
                    print(f"Reasoning Type: {reasoning_chain.reasoning_type.value.replace('_', ' ').title()}")
                    print("\nReasoning Steps:")
                    
                    for i, step in enumerate(reasoning_chain.steps):
                        step_text = step.thought.strip()
                        if step_text:
                            if any(header in step_text for header in ["Understanding:", "Analysis:", "Reasoning:", "Solution:"]):
                                print(f"\n📋 {step_text}")
                            else:
                                print(f"   {step_text}")
                    print("="*60)
            else:
                print(result)
        else:
            # Regular query without CoT
            response = await agent.chat(query)
            print(f"\n🤖 SilentCodingLegend: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Query error: {e}")

async def cot_query(agent: SilentCodingLegendAgent, query: str, reasoning_type: str = "chain_of_thought"):
    """Handle a single query with explicit Chain-of-Thought reasoning"""
    try:
        print(f"\n🤖 SilentCodingLegend 🧠 (Chain-of-Thought - {reasoning_type.replace('_', ' ').title()}): ")
        
        # Use Chain-of-Thought reasoning
        from src.core.chain_of_thought import ReasoningType
        reasoning_enum = ReasoningType(reasoning_type)
        result = agent.chat_sync_with_reasoning(
            query,
            reasoning_type=reasoning_enum
        )
        
        if isinstance(result, tuple) and len(result) == 2:
            final_response, reasoning_chain = result
            
            # Clean up response if it contains reasoning object string
            if isinstance(final_response, str) and "ReasoningChain(" in final_response:
                final_response = final_response.split("ReasoningChain(")[0].strip().rstrip(", ")
            
            print(f"\n📝 Final Answer: {final_response}")
            
            # Display reasoning process
            if reasoning_chain:
                print("\n" + "="*60)
                print("🔍 REASONING PROCESS:")
                print("="*60)
                print(f"Problem: {reasoning_chain.problem}")
                print(f"Reasoning Type: {reasoning_chain.reasoning_type.value.replace('_', ' ').title()}")
                print("\nReasoning Steps:")
                
                for i, step in enumerate(reasoning_chain.steps):
                    step_text = step.thought.strip()
                    if step_text:
                        if any(header in step_text for header in ["Understanding:", "Analysis:", "Reasoning:", "Solution:"]):
                            print(f"\n📋 {step_text}")
                        else:
                            print(f"   {step_text}")
                print("="*60)
        else:
            print(f"\n📝 Response: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CoT query error: {e}")

async def generate_code_cli(agent: SilentCodingLegendAgent, description: str, language: str, include_tests: bool):
    """Generate code via CLI"""
    try:
        response = await agent.generate_code(
            description, 
            language=language, 
            include_tests=include_tests
        )
        print(f"\n🤖 Generated {language} code:\n")
        print(response)
    except Exception as e:
        print(f"❌ Error generating code: {e}")
        logger.error(f"Code generation error: {e}")

async def review_code_cli(agent: SilentCodingLegendAgent, code_file: str, language: str):
    """Review code from file via CLI"""
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        response = await agent.review_code(code, language=language)
        print(f"\n🤖 Code review for {code_file}:\n")
        print(response)
    except FileNotFoundError:
        print(f"❌ File not found: {code_file}")
    except Exception as e:
        print(f"❌ Error reviewing code: {e}")
        logger.error(f"Code review error: {e}")

def show_cot_help():
    """Show Chain-of-Thought usage examples"""
    print("\n🧠 Chain-of-Thought (CoT) Reasoning Help")
    print("="*50)
    print("\n📋 Usage Options:")
    print("1. Interactive Chat with CoT trigger:")
    print("   ./cli.py chat")
    print("   👤 You: ***COT*** How do I optimize a Python function for performance?")
    print("\n2. Single query with CoT:")
    print("   ./cli.py cot 'Explain the time complexity of bubble sort'")
    print("\n3. CoT with specific reasoning type:")
    print("   ./cli.py cot 'Design a REST API' --reasoning-type step_by_step")
    print("\n🔧 Available Reasoning Types:")
    print("   • chain_of_thought   - Standard step-by-step reasoning")
    print("   • react             - Reasoning and Acting interleaved")
    print("   • step_by_step      - Explicit step breakdown")
    print("   • problem_decomposition - Break complex problems into parts")
    print("   • reflection        - Self-reflective reasoning")
    print("\n💡 CoT Trigger: Use '***COT***' in interactive chat to enable reasoning")
    print("   Example: '***COT*** Help me debug this algorithm'")
    print("\n" + "="*50)

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="SilentCodingLegend AI Agent CLI - Now with Chain-of-Thought reasoning!",
        epilog="💡 Pro tip: Use '***COT***' in chat mode to trigger Chain-of-Thought reasoning, or use 'help-cot' for examples"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Start interactive chat')
    chat_parser.add_argument('--session-id', help='Session ID for conversation continuity')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Send a single query')
    query_parser.add_argument('message', help='The message to send')
    
    # CoT Query command
    cot_parser = subparsers.add_parser('cot', help='Send a query with Chain-of-Thought reasoning')
    cot_parser.add_argument('message', help='The message to send with CoT reasoning')
    cot_parser.add_argument('--reasoning-type', '-r', 
                           choices=['chain_of_thought', 'react', 'step_by_step', 'problem_decomposition', 'reflection'],
                           default='chain_of_thought',
                           help='Type of reasoning to use')
    
    # Generate code command
    gen_parser = subparsers.add_parser('generate', help='Generate code')
    gen_parser.add_argument('description', help='Description of the code to generate')
    gen_parser.add_argument('--language', '-l', default='python', help='Programming language')
    gen_parser.add_argument('--tests', '-t', action='store_true', help='Include unit tests')
    
    # Review code command
    review_parser = subparsers.add_parser('review', help='Review code from file')
    review_parser.add_argument('file', help='Path to the code file')
    review_parser.add_argument('--language', '-l', default='python', help='Programming language')
    
    # Agent info command
    info_parser = subparsers.add_parser('info', help='Show agent information')
    
    # Help command for CoT usage
    help_parser = subparsers.add_parser('help-cot', help='Show Chain-of-Thought usage examples')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize agent
    agent = SilentCodingLegendAgent()
    
    try:
        if args.command == 'chat':
            asyncio.run(interactive_chat(agent, args.session_id))
        
        elif args.command == 'query':
            asyncio.run(single_query(agent, args.message))
        
        elif args.command == 'cot':
            asyncio.run(cot_query(agent, args.message, args.reasoning_type))
        
        elif args.command == 'generate':
            asyncio.run(generate_code_cli(agent, args.description, args.language, args.tests))
        
        elif args.command == 'review':
            asyncio.run(review_code_cli(agent, args.file, args.language))
        
        elif args.command == 'info':
            info = agent.get_agent_info()
            print("\n🤖 SilentCodingLegend AI Agent Information:")
            print(f"Name: {info['name']}")
            print(f"Description: {info['description']}")
            print(f"Version: {info['version']}")
            print(f"Status: {info['status']}")
            print("\nCapabilities:")
            for capability in info['capabilities']:
                print(f"  • {capability}")
        
        elif args.command == 'help-cot':
            show_cot_help()
        
        elif args.command == 'help-cot':
            show_cot_help()
                
    except KeyboardInterrupt:
        print("\n\n🤖 SilentCodingLegend: Goodbye! Happy coding!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"CLI error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

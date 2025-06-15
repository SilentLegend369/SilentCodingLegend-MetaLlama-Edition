"""
Agent Interaction Handler
Centralized handling of agent interactions with consistent error handling and session management
"""
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json

from src.config.coding_config import SessionData, save_coding_session
from src.utils.logging import get_logger

logger = get_logger(__name__)


class AgentInteractionHandler:
    """Handles all agent interactions with consistent patterns"""
    
    def __init__(self, agent, session_id: str):
        self.agent = agent
        self.session_id = session_id
    
    def execute_request(self, 
                       prompt: str,
                       session_data: SessionData,
                       display_format: str = "text",
                       language: Optional[str] = None,
                       use_reasoning: bool = False,
                       reasoning_type: Optional[Any] = None) -> Tuple[str, Optional[Any]]:
        """
        Execute an agent request with consistent error handling and session management
        
        Args:
            prompt: The prompt to send to the agent
            session_data: Session data to save
            display_format: How to display the result ("text", "code", "markdown")
            language: Programming language for code display
            use_reasoning: Whether to use chain-of-thought reasoning
            reasoning_type: Type of reasoning to use
            
        Returns:
            Tuple of (response, reasoning_chain)
        """
        try:
            if use_reasoning and hasattr(self.agent, 'chat_sync_with_reasoning'):
                response, reasoning_chain = self.agent.chat_sync_with_reasoning(
                    prompt,
                    self.session_id,
                    use_cot=True,
                    reasoning_type=reasoning_type
                )
            else:
                response = self.agent.chat_sync(prompt, self.session_id)
                reasoning_chain = None
            
            # Save session data
            self._save_session_data(session_data)
            
            return response, reasoning_chain
            
        except Exception as e:
            error_msg = f"Error executing agent request: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def build_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """
        Build a comprehensive prompt from base prompt and context
        
        Args:
            base_prompt: The base prompt template
            context: Context dictionary with additional information
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [base_prompt]
        
        # Add context-specific information
        if context.get('language'):
            prompt_parts.append(f"Programming language: {context['language']}")
        
        if context.get('requirements'):
            if isinstance(context['requirements'], list):
                prompt_parts.extend(context['requirements'])
            else:
                prompt_parts.append(str(context['requirements']))
        
        if context.get('constraints'):
            prompt_parts.append(f"Constraints: {context['constraints']}")
        
        if context.get('examples'):
            prompt_parts.append(f"Examples: {context['examples']}")
        
        return ". ".join(prompt_parts)
    
    def format_code_prompt(self, 
                          task_description: str,
                          language: str,
                          include_tests: bool = False,
                          include_docs: bool = False,
                          include_comments: bool = False,
                          follow_conventions: bool = False,
                          additional_requirements: Optional[List[str]] = None) -> str:
        """
        Format a standardized code generation prompt
        
        Args:
            task_description: What the code should do
            language: Programming language
            include_tests: Whether to include unit tests
            include_docs: Whether to include documentation
            include_comments: Whether to include inline comments
            follow_conventions: Whether to follow language conventions
            additional_requirements: Any additional requirements
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [f"Create {language} code: {task_description}"]
        
        if include_tests:
            prompt_parts.append("Include comprehensive unit tests")
        if include_docs:
            prompt_parts.append("Include detailed documentation")
        if include_comments:
            prompt_parts.append("Add inline comments explaining the code")
        if follow_conventions:
            prompt_parts.append(f"Follow {language} best practices and conventions")
        
        if additional_requirements:
            prompt_parts.extend(additional_requirements)
        
        return ". ".join(prompt_parts)
    
    def format_review_prompt(self,
                           code: str,
                           language: str,
                           review_aspects: List[str],
                           specific_concerns: Optional[str] = None) -> str:
        """
        Format a standardized code review prompt
        
        Args:
            code: Code to review
            language: Programming language
            review_aspects: Aspects to focus on during review
            specific_concerns: Any specific concerns to address
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Review this {language} code and provide detailed analysis focusing on: {', '.join(review_aspects)}.

Code:
```{language}
{code}
```

Please provide:
1. Overall assessment
2. Specific issues and improvements
3. Best practice recommendations
4. Refactored code suggestions if needed"""
        
        if specific_concerns:
            prompt += f"\n\nSpecific concerns to address: {specific_concerns}"
        
        return prompt
    
    def format_debug_prompt(self,
                          code: str,
                          language: str,
                          error_message: Optional[str] = None,
                          expected_behavior: Optional[str] = None,
                          context: Optional[str] = None) -> str:
        """
        Format a standardized debugging prompt
        
        Args:
            code: Problematic code
            language: Programming language
            error_message: Error message or description
            expected_behavior: What the code should do
            context: Additional context about the problem
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Debug this {language} code and provide a solution.

Problematic Code:
```{language}
{code}
```

Error Message: {error_message if error_message else 'No specific error message provided'}
Expected Behavior: {expected_behavior if expected_behavior else 'Not specified'}"""
        
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        prompt += """

Please provide:
1. Root cause analysis
2. Step-by-step explanation of the issue
3. Fixed code with corrections
4. Prevention tips for similar issues"""
        
        return prompt
    
    def format_data_science_prompt(self,
                                 task_type: str,
                                 description: str,
                                 data_format: str,
                                 data_size: str,
                                 include_plots: bool = False,
                                 include_stats: bool = False,
                                 include_ml_metrics: bool = False,
                                 optimize_code: bool = False,
                                 additional_libraries: Optional[List[str]] = None) -> str:
        """
        Format a standardized data science prompt
        
        Args:
            task_type: Type of data science task
            description: Task description
            data_format: Format of the data
            data_size: Size of the dataset
            include_plots: Whether to include visualizations
            include_stats: Whether to include statistics
            include_ml_metrics: Whether to include ML metrics
            optimize_code: Whether to optimize for performance
            additional_libraries: Any additional libraries to use
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            f"Create Python code for {task_type.lower()}: {description}",
            f"Data format: {data_format}",
            f"Dataset size: {data_size}",
            "Use appropriate libraries: numpy, pandas, scikit-learn, matplotlib"
        ]
        
        if additional_libraries:
            prompt_parts.append(f"Additional libraries: {', '.join(additional_libraries)}")
        
        if include_plots:
            prompt_parts.append("Include matplotlib visualizations with proper labels and styling")
        if include_stats:
            prompt_parts.append("Include statistical analysis and summary statistics")
        if include_ml_metrics and "Model" in task_type:
            prompt_parts.append("Include comprehensive model evaluation metrics")
        if optimize_code:
            prompt_parts.append("Optimize code for performance and memory efficiency")
        
        prompt_parts.extend([
            "Include error handling and data validation",
            "Add detailed comments explaining each step",
            "Follow data science best practices",
            "Make the code production-ready and well-structured"
        ])
        
        return ". ".join(prompt_parts)
    
    def _save_session_data(self, session_data: SessionData) -> None:
        """Save session data to file"""
        try:
            save_coding_session(session_data.__dict__, self.session_id)
        except Exception as e:
            logger.error(f"Failed to save session data: {str(e)}")


class PromptTemplates:
    """Collection of standardized prompt templates"""
    
    @staticmethod
    def explanation_prompt(content: str, language: str, explanation_type: str) -> str:
        """Generate explanation prompt based on type"""
        if explanation_type == "Explain Code":
            return f"Explain this {language} code in detail, including what it does, how it works, and any important concepts:\n\n```{language}\n{content}\n```"
        elif explanation_type == "Learn Concept":
            return f"Explain the programming concept '{content}' with examples in {language}. Include practical applications and best practices."
        elif explanation_type == "Compare Solutions":
            return f"Compare and contrast {content} in the context of {language} programming. Explain pros, cons, and when to use each."
        else:  # Best Practices
            return f"Explain best practices for {content} in {language} programming. Include examples and common pitfalls to avoid."
    
    @staticmethod
    def optimization_prompt(code: str, language: str, optimization_goals: List[str]) -> str:
        """Generate code optimization prompt"""
        goals_str = ", ".join(optimization_goals)
        return f"""Optimize this {language} code focusing on: {goals_str}

Original Code:
```{language}
{code}
```

Please provide:
1. Performance analysis of the original code
2. Optimized version with improvements
3. Explanation of optimizations made
4. Performance comparison and metrics
5. Alternative approaches if applicable"""
    
    @staticmethod
    def architecture_prompt(requirements: str, technology_stack: List[str], constraints: List[str]) -> str:
        """Generate system architecture design prompt"""
        stack_str = ", ".join(technology_stack)
        constraints_str = ", ".join(constraints)
        
        return f"""Design a system architecture for the following requirements:

Requirements: {requirements}

Technology Stack: {stack_str}
Constraints: {constraints_str}

Please provide:
1. High-level architecture diagram description
2. Component breakdown and responsibilities
3. Data flow and interaction patterns
4. Scalability considerations
5. Security considerations
6. Implementation guidelines
7. Potential challenges and solutions"""
    
    @staticmethod
    def refactoring_prompt(code: str, language: str, refactoring_goals: List[str]) -> str:
        """Generate code refactoring prompt"""
        goals_str = ", ".join(refactoring_goals)
        return f"""Refactor this {language} code to improve: {goals_str}

Original Code:
```{language}
{code}
```

Please provide:
1. Analysis of current code issues
2. Refactored code with improvements
3. Explanation of changes made
4. Design pattern recommendations
5. Testing strategy for the refactored code"""


# Convenience functions for common operations
def create_agent_handler(agent, session_id: str) -> AgentInteractionHandler:
    """Create a new agent interaction handler"""
    return AgentInteractionHandler(agent, session_id)


def execute_simple_request(agent, session_id: str, prompt: str, session_type: str, **kwargs) -> str:
    """Execute a simple agent request with minimal setup"""
    handler = AgentInteractionHandler(agent, session_id)
    
    session_data = SessionData(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        session_type=session_type,
        **kwargs
    )
    
    response, _ = handler.execute_request(prompt, session_data)
    return response

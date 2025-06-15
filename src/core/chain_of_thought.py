"""
Chain-of-Thought (CoT) Reasoning System
Advanced reasoning capabilities for the SilentCodingLegend AI Agent
Enhanced with NLTK natural language processing
"""
import re
import json
import asyncio
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from ..utils.logging import get_logger

# NLTK integration
try:
    from .nltk_processor import NLTKProcessor, TextAnalysis
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = get_logger(__name__)

class ReasoningType(Enum):
    """Types of reasoning approaches"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    REACT = "react"
    STEP_BY_STEP = "step_by_step" 
    PROBLEM_DECOMPOSITION = "problem_decomposition"
    REFLECTION = "reflection"

@dataclass
class ThoughtStep:
    """Individual step in the reasoning process"""
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    confidence: float = 0.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ReasoningChain:
    """Complete reasoning chain for a problem"""
    problem: str
    reasoning_type: ReasoningType
    steps: List[ThoughtStep]
    final_answer: str
    confidence_score: float
    created_at: str = None
    # NLTK enhancement fields
    text_analysis: Optional['TextAnalysis'] = None
    enhanced_confidence: Optional[float] = None
    key_concepts: Optional[List[str]] = None
    question_type: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class ChainOfThoughtReasoner:
    """
    Implements Chain-of-Thought reasoning for complex problem solving
    Enhanced with NLTK natural language processing
    """
    
    def __init__(self):
        self.reasoning_templates = {
            ReasoningType.CHAIN_OF_THOUGHT: self._cot_template,
            ReasoningType.REACT: self._react_template,
            ReasoningType.STEP_BY_STEP: self._step_by_step_template,
            ReasoningType.PROBLEM_DECOMPOSITION: self._decomposition_template,
            ReasoningType.REFLECTION: self._reflection_template
        }
        
        # Initialize NLTK processor if available
        self.nltk_processor = None
        if NLTK_AVAILABLE:
            try:
                self.nltk_processor = NLTKProcessor()
                logger.info("NLTK processor initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize NLTK processor: {e}")
                self.nltk_processor = None
        else:
            logger.info("NLTK not available, using basic text processing")
        
        logger.info("Initialized Chain-of-Thought Reasoner")
    
    def should_use_cot_reasoning(self, message: str) -> bool:
        """
        Determine if a message would benefit from Chain-of-Thought reasoning
        Enhanced with NLTK analysis
        
        Args:
            message (str): User input message
            
        Returns:
            bool: True if CoT reasoning should be used
        """
        # Use NLTK analysis if available
        if self.nltk_processor:
            try:
                # Get question type from NLTK
                question_type = self.nltk_processor.detect_question_type(message)
                
                # Complex question types benefit from CoT
                complex_types = {'procedural', 'explanatory', 'troubleshooting', 'design', 'comparative'}
                if question_type in complex_types:
                    return True
                
                # Extract key concepts for complexity assessment
                key_concepts = self.nltk_processor.extract_key_concepts(message, top_n=5)
                technical_concepts = [concept for concept in key_concepts 
                                    if concept in self.nltk_processor.technical_terms]
                
                # If message contains multiple technical concepts, use CoT
                if len(technical_concepts) >= 2:
                    return True
                    
            except Exception as e:
                logger.warning(f"NLTK analysis failed in CoT detection: {e}")
        
        # Fallback to original method
        cot_indicators = [
            # Problem-solving keywords
            "solve", "calculate", "analyze", "debug", "optimize", "design",
            "implement", "explain", "how to", "why", "what if", "compare",
            
            # Complexity indicators
            "algorithm", "architecture", "system", "database", "performance",
            "security", "scalability", "integration", "deployment",
            
            # Multi-step indicators
            "step by step", "process", "procedure", "workflow", "pipeline",
            "sequence", "stages", "phases", "approach", "methodology",
            
            # Code-related complexity
            "refactor", "review", "test", "document", "structure", "pattern",
            "best practice", "error handling", "validation", "optimization"
        ]
        
        message_lower = message.lower()
        
        # Check for complexity indicators
        complexity_score = sum(1 for indicator in cot_indicators if indicator in message_lower)
        
        # Check message length (longer messages often need structured reasoning)
        length_score = len(message.split()) > 20
        
        # Check for question words that indicate complex queries
        question_indicators = ["how", "why", "what", "when", "where", "which"]
        has_complex_question = any(q in message_lower for q in question_indicators)
        
        return complexity_score >= 2 or length_score or has_complex_question
    
    def select_reasoning_type(self, message: str) -> ReasoningType:
        """
        Select the most appropriate reasoning type based on the message
        Enhanced with NLTK question type detection
        
        Args:
            message (str): User input message
            
        Returns:
            ReasoningType: Best reasoning approach for this message
        """
        # Use NLTK question type detection if available
        if self.nltk_processor:
            try:
                question_type = self.nltk_processor.detect_question_type(message)
                
                # Map NLTK question types to reasoning types
                type_mapping = {
                    'procedural': ReasoningType.STEP_BY_STEP,
                    'explanatory': ReasoningType.CHAIN_OF_THOUGHT,
                    'troubleshooting': ReasoningType.REFLECTION,
                    'design': ReasoningType.PROBLEM_DECOMPOSITION,
                    'comparative': ReasoningType.CHAIN_OF_THOUGHT,
                    'definitional': ReasoningType.CHAIN_OF_THOUGHT,
                    'general': ReasoningType.CHAIN_OF_THOUGHT
                }
                
                if question_type in type_mapping:
                    logger.info(f"NLTK detected question type: {question_type} -> {type_mapping[question_type].value}")
                    return type_mapping[question_type]
                    
            except Exception as e:
                logger.warning(f"NLTK reasoning type selection failed: {e}")
        
        # Fallback to original keyword-based method
        message_lower = message.lower()
        
        # ReAct for tool-using or interactive tasks
        if any(word in message_lower for word in ["search", "look up", "find", "check", "verify", "test"]):
            return ReasoningType.REACT
        
        # Problem decomposition for complex system design
        if any(word in message_lower for word in ["design", "architecture", "system", "build", "create"]):
            return ReasoningType.PROBLEM_DECOMPOSITION
        
        # Step-by-step for procedures and tutorials
        if any(word in message_lower for word in ["how to", "tutorial", "guide", "steps", "process"]):
            return ReasoningType.STEP_BY_STEP
        
        # Reflection for debugging and analysis
        if any(word in message_lower for word in ["debug", "fix", "error", "problem", "issue", "analyze"]):
            return ReasoningType.REFLECTION
        
        # Default to chain-of-thought
        return ReasoningType.CHAIN_OF_THOUGHT
    
    def _cot_template(self, problem: str) -> str:
        """Chain-of-Thought reasoning template"""
        return f"""Think through this problem step by step using clear reasoning:

Problem: {problem}

Please follow this structure:
1. **Understanding**: What is the core problem or question?
2. **Analysis**: Break down the key components and requirements
3. **Reasoning**: Work through the logic step by step
4. **Solution**: Provide the final answer or recommendation

Let me think through this carefully:"""

    def _react_template(self, problem: str) -> str:
        """ReAct (Reason + Act) reasoning template"""
        return f"""Use the ReAct format to solve this problem systematically:

Problem: {problem}

Follow this format:
**Thought**: [Your reasoning about what to do next]
**Action**: [What action or step to take]
**Observation**: [What you learned or discovered]

Continue this cycle until you reach a solution.

Let me start:"""

    def _step_by_step_template(self, problem: str) -> str:
        """Step-by-step reasoning template"""
        return f"""Provide a detailed step-by-step solution:

Problem: {problem}

Break this down into clear, actionable steps:

**Step 1**: [First action/consideration]
**Step 2**: [Second action/consideration]
**Step 3**: [Third action/consideration]
[Continue as needed...]

**Summary**: [Final conclusion/result]

Let me work through this systematically:"""

    def _decomposition_template(self, problem: str) -> str:
        """Problem decomposition reasoning template"""
        return f"""Decompose this complex problem into manageable parts:

Problem: {problem}

**Problem Decomposition**:
1. **Core Components**: What are the main parts of this problem?
2. **Dependencies**: How do these parts relate to each other?
3. **Priorities**: What should be tackled first?
4. **Sub-problems**: Break each component into smaller tasks
5. **Integration**: How do we combine the solutions?

Let me analyze this systematically:"""

    def _reflection_template(self, problem: str) -> str:
        """Reflection-based reasoning template"""
        return f"""Use reflection to thoroughly analyze this problem:

Problem: {problem}

**Reflection Process**:
1. **Current Situation**: What is happening now?
2. **Root Cause Analysis**: Why is this happening?
3. **Alternative Perspectives**: What other ways can we view this?
4. **Potential Solutions**: What options do we have?
5. **Evaluation**: What are the pros and cons of each option?
6. **Decision**: What is the best approach and why?

Let me reflect on this carefully:"""

    def generate_reasoning_prompt(self, message: str, reasoning_type: Optional[ReasoningType] = None) -> str:
        """
        Generate a prompt that encourages Chain-of-Thought reasoning
        
        Args:
            message (str): Original user message
            reasoning_type (Optional[ReasoningType]): Specific reasoning type to use
            
        Returns:
            str: Enhanced prompt with CoT structure
        """
        if reasoning_type is None:
            reasoning_type = self.select_reasoning_type(message)
        
        template_func = self.reasoning_templates[reasoning_type]
        enhanced_prompt = template_func(message)
        
        logger.info(f"Generated {reasoning_type.value} reasoning prompt")
        return enhanced_prompt
    
    def parse_reasoning_response(self, response: str, original_problem: str = "") -> ReasoningChain:
        """
        Parse AI response to extract reasoning steps
        Enhanced with NLTK text analysis
        
        Args:
            response (str): AI response with reasoning
            original_problem (str): Original problem statement
            
        Returns:
            ReasoningChain: Structured reasoning chain with NLTK enhancements
        """
        steps = []
        final_answer = ""
        
        # Try to parse different reasoning formats
        if "**Thought**:" in response and "**Action**:" in response:
            # ReAct format
            steps = self._parse_react_format(response)
        elif "**Step" in response:
            # Step-by-step format
            steps = self._parse_step_format(response)
        else:
            # General CoT format
            steps = self._parse_general_cot(response)
        
        # Extract final answer (usually at the end)
        final_answer = self._extract_final_answer(response)
        
        # Calculate confidence based on reasoning quality
        confidence = self._calculate_confidence(steps, response)
        
        # NLTK enhancements
        text_analysis = None
        enhanced_confidence = confidence
        key_concepts = []
        question_type = None
        
        if self.nltk_processor:
            try:
                # Analyze the response text with safe async handling
                try:
                    # Try to get current event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task and run in thread if loop is already running
                        import threading
                        result = None
                        exception = None
                        
                        def run_analysis():
                            nonlocal result, exception
                            try:
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                try:
                                    result = new_loop.run_until_complete(self.nltk_processor.analyze_text(response))
                                finally:
                                    new_loop.close()
                            except Exception as e:
                                exception = e
                        
                        thread = threading.Thread(target=run_analysis)
                        thread.start()
                        thread.join()
                        
                        if exception:
                            raise exception
                        text_analysis = result
                    else:
                        # Can run directly
                        text_analysis = loop.run_until_complete(self.nltk_processor.analyze_text(response))
                except RuntimeError:
                    # No event loop, create one
                    text_analysis = asyncio.run(self.nltk_processor.analyze_text(response))
                
                # Enhance confidence using NLTK
                enhanced_confidence = self.nltk_processor.enhance_reasoning_confidence(response, confidence)
                
                # Extract key concepts from problem and response
                problem_concepts = self.nltk_processor.extract_key_concepts(original_problem)
                response_concepts = self.nltk_processor.extract_key_concepts(response)
                key_concepts = list(set(problem_concepts + response_concepts))
                
                # Detect question type
                if original_problem:
                    question_type = self.nltk_processor.detect_question_type(original_problem)
                    
                logger.info(f"NLTK analysis complete - Enhanced confidence: {enhanced_confidence:.3f}")
                
            except Exception as e:
                logger.warning(f"NLTK analysis failed during response parsing: {e}")
        
        return ReasoningChain(
            problem=original_problem or "Parsed from response",
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            steps=steps,
            final_answer=final_answer,
            confidence_score=confidence,
            text_analysis=text_analysis,
            enhanced_confidence=enhanced_confidence,
            key_concepts=key_concepts,
            question_type=question_type
        )
    
    def _parse_react_format(self, response: str) -> List[ThoughtStep]:
        """Parse ReAct format response"""
        steps = []
        
        # Find all Thought-Action-Observation triplets
        pattern = r'\*\*Thought\*\*:(.*?)(?=\*\*Action\*\*:|\*\*Thought\*\*:|$)(.*?)(?=\*\*Observation\*\*:|\*\*Thought\*\*:|$)(.*?)(?=\*\*Thought\*\*:|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for i, (thought, action, observation) in enumerate(matches):
            step = ThoughtStep(
                step_number=i + 1,
                thought=thought.strip(),
                action=action.replace("**Action**:", "").strip() if "**Action**:" in action else None,
                observation=observation.replace("**Observation**:", "").strip() if "**Observation**:" in observation else None,
                confidence=0.8
            )
            steps.append(step)
        
        return steps
    
    def _parse_step_format(self, response: str) -> List[ThoughtStep]:
        """Parse step-by-step format response"""
        steps = []
        
        # Find all numbered steps
        pattern = r'\*\*Step\s+(\d+)\*\*:(.*?)(?=\*\*Step\s+\d+\*\*:|\*\*Summary\*\*:|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for step_num, content in matches:
            step = ThoughtStep(
                step_number=int(step_num),
                thought=content.strip(),
                confidence=0.7
            )
            steps.append(step)
        
        return steps
    
    def _parse_general_cot(self, response: str) -> List[ThoughtStep]:
        """Parse general chain-of-thought response"""
        steps = []
        
        # Split by common reasoning markers
        sections = re.split(r'\d+\.|•|\*\*|\n\n', response)
        
        for i, section in enumerate(sections):
            section = section.strip()
            if len(section) > 20:  # Filter out very short sections
                step = ThoughtStep(
                    step_number=i + 1,
                    thought=section,
                    confidence=0.6
                )
                steps.append(step)
        
        return steps
    
    def _extract_final_answer(self, response: str) -> str:
        """Extract the final answer from the response"""
        # Look for common final answer patterns
        patterns = [
            r'\*\*Summary\*\*:(.*?)$',
            r'\*\*Conclusion\*\*:(.*?)$',
            r'\*\*Final Answer\*\*:(.*?)$',
            r'\*\*Result\*\*:(.*?)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If no specific pattern found, take the last significant paragraph
        paragraphs = [p.strip() for p in response.split('\n\n') if len(p.strip()) > 50]
        return paragraphs[-1] if paragraphs else response[-200:]
    
    def _calculate_confidence(self, steps: List[ThoughtStep], response: str) -> float:
        """Calculate confidence score based on reasoning quality"""
        if not steps:
            return 0.3
        
        # Base confidence on number of reasoning steps
        step_score = min(len(steps) / 5.0, 1.0) * 0.4
        
        # Check for reasoning quality indicators
        quality_indicators = [
            "because", "therefore", "thus", "consequently", "as a result",
            "this means", "we can conclude", "it follows that", "given that"
        ]
        
        quality_score = min(
            sum(1 for indicator in quality_indicators if indicator in response.lower()) / 3.0,
            1.0
        ) * 0.3
        
        # Check for structured thinking
        structure_indicators = ["first", "second", "third", "next", "then", "finally"]
        structure_score = min(
            sum(1 for indicator in structure_indicators if indicator in response.lower()) / 4.0,
            1.0
        ) * 0.3
        
        return step_score + quality_score + structure_score

class LoopOfThoughtAgent:
    """
    Enhanced agent that uses Loop of Thought reasoning
    """
    
    def __init__(self, base_agent):
        self.base_agent = base_agent
        self.reasoner = ChainOfThoughtReasoner()
        self.reasoning_history: List[ReasoningChain] = []
        logger.info("Initialized Loop of Thought Agent")
    
    async def enhanced_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        use_cot: bool = None,
        reasoning_type: Optional[ReasoningType] = None
    ) -> Tuple[str, Optional[ReasoningChain]]:
        """
        Enhanced chat with Chain-of-Thought reasoning
        
        Args:
            message (str): User input
            session_id (Optional[str]): Session identifier
            use_cot (bool): Force CoT usage (None for auto-detection)
            reasoning_type (Optional[ReasoningType]): Specific reasoning type
            
        Returns:
            Tuple[str, Optional[ReasoningChain]]: Response and reasoning chain
        """
        # Determine if we should use CoT reasoning
        if use_cot is None:
            use_cot = self.reasoner.should_use_cot_reasoning(message)
        
        if use_cot:
            # Generate CoT prompt
            enhanced_prompt = self.reasoner.generate_reasoning_prompt(message, reasoning_type)
            
            # Get AI response with reasoning
            response = await self.base_agent.chat(enhanced_prompt, session_id)
            
            # Parse the reasoning chain with NLTK enhancements
            reasoning_chain = self.reasoner.parse_reasoning_response(response, message)
            reasoning_chain.problem = message
            
            # Store in history
            self.reasoning_history.append(reasoning_chain)
            
            # Extract clean final answer from the reasoning chain
            final_answer = reasoning_chain.final_answer if reasoning_chain.final_answer else response
            
            logger.info(f"Generated CoT response with {len(reasoning_chain.steps)} reasoning steps")
            return final_answer, reasoning_chain
        else:
            # Use regular chat
            response = await self.base_agent.chat(message, session_id)
            return response, None
    
    def get_reasoning_history(self) -> List[ReasoningChain]:
        """Get the history of reasoning chains"""
        return self.reasoning_history
    
    def export_reasoning_analysis(self) -> Dict:
        """Export reasoning analysis for review with NLTK enhancements"""
        chains_data = []
        
        for chain in self.reasoning_history:
            chain_data = {
                "problem": chain.problem,
                "reasoning_type": chain.reasoning_type.value,
                "steps_count": len(chain.steps),
                "confidence": chain.confidence_score,
                "created_at": chain.created_at
            }
            
            # Add NLTK enhancements if available
            if chain.enhanced_confidence is not None:
                chain_data["enhanced_confidence"] = chain.enhanced_confidence
            if chain.key_concepts:
                chain_data["key_concepts"] = chain.key_concepts
            if chain.question_type:
                chain_data["question_type"] = chain.question_type
            if chain.text_analysis:
                chain_data["text_analysis"] = {
                    "complexity": chain.text_analysis.complexity.value,
                    "sentiment_score": chain.text_analysis.sentiment_score,
                    "word_count": chain.text_analysis.word_count,
                    "sentence_count": chain.text_analysis.sentence_count,
                    "readability_score": chain.text_analysis.readability_score,
                    "technical_terms": chain.text_analysis.technical_terms,
                    "reasoning_indicators": chain.text_analysis.reasoning_indicators
                }
            
            chains_data.append(chain_data)
        
        # Calculate averages
        total_chains = len(self.reasoning_history)
        avg_confidence = sum(chain.confidence_score for chain in self.reasoning_history) / total_chains if total_chains else 0
        avg_enhanced_confidence = sum(
            chain.enhanced_confidence for chain in self.reasoning_history 
            if chain.enhanced_confidence is not None
        ) / total_chains if total_chains else 0
        
        return {
            "total_chains": total_chains,
            "average_confidence": avg_confidence,
            "average_enhanced_confidence": avg_enhanced_confidence,
            "reasoning_types": {rt.value: sum(1 for chain in self.reasoning_history if chain.reasoning_type == rt) for rt in ReasoningType},
            "nltk_enabled": self.reasoner.nltk_processor is not None,
            "chains": chains_data
        }

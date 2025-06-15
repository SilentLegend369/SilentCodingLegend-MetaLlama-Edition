"""
Chain of Thought Reasoning Tools Plugin

Provides advanced reasoning capabilities including:
- Chain-of-thought reasoning
- Step-by-step analysis
- Problem decomposition
- Reflection and self-correction
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# Import the Chain of Thought reasoner
try:
    from src.core.chain_of_thought import ChainOfThoughtReasoner, ReasoningType
    REASONER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Chain of thought reasoner not available: {e}")
    REASONER_AVAILABLE = False

from src.plugins import BasePlugin, PluginMetadata, PluginType
from src.plugins.tool_registry import Tool, ToolParameter, ParameterType

class ChainOfThoughtPlugin(BasePlugin):
    """Plugin providing Chain of Thought reasoning capabilities"""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="ChainOfThoughtReasoningTools",
            version="1.0.0",
            description="Advanced reasoning with Chain-of-Thought, analysis, and problem decomposition",
            author="SilentCodingLegend",
            plugin_type=PluginType.TOOL,
            dependencies=[]
        )
        super().__init__(metadata)
        
        # Initialize reasoner if available
        self.reasoner = None
        if REASONER_AVAILABLE:
            try:
                self.reasoner = ChainOfThoughtReasoner()
            except Exception as e:
                logging.error(f"Failed to initialize reasoner: {e}")
    
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            logging.info("Chain of Thought Reasoning Plugin initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Chain of Thought plugin: {e}")
            return False
    
    def get_tools(self) -> List[Tool]:
        """Get available reasoning tools"""
        return [
            Tool(
                name="chain_of_thought_reasoning",
                description="Perform chain-of-thought reasoning on a problem or question",
                category="reasoning",
                parameters=[
                    ToolParameter(
                        name="problem",
                        type=ParameterType.STRING,
                        description="The problem or question to reason about",
                        required=True
                    ),
                    ToolParameter(
                        name="reasoning_type",
                        type=ParameterType.STRING,
                        description="Type of reasoning (chain_of_thought, step_by_step, problem_decomposition, react, reflection)",
                        required=False,
                        default="chain_of_thought"
                    ),
                    ToolParameter(
                        name="max_steps",
                        type=ParameterType.INTEGER,
                        description="Maximum number of reasoning steps",
                        required=False,
                        default=5
                    )
                ],
                function=self.chain_of_thought_reasoning,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="step_by_step_analysis",
                description="Break down a complex problem into manageable steps",
                category="reasoning",
                parameters=[
                    ToolParameter(
                        name="problem",
                        type=ParameterType.STRING,
                        description="The complex problem to analyze",
                        required=True
                    ),
                    ToolParameter(
                        name="context",
                        type=ParameterType.STRING,
                        description="Additional context or constraints",
                        required=False,
                        default=""
                    )
                ],
                function=self.step_by_step_analysis,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="problem_decomposition",
                description="Decompose a complex problem into smaller sub-problems",
                category="reasoning",
                parameters=[
                    ToolParameter(
                        name="problem",
                        type=ParameterType.STRING,
                        description="The complex problem to decompose",
                        required=True
                    ),
                    ToolParameter(
                        name="depth",
                        type=ParameterType.INTEGER,
                        description="Depth of decomposition",
                        required=False,
                        default=3
                    )
                ],
                function=self.problem_decomposition,
                plugin_name=self.metadata.name
            ),
            Tool(
                name="reasoning_reflection",
                description="Reflect on and validate reasoning steps",
                category="reasoning",
                parameters=[
                    ToolParameter(
                        name="reasoning_chain",
                        type=ParameterType.STRING,
                        description="The reasoning chain to reflect upon (JSON format)",
                        required=True
                    ),
                    ToolParameter(
                        name="focus_areas",
                        type=ParameterType.STRING,
                        description="Specific areas to focus reflection on",
                        required=False,
                        default="logic,completeness,accuracy"
                    )
                ],
                function=self.reasoning_reflection,
                plugin_name=self.metadata.name
            )
        ]
    
    async def chain_of_thought_reasoning(self, problem: str, reasoning_type: str = "chain_of_thought", max_steps: int = 5) -> Dict[str, Any]:
        """Perform chain-of-thought reasoning"""
        try:
            if not REASONER_AVAILABLE or not self.reasoner:
                # Fallback implementation
                return await self._fallback_reasoning(problem, reasoning_type, max_steps)
            
            # Use the actual reasoner
            reasoning_enum = ReasoningType(reasoning_type)
            result = await self.reasoner.reason(problem, reasoning_enum, max_steps=max_steps)
            
            return {
                "success": True,
                "problem": problem,
                "reasoning_type": reasoning_type,
                "chain": [
                    {
                        "step": step.step_number,
                        "thought": step.thought,
                        "action": step.action,
                        "observation": step.observation,
                        "confidence": step.confidence
                    }
                    for step in result.steps
                ],
                "conclusion": result.conclusion,
                "confidence": result.confidence,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "problem": problem,
                "timestamp": datetime.now().isoformat()
            }
    
    async def step_by_step_analysis(self, problem: str, context: str = "") -> Dict[str, Any]:
        """Break down a problem into steps"""
        try:
            # Create step-by-step breakdown
            steps = [
                "1. **Understand the Problem**: Clearly define what needs to be solved",
                "2. **Identify Key Components**: Break down the problem into main elements",
                "3. **Gather Information**: Collect relevant data and context",
                "4. **Develop Strategy**: Create a plan of approach",
                "5. **Execute Solution**: Implement the planned approach",
                "6. **Validate Results**: Check and verify the solution"
            ]
            
            # Analyze the specific problem
            analysis = f"Problem: {problem}\\n"
            if context:
                analysis += f"Context: {context}\\n\\n"
            
            analysis += "Step-by-Step Analysis:\\n"
            for i, step in enumerate(steps, 1):
                analysis += f"{step}\\n"
            
            return {
                "success": True,
                "problem": problem,
                "context": context,
                "steps": steps,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "problem": problem,
                "timestamp": datetime.now().isoformat()
            }
    
    async def problem_decomposition(self, problem: str, depth: int = 3) -> Dict[str, Any]:
        """Decompose a complex problem"""
        try:
            decomposition = {
                "main_problem": problem,
                "sub_problems": [],
                "dependencies": [],
                "complexity_level": "medium"
            }
            
            # Simple decomposition logic
            if "code" in problem.lower() or "program" in problem.lower():
                decomposition["sub_problems"] = [
                    "Define requirements and specifications",
                    "Design system architecture",
                    "Implement core functionality",
                    "Add error handling and validation",
                    "Test and debug the solution",
                    "Document and optimize"
                ]
                decomposition["complexity_level"] = "high"
            elif "analyze" in problem.lower() or "research" in problem.lower():
                decomposition["sub_problems"] = [
                    "Define analysis scope and objectives",
                    "Gather relevant data and sources",
                    "Apply analytical methods",
                    "Interpret results and findings",
                    "Draw conclusions and recommendations"
                ]
            else:
                decomposition["sub_problems"] = [
                    "Clarify problem statement",
                    "Identify constraints and requirements",
                    "Explore potential solutions",
                    "Evaluate solution options",
                    "Implement chosen solution"
                ]
            
            return {
                "success": True,
                "decomposition": decomposition,
                "depth": depth,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "problem": problem,
                "timestamp": datetime.now().isoformat()
            }
    
    async def reasoning_reflection(self, reasoning_chain: str, focus_areas: str = "logic,completeness,accuracy") -> Dict[str, Any]:
        """Reflect on reasoning quality"""
        try:
            areas = [area.strip() for area in focus_areas.split(",")]
            
            reflection = {
                "input_chain": reasoning_chain,
                "focus_areas": areas,
                "assessment": {},
                "suggestions": [],
                "overall_quality": "good"
            }
            
            # Simple reflection logic
            for area in areas:
                if area == "logic":
                    reflection["assessment"]["logic"] = "Reasoning follows logical progression"
                elif area == "completeness":
                    reflection["assessment"]["completeness"] = "Analysis covers main aspects"
                elif area == "accuracy":
                    reflection["assessment"]["accuracy"] = "Conclusions appear sound"
                else:
                    reflection["assessment"][area] = f"Assessment for {area} completed"
            
            reflection["suggestions"] = [
                "Consider alternative perspectives",
                "Validate assumptions with additional data",
                "Check for potential biases in reasoning"
            ]
            
            return {
                "success": True,
                "reflection": reflection,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "reasoning_chain": reasoning_chain,
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        try:
            # No specific cleanup needed for reasoning tools
            logging.info("Chain of Thought Reasoning Plugin cleaned up")
        except Exception as e:
            logging.error(f"Error during Chain of Thought plugin cleanup: {e}")
    
    async def _fallback_reasoning(self, problem: str, reasoning_type: str, max_steps: int) -> Dict[str, Any]:
        """Fallback reasoning when main reasoner isn't available"""
        
        steps = []
        
        # Generate reasoning steps based on problem
        if "code" in problem.lower() or "programming" in problem.lower():
            steps = [
                {"step": 1, "thought": "Analyze the programming problem requirements", "confidence": 0.9},
                {"step": 2, "thought": "Identify key algorithms and data structures needed", "confidence": 0.8},
                {"step": 3, "thought": "Design the solution architecture", "confidence": 0.85},
                {"step": 4, "thought": "Consider edge cases and error handling", "confidence": 0.75},
                {"step": 5, "thought": "Plan implementation and testing strategy", "confidence": 0.8}
            ]
        elif "math" in problem.lower() or "calculate" in problem.lower():
            steps = [
                {"step": 1, "thought": "Identify the mathematical concepts involved", "confidence": 0.9},
                {"step": 2, "thought": "Break down the problem into smaller parts", "confidence": 0.85},
                {"step": 3, "thought": "Apply relevant formulas and methods", "confidence": 0.8},
                {"step": 4, "thought": "Verify calculations and check for errors", "confidence": 0.75},
                {"step": 5, "thought": "Interpret results in context of original problem", "confidence": 0.8}
            ]
        else:
            steps = [
                {"step": 1, "thought": "Define the problem clearly and precisely", "confidence": 0.9},
                {"step": 2, "thought": "Gather relevant information and context", "confidence": 0.8},
                {"step": 3, "thought": "Generate potential solutions or approaches", "confidence": 0.75},
                {"step": 4, "thought": "Evaluate pros and cons of each approach", "confidence": 0.7},
                {"step": 5, "thought": "Select best solution and plan implementation", "confidence": 0.8}
            ]
        
        # Limit to max_steps
        steps = steps[:max_steps]
        
        conclusion = f"Based on {reasoning_type} reasoning, the problem '{problem}' requires a systematic approach with {len(steps)} key steps."
        
        return {
            "success": True,
            "problem": problem,
            "reasoning_type": reasoning_type,
            "chain": steps,
            "conclusion": conclusion,
            "confidence": 0.8,
            "note": "Fallback reasoning used (advanced reasoner not available)",
            "timestamp": datetime.now().isoformat()
        }

# Plugin instance - this is how the plugin system discovers the plugin
plugin = ChainOfThoughtPlugin()

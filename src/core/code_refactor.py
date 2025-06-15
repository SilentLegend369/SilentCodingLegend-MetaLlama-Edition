"""
AI-powered code refactoring utility for intelligent code improvement suggestions
"""
import ast
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import tempfile

from config import ADVANCED_AI_CONFIG

logger = logging.getLogger(__name__)

class CodeRefactoringAgent:
    """AI-powered code refactoring and improvement suggestions system"""
    
    def __init__(self):
        self.config = ADVANCED_AI_CONFIG["code_refactoring"]
        self.analysis_patterns = self.config["analysis_patterns"]
        
    def analyze_code_quality(self, code: str, file_path: str = None) -> Dict[str, Any]:
        """
        Analyze code quality and identify improvement opportunities
        
        Args:
            code: Source code to analyze
            file_path: Optional file path for context
            
        Returns:
            Dict containing code quality analysis
        """
        try:
            tree = ast.parse(code)
            analysis = {
                "complexity_score": self._calculate_complexity(tree),
                "code_smells": self._detect_code_smells(code, tree),
                "suggestions": self._generate_suggestions(tree, code),
                "metrics": self._calculate_metrics(tree, code),
                "security_issues": self._check_security_issues(code),
                "performance_issues": self._check_performance_issues(tree, code),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Code quality analysis completed for {file_path or 'code snippet'}")
            return analysis
            
        except SyntaxError as e:
            return {
                "error": f"Syntax error in code: {e}",
                "line": getattr(e, 'lineno', 'unknown'),
                "column": getattr(e, 'col_offset', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
            return {"error": str(e)}
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate various complexity metrics"""
        complexity = {
            "cyclomatic": 0,
            "cognitive": 0,
            "lines_of_code": 0,
            "functions": 0,
            "classes": 0
        }
        
        for node in ast.walk(tree):
            # Cyclomatic complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try, 
                               ast.ExceptHandler, ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity["cyclomatic"] += 1
            
            # Count functions and classes
            if isinstance(node, ast.FunctionDef):
                complexity["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                complexity["classes"] += 1
        
        return complexity
    
    def _detect_code_smells(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect common code smells"""
        smells = []
        lines = code.split('\n')
        
        # Long parameter lists
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:
                    smells.append({
                        "type": "long_parameter_list",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' has {len(node.args.args)} parameters (consider refactoring)",
                        "severity": "medium"
                    })
        
        # Long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = getattr(node, 'end_lineno', node.lineno) - node.lineno
                if func_lines > 50:
                    smells.append({
                        "type": "long_function",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' is {func_lines} lines long (consider breaking it down)",
                        "severity": "high"
                    })
        
        # TODO comments
        for i, line in enumerate(lines, 1):
            if re.search(r'#.*TODO|#.*FIXME|#.*HACK', line, re.IGNORECASE):
                smells.append({
                    "type": "todo_comment",
                    "line": i,
                    "message": "TODO/FIXME comment found - consider addressing",
                    "severity": "low"
                })
        
        # Hardcoded values
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in [0, 1, -1] and hasattr(node, 'lineno'):
                    smells.append({
                        "type": "magic_number",
                        "line": node.lineno,
                        "message": f"Magic number {node.value} found - consider using a named constant",
                        "severity": "low"
                    })
        
        return smells
    
    def _generate_suggestions(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Suggest type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns and not any(arg.annotation for arg in node.args.args):
                    suggestions.append({
                        "type": "add_type_hints",
                        "line": node.lineno,
                        "message": f"Consider adding type hints to function '{node.name}'",
                        "example": f"def {node.name}(param: Type) -> ReturnType:"
                    })
        
        # Suggest docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    suggestions.append({
                        "type": "add_docstring",
                        "line": node.lineno,
                        "message": f"Consider adding a docstring to {node.__class__.__name__.lower()} '{node.name}'"
                    })
        
        # Suggest list comprehensions
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Simple pattern detection for loops that could be comprehensions
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Call)):
                    suggestions.append({
                        "type": "use_comprehension",
                        "line": node.lineno,
                        "message": "Consider using a list comprehension instead of a for loop"
                    })
        
        return suggestions
    
    def _calculate_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate code metrics"""
        lines = code.split('\n')
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "imports": len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]),
            "variables": len([node for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)])
        }
    
    def _check_security_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for potential security issues"""
        issues = []
        lines = code.split('\n')
        
        security_patterns = [
            (r'eval\(', "Use of eval() can be dangerous"),
            (r'exec\(', "Use of exec() can be dangerous"),
            (r'input\(', "Consider validating user input"),
            (r'open\(.*[\'\"]\w+[\'\"]\s*,\s*[\'\"]\w*w', "File write operations should be carefully validated"),
            (r'subprocess\.|os\.system', "Shell command execution should be carefully validated"),
            (r'pickle\.loads?', "Pickle can be unsafe with untrusted data"),
            (r'yaml\.load\(', "Use yaml.safe_load() instead of yaml.load()"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message in security_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "type": "security_warning",
                        "line": i,
                        "message": message,
                        "pattern": pattern
                    })
        
        return issues
    
    def _check_performance_issues(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Check for potential performance issues"""
        issues = []
        
        # Check for string concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if (isinstance(child, ast.AugAssign) and 
                        isinstance(child.op, ast.Add) and
                        isinstance(child.target, ast.Name)):
                        issues.append({
                            "type": "performance_warning",
                            "line": getattr(child, 'lineno', 'unknown'),
                            "message": "String concatenation in loop - consider using join() or f-strings",
                            "suggestion": "Use ''.join(items) or collect in list and join at end"
                        })
        
        # Check for inefficient list operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr == 'append' and
                    isinstance(node.func.value, ast.Name)):
                    # This is a basic check - more sophisticated analysis would be needed
                    pass
        
        return issues
    
    def suggest_refactoring(self, code: str, refactoring_type: str = "general") -> Dict[str, Any]:
        """
        Suggest specific refactoring based on type
        
        Args:
            code: Source code to refactor
            refactoring_type: Type of refactoring (general, performance, readability, etc.)
            
        Returns:
            Dict containing refactoring suggestions
        """
        analysis = self.analyze_code_quality(code)
        
        refactoring_suggestions = {
            "original_code": code,
            "analysis": analysis,
            "refactoring_type": refactoring_type,
            "suggestions": [],
            "estimated_impact": "medium",
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate specific suggestions based on type
        if refactoring_type == "performance":
            refactoring_suggestions["suggestions"] = self._performance_refactoring_suggestions(analysis)
        elif refactoring_type == "readability":
            refactoring_suggestions["suggestions"] = self._readability_refactoring_suggestions(analysis)
        elif refactoring_type == "security":
            refactoring_suggestions["suggestions"] = self._security_refactoring_suggestions(analysis)
        else:
            # General refactoring combines all types
            refactoring_suggestions["suggestions"] = (
                self._performance_refactoring_suggestions(analysis) +
                self._readability_refactoring_suggestions(analysis) +
                self._security_refactoring_suggestions(analysis)
            )
        
        return refactoring_suggestions
    
    def _performance_refactoring_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance-focused refactoring suggestions"""
        suggestions = []
        
        if "performance_issues" in analysis:
            for issue in analysis["performance_issues"]:
                suggestions.append({
                    "type": "performance_improvement",
                    "priority": "high",
                    "description": issue["message"],
                    "suggestion": issue.get("suggestion", "Review and optimize this code section")
                })
        
        return suggestions
    
    def _readability_refactoring_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate readability-focused refactoring suggestions"""
        suggestions = []
        
        if "code_smells" in analysis:
            for smell in analysis["code_smells"]:
                if smell["type"] in ["long_function", "long_parameter_list"]:
                    suggestions.append({
                        "type": "readability_improvement",
                        "priority": "medium",
                        "description": smell["message"],
                        "suggestion": "Consider breaking this into smaller, more focused components"
                    })
        
        if "suggestions" in analysis:
            for suggestion in analysis["suggestions"]:
                if suggestion["type"] in ["add_docstring", "add_type_hints"]:
                    suggestions.append({
                        "type": "documentation_improvement",
                        "priority": "low",
                        "description": suggestion["message"],
                        "suggestion": suggestion.get("example", "Add appropriate documentation")
                    })
        
        return suggestions
    
    def _security_refactoring_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security-focused refactoring suggestions"""
        suggestions = []
        
        if "security_issues" in analysis:
            for issue in analysis["security_issues"]:
                suggestions.append({
                    "type": "security_improvement",
                    "priority": "high",
                    "description": issue["message"],
                    "suggestion": "Review this code for security implications and apply appropriate safeguards"
                })
        
        return suggestions
    
    def generate_refactored_code(self, code: str, apply_suggestions: List[str] = None) -> Dict[str, Any]:
        """
        Generate refactored version of code (basic implementation)
        
        Args:
            code: Original code
            apply_suggestions: List of suggestion types to apply
            
        Returns:
            Dict containing original and refactored code
        """
        # This is a simplified implementation
        # A full implementation would require more sophisticated AST manipulation
        
        refactored_code = code
        applied_changes = []
        
        # Simple example transformations
        if not apply_suggestions or "add_type_hints" in apply_suggestions:
            # Add basic type hints (simplified)
            refactored_code = re.sub(
                r'def (\w+)\(([^)]+)\):',
                r'def \1(\2) -> Any:',
                refactored_code
            )
            if refactored_code != code:
                applied_changes.append("Added basic type hints")
        
        if not apply_suggestions or "improve_docstrings" in apply_suggestions:
            # Add basic docstrings (simplified)
            refactored_code = re.sub(
                r'(def \w+\([^)]*\).*?:)\n',
                r'\1\n    """TODO: Add function description"""\n',
                refactored_code
            )
        
        return {
            "original_code": code,
            "refactored_code": refactored_code,
            "applied_changes": applied_changes,
            "improvement_notes": "This is a basic refactoring example. Real-world refactoring would require more sophisticated analysis.",
            "timestamp": datetime.now().isoformat()
        }

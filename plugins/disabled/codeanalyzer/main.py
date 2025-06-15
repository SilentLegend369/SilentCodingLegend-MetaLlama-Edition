"""
Code Analyzer Plugin for SilentCodingLegend AI Agent
"""

import ast
import os
from typing import Dict, List, Any
from src.plugins.base_plugin import ToolPlugin, PluginMetadata, PluginType

class CodeAnalyzerPlugin(ToolPlugin):
    """Plugin providing code analysis capabilities"""
    
    async def initialize(self) -> bool:
        """Initialize the code analyzer plugin"""
        
        self.register_tool(
            "analyze_python_code",
            self.analyze_python_code,
            "Analyze Python code for metrics and issues",
            {
                "code": {"type": "string", "description": "Python code to analyze", "required": True}
            }
        )
        
        self.register_tool(
            "count_lines_of_code",
            self.count_lines_of_code,
            "Count lines of code in a file or directory",
            {
                "path": {"type": "string", "description": "File or directory path", "required": True}
            }
        )
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in Llama format"""
        return [tool.to_llama_schema() for tool in self._tools.values()]
    
    async def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code and return metrics"""
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "lines": len(code.split('\n')),
                "complexity_score": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis["imports"] += 1
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    analysis["complexity_score"] += 1
            
            return analysis
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze code: {e}")
    
    async def count_lines_of_code(self, path: str) -> Dict[str, int]:
        """Count lines of code in files"""
        try:
            total_lines = 0
            total_files = 0
            
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    total_lines = len(f.readlines())
                    total_files = 1
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as f:
                                    total_lines += len(f.readlines())
                                    total_files += 1
                            except:
                                continue
            
            return {
                "total_lines": total_lines,
                "total_files": total_files,
                "average_lines_per_file": total_lines // max(total_files, 1)
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to count lines of code: {e}")

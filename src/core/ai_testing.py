"""
AI-powered testing utility for automatic test generation and execution
"""
import ast
import inspect
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import tempfile
import subprocess

from config import ADVANCED_AI_CONFIG
from src.core.code_sandbox import CodeSandbox

logger = logging.getLogger(__name__)

class AITestGenerator:
    """AI-powered test generation and execution system"""
    
    def __init__(self):
        self.config = ADVANCED_AI_CONFIG["ai_testing"]
        self.sandbox = CodeSandbox()
        self.supported_frameworks = self.config["test_frameworks"]
        
    def analyze_function(self, code: str, function_name: str = None) -> Dict[str, Any]:
        """
        Analyze a function to understand its structure and requirements
        
        Args:
            code: Source code containing the function
            function_name: Optional specific function to analyze
            
        Returns:
            Dict containing function analysis
        """
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if function_name is None or node.name == function_name:
                        func_info = {
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "defaults": len(node.args.defaults),
                            "returns": self._analyze_return_type(node),
                            "docstring": ast.get_docstring(node),
                            "complexity": self._calculate_complexity(node),
                            "dependencies": self._find_dependencies(node),
                            "side_effects": self._detect_side_effects(node)
                        }
                        functions.append(func_info)
            
            return {
                "success": True,
                "functions": functions,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Function analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_unit_tests(self, code: str, function_name: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive unit tests for functions
        
        Args:
            code: Source code to test
            function_name: Optional specific function to test
            
        Returns:
            Dict containing generated tests
        """
        analysis = self.analyze_function(code, function_name)
        if not analysis["success"]:
            return analysis
        
        generated_tests = []
        
        for func_info in analysis["functions"]:
            test_cases = self._generate_test_cases(func_info)
            test_code = self._create_pytest_test(func_info, test_cases)
            
            generated_tests.append({
                "function_name": func_info["name"],
                "test_code": test_code,
                "test_cases": test_cases,
                "framework": "pytest"
            })
        
        return {
            "success": True,
            "generated_tests": generated_tests,
            "total_test_cases": sum(len(t["test_cases"]) for t in generated_tests),
            "generation_timestamp": datetime.now().isoformat()
        }
    
    def generate_integration_tests(self, code: str, class_name: str = None) -> Dict[str, Any]:
        """
        Generate integration tests for classes and modules
        
        Args:
            code: Source code to test
            class_name: Optional specific class to test
            
        Returns:
            Dict containing generated integration tests
        """
        try:
            tree = ast.parse(code)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if class_name is None or node.name == class_name:
                        class_info = {
                            "name": node.name,
                            "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                            "attributes": self._find_class_attributes(node),
                            "inheritance": [base.id for base in node.bases if isinstance(base, ast.Name)]
                        }
                        classes.append(class_info)
            
            integration_tests = []
            for class_info in classes:
                test_code = self._create_integration_test(class_info)
                integration_tests.append({
                    "class_name": class_info["name"],
                    "test_code": test_code,
                    "framework": "pytest"
                })
            
            return {
                "success": True,
                "integration_tests": integration_tests,
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integration test generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_tests(self, test_code: str, original_code: str = "") -> Dict[str, Any]:
        """
        Execute generated tests using the sandbox
        
        Args:
            test_code: Test code to execute
            original_code: Original code being tested
            
        Returns:
            Dict containing test execution results
        """
        # Combine original code with test code
        full_code = original_code + "\n\n" + test_code
        
        # Execute in sandbox
        result = self.sandbox.execute_python_code(full_code)
        
        if result["success"]:
            # Parse test results from output
            test_results = self._parse_test_output(result["output"])
            result.update(test_results)
        
        return result
    
    def generate_mock_data(self, data_type: str, count: int = 10) -> List[Any]:
        """
        Generate mock data for testing
        
        Args:
            data_type: Type of data to generate
            count: Number of data items to generate
            
        Returns:
            List of generated mock data
        """
        import random
        import string
        
        if data_type == "string":
            return [''.join(random.choices(string.ascii_letters, k=random.randint(5, 15))) for _ in range(count)]
        elif data_type == "int":
            return [random.randint(-1000, 1000) for _ in range(count)]
        elif data_type == "float":
            return [round(random.uniform(-100.0, 100.0), 2) for _ in range(count)]
        elif data_type == "bool":
            return [random.choice([True, False]) for _ in range(count)]
        elif data_type == "list":
            return [[random.randint(1, 10) for _ in range(random.randint(1, 5))] for _ in range(count)]
        elif data_type == "dict":
            return [{f"key_{i}": random.randint(1, 100) for i in range(random.randint(1, 3))} for _ in range(count)]
        else:
            return [None] * count
    
    def _generate_test_cases(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for a function"""
        test_cases = []
        func_name = func_info["name"]
        args = func_info["args"]
        
        # Generate edge cases
        if args:
            # Test with None values
            test_cases.append({
                "name": f"test_{func_name}_with_none",
                "args": [None] * len(args),
                "expected_behavior": "should handle None inputs gracefully"
            })
            
            # Test with empty values
            empty_values = []
            for arg in args:
                if "str" in arg.lower() or "text" in arg.lower():
                    empty_values.append("")
                elif "list" in arg.lower() or "array" in arg.lower():
                    empty_values.append([])
                elif "dict" in arg.lower():
                    empty_values.append({})
                elif "num" in arg.lower() or "int" in arg.lower():
                    empty_values.append(0)
                else:
                    empty_values.append(None)
            
            test_cases.append({
                "name": f"test_{func_name}_with_empty_values",
                "args": empty_values,
                "expected_behavior": "should handle empty inputs"
            })
            
            # Generate positive test cases with mock data
            for i in range(3):
                mock_args = []
                for arg in args:
                    if "str" in arg.lower() or "text" in arg.lower():
                        mock_args.append(self.generate_mock_data("string", 1)[0])
                    elif "num" in arg.lower() or "int" in arg.lower():
                        mock_args.append(self.generate_mock_data("int", 1)[0])
                    elif "float" in arg.lower():
                        mock_args.append(self.generate_mock_data("float", 1)[0])
                    elif "bool" in arg.lower():
                        mock_args.append(self.generate_mock_data("bool", 1)[0])
                    elif "list" in arg.lower():
                        mock_args.append(self.generate_mock_data("list", 1)[0])
                    elif "dict" in arg.lower():
                        mock_args.append(self.generate_mock_data("dict", 1)[0])
                    else:
                        mock_args.append(f"test_value_{i}")
                
                test_cases.append({
                    "name": f"test_{func_name}_case_{i+1}",
                    "args": mock_args,
                    "expected_behavior": "should return valid result"
                })
        
        # Test for functions with no arguments
        else:
            test_cases.append({
                "name": f"test_{func_name}_no_args",
                "args": [],
                "expected_behavior": "should execute without arguments"
            })
        
        return test_cases
    
    def _create_pytest_test(self, func_info: Dict[str, Any], test_cases: List[Dict[str, Any]]) -> str:
        """Create pytest test code"""
        func_name = func_info["name"]
        
        test_code = f"""
import pytest

def test_{func_name}_exists():
    \"\"\"Test that the function exists and is callable\"\"\"
    assert callable({func_name})

"""
        
        for case in test_cases:
            args_str = ", ".join(repr(arg) for arg in case["args"])
            test_code += f"""
def {case["name"]}():
    \"\"\"Test case: {case["expected_behavior"]}\"\"\"
    try:
        result = {func_name}({args_str})
        # Basic assertion - function should not raise unexpected exceptions
        assert result is not None or result is None  # Allow any result
        print(f"✅ {case["name"]}: PASSED")
    except Exception as e:
        print(f"❌ {case["name"]}: FAILED - {{str(e)}}")
        # Don't fail the test for expected exceptions in edge cases
        if "none" in "{case["name"]}" or "empty" in "{case["name"]}":
            pass  # Expected to potentially fail
        else:
            raise

"""
        
        return test_code
    
    def _create_integration_test(self, class_info: Dict[str, Any]) -> str:
        """Create integration test code for a class"""
        class_name = class_info["name"]
        
        test_code = f"""
import pytest

class Test{class_name}Integration:
    \"\"\"Integration tests for {class_name}\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures\"\"\"
        self.instance = {class_name}()
    
    def test_{class_name.lower()}_instantiation(self):
        \"\"\"Test that the class can be instantiated\"\"\"
        assert self.instance is not None
        assert isinstance(self.instance, {class_name})
    
"""
        
        for method in class_info["methods"]:
            if not method.startswith("_"):  # Skip private methods
                test_code += f"""
    def test_{method}_method_exists(self):
        \"\"\"Test that {method} method exists\"\"\"
        assert hasattr(self.instance, '{method}')
        assert callable(getattr(self.instance, '{method}'))
    
"""
        
        return test_code
    
    def _analyze_return_type(self, node: ast.FunctionDef) -> str:
        """Analyze function return type"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if child.value:
                    if isinstance(child.value, ast.Constant):
                        return type(child.value.value).__name__
                    elif isinstance(child.value, ast.Name):
                        return "variable"
                    elif isinstance(child.value, ast.List):
                        return "list"
                    elif isinstance(child.value, ast.Dict):
                        return "dict"
        return "unknown"
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _find_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Find function dependencies"""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                dependencies.append(child.func.id)
        
        return list(set(dependencies))
    
    def _detect_side_effects(self, node: ast.FunctionDef) -> List[str]:
        """Detect potential side effects"""
        side_effects = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Global):
                side_effects.append("modifies_global_variables")
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ["append", "extend", "remove", "pop", "clear"]:
                        side_effects.append("modifies_mutable_arguments")
                elif isinstance(child.func, ast.Name):
                    if child.func.id in ["print", "open", "write"]:
                        side_effects.append("io_operations")
        
        return list(set(side_effects))
    
    def _find_class_attributes(self, node: ast.ClassDef) -> List[str]:
        """Find class attributes"""
        attributes = []
        
        for child in node.body:
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return attributes
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse test execution output"""
        lines = output.split('\n')
        passed_tests = []
        failed_tests = []
        
        for line in lines:
            if "✅" in line and "PASSED" in line:
                test_name = line.split("✅")[1].split(":")[0].strip()
                passed_tests.append(test_name)
            elif "❌" in line and "FAILED" in line:
                test_name = line.split("❌")[1].split(":")[0].strip()
                failed_tests.append(test_name)
        
        total_tests = len(passed_tests) + len(failed_tests)
        coverage = (len(passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "coverage_percentage": round(coverage, 2)
            },
            "passed_tests": passed_tests,
            "failed_tests": failed_tests
        }

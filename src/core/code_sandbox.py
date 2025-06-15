"""
Secure code execution sandbox for safe code testing and execution
"""
import os
import sys
import subprocess
import tempfile
import logging
import time
import signal
import resource
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import ast
import contextlib
import io
from datetime import datetime

from config import ADVANCED_AI_CONFIG

logger = logging.getLogger(__name__)

class CodeSandbox:
    """Secure sandbox environment for code execution"""
    
    def __init__(self):
        self.config = ADVANCED_AI_CONFIG["code_sandbox"]
        self.timeout = self.config["timeout_seconds"]
        self.memory_limit = self.config["memory_limit_mb"] * 1024 * 1024  # Convert to bytes
        self.max_output_lines = self.config["max_output_lines"]
        self.allowed_imports = set(self.config["allowed_imports"])
        self.restricted_functions = set(self.config["restricted_functions"])
        self.sandbox_dir = Path(self.config["sandbox_directory"])
        
        # Create sandbox directory if it doesn't exist
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_python_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate Python code for security and syntax
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Parse the code to check syntax
            tree = ast.parse(code)
            
            # Check for restricted functions and imports
            for node in ast.walk(tree):
                # Check for restricted function calls
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in self.restricted_functions:
                        return False, f"Restricted function: {node.func.id}"
                
                # Check for restricted imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.allowed_imports and not alias.name.startswith('_'):
                            return False, f"Restricted import: {alias.name}"
                
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in self.allowed_imports:
                        return False, f"Restricted import: {node.module}"
                
                # Check for file operations
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['open', 'file']:
                        return False, "File operations are restricted in sandbox"
                
                # Check for system operations
                if isinstance(node, ast.Attribute):
                    if node.attr in ['system', 'popen', 'spawn']:
                        return False, f"System operation restricted: {node.attr}"
            
            return True, ""
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def execute_python_code(self, code: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute Python code safely in sandbox
        
        Args:
            code: Python code to execute
            input_data: Optional input data for the code
            
        Returns:
            Dict containing execution results
        """
        # Validate code first
        is_valid, error_msg = self.validate_python_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Code validation failed: {error_msg}",
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            # Create a restricted execution environment
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Create safe globals with restricted builtins
            safe_builtins = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'reversed': reversed,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'round': round,
                }
            }
            
            # Add allowed imports to globals
            for module_name in self.allowed_imports:
                try:
                    safe_builtins[module_name] = __import__(module_name)
                except ImportError:
                    logger.warning(f"Failed to import allowed module: {module_name}")
            
            # Redirect stdout and stderr
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):
                
                # Set resource limits
                try:
                    # Limit memory usage (Unix-like systems only)
                    if hasattr(resource, 'RLIMIT_AS'):
                        resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
                except (OSError, AttributeError):
                    logger.warning("Could not set memory limit")
                
                # Execute the code with timeout
                def timeout_handler(signum, frame):
                    raise TimeoutError("Code execution timed out")
                
                # Set timeout (Unix-like systems only)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.timeout)
                except AttributeError:
                    logger.warning("Timeout not available on this system")
                
                try:
                    # Execute the code
                    exec(code, safe_builtins)
                finally:
                    # Cancel the alarm
                    try:
                        signal.alarm(0)
                    except AttributeError:
                        pass
            
            # Capture output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            # Limit output length
            output_lines = stdout_output.split('\n')
            if len(output_lines) > self.max_output_lines:
                stdout_output = '\n'.join(output_lines[:self.max_output_lines]) + \
                               f'\n... (output truncated, {len(output_lines)} total lines)'
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "output": stdout_output,
                "error": stderr_output,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except TimeoutError:
            return {
                "success": False,
                "error": f"Code execution timed out after {self.timeout} seconds",
                "execution_time": time.time() - start_time
            }
        except MemoryError:
            return {
                "success": False,
                "error": f"Code execution exceeded memory limit ({self.config['memory_limit_mb']}MB)",
                "execution_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    def execute_javascript(self, code: str) -> Dict[str, Any]:
        """
        Execute JavaScript code using Node.js
        
        Args:
            code: JavaScript code to execute
            
        Returns:
            Dict containing execution results
        """
        start_time = time.time()
        
        try:
            # Create temporary file for the JavaScript code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute JavaScript using Node.js
                result = subprocess.run(
                    ['node', temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=self.sandbox_dir
                )
                
                execution_time = time.time() - start_time
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "execution_time": execution_time,
                    "return_code": result.returncode,
                    "timestamp": datetime.now().isoformat()
                }
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"JavaScript execution timed out after {self.timeout} seconds",
                "execution_time": time.time() - start_time
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Node.js not found. Please install Node.js to execute JavaScript code.",
                "execution_time": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"JavaScript execution error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    def execute_bash(self, command: str) -> Dict[str, Any]:
        """
        Execute bash commands safely
        
        Args:
            command: Bash command to execute
            
        Returns:
            Dict containing execution results
        """
        # Whitelist of safe commands
        safe_commands = {
            'ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'wc', 'grep', 'find',
            'sort', 'uniq', 'cut', 'tr', 'date', 'whoami', 'uname'
        }
        
        # Check if command starts with a safe command
        first_word = command.strip().split()[0] if command.strip() else ""
        if first_word not in safe_commands:
            return {
                "success": False,
                "error": f"Command '{first_word}' is not allowed in sandbox",
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.sandbox_dir
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command execution timed out after {self.timeout} seconds",
                "execution_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    def execute_code(self, code: str, language: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Main execution function that routes to appropriate language handler
        
        Args:
            code: Code to execute
            language: Programming language
            input_data: Optional input data
            
        Returns:
            Dict containing execution results
        """
        language = language.lower()
        
        if language == "python":
            return self.execute_python_code(code, input_data)
        elif language == "javascript" or language == "js":
            return self.execute_javascript(code)
        elif language == "bash" or language == "shell":
            return self.execute_bash(code)
        else:
            return {
                "success": False,
                "error": f"Language '{language}' is not supported in sandbox",
                "execution_time": 0
            }
    
    def cleanup_sandbox(self) -> bool:
        """
        Clean up sandbox directory
        
        Returns:
            bool: True if cleanup successful
        """
        try:
            # Remove temporary files older than 1 hour
            current_time = time.time()
            for file_path in self.sandbox_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 3600:  # 1 hour
                        file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Sandbox cleanup failed: {e}")
            return False

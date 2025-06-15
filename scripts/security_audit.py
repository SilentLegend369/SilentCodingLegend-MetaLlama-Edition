#!/usr/bin/env python3
"""
Security Audit Script for SilentCodingLegend AI Agent
Checks for security best practices and potential vulnerabilities
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any

class SecurityAuditor:
    """Security auditor for the Streamlit application"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        
    def audit_unsafe_html(self) -> List[Dict[str, Any]]:
        """Check for unsafe HTML usage"""
        issues = []
        
        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        if "unsafe_allow_html=True" in line:
                            # Check if it's for CSS loading (acceptable)
                            if any(keyword in line.lower() for keyword in ['css', 'style', 'load_css']):
                                issues.append({
                                    "type": "info",
                                    "file": str(file_path.relative_to(self.project_root)),
                                    "line": i,
                                    "issue": "Acceptable unsafe HTML usage for CSS",
                                    "content": line.strip()
                                })
                            else:
                                issues.append({
                                    "type": "warning",
                                    "file": str(file_path.relative_to(self.project_root)),
                                    "line": i,
                                    "issue": "Unsafe HTML usage found",
                                    "content": line.strip()
                                })
            except Exception as e:
                issues.append({
                    "type": "error",
                    "file": str(file_path.relative_to(self.project_root)),
                    "line": 0,
                    "issue": f"Failed to read file: {e}",
                    "content": ""
                })
        
        return issues
    
    def audit_hardcoded_values(self) -> List[Dict[str, Any]]:
        """Check for hardcoded configuration values"""
        issues = []
        
        # Common hardcoded patterns to look for
        patterns = [
            (r'"#[0-9A-Fa-f]{6}"', "Hardcoded color value"),
            (r'page_title\s*=\s*["\'][^"\']+["\']', "Hardcoded page title"),
            (r'page_icon\s*=\s*["\'][^"\']+["\']', "Hardcoded page icon"),
            (r'layout\s*=\s*["\'][^"\']+["\']', "Hardcoded layout"),
        ]
        
        python_files = list(self.project_root.glob("**/*.py"))
        
        for file_path in python_files:
            # Skip config files
            if "config.py" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, description in patterns:
                            if re.search(pattern, line):
                                issues.append({
                                    "type": "info",
                                    "file": str(file_path.relative_to(self.project_root)),
                                    "line": i,
                                    "issue": description,
                                    "content": line.strip()
                                })
            except Exception as e:
                continue
        
        return issues
    
    def audit_input_validation(self) -> List[Dict[str, Any]]:
        """Check for proper input validation"""
        issues = []
        
        python_files = list(self.project_root.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for st.chat_input usage
                    if "st.chat_input" in content and "len(" not in content:
                        issues.append({
                            "type": "warning",
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": 0,
                            "issue": "Chat input without length validation",
                            "content": "Check if input length is validated"
                        })
                        
                    # Look for user input handling
                    if "st.text_input" in content or "st.text_area" in content:
                        if "len(" not in content and "validate" not in content.lower():
                            issues.append({
                                "type": "info",
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": 0,
                                "issue": "Text input without apparent validation",
                                "content": "Consider adding input validation"
                            })
            except Exception as e:
                continue
        
        return issues
    
    def audit_error_handling(self) -> List[Dict[str, Any]]:
        """Check for proper error handling"""
        issues = []
        
        python_files = list(self.project_root.glob("**/*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Count try-except blocks vs functions
                    try_count = content.count("try:")
                    except_count = content.count("except")
                    function_count = content.count("def ")
                    
                    if function_count > 5 and try_count < 2:
                        issues.append({
                            "type": "info",
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": 0,
                            "issue": f"Low error handling ratio: {try_count} try blocks for {function_count} functions",
                            "content": "Consider adding more error handling"
                        })
                        
                    # Check for bare except clauses
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.match(r'\s*except\s*:', line):
                            issues.append({
                                "type": "warning",
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": i,
                                "issue": "Bare except clause found",
                                "content": line.strip()
                            })
            except Exception as e:
                continue
        
        return issues
    
    def audit_async_safety(self) -> List[Dict[str, Any]]:
        """Check for async safety in Streamlit context"""
        issues = []
        
        python_files = list(self.project_root.glob("**/*.py"))
        
        for file_path in python_files:
            # Skip if not a Streamlit-related file
            if "streamlit" not in str(file_path).lower() and "pages" not in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        # Check for asyncio.run in Streamlit context
                        if "asyncio.run" in line and "streamlit" in content.lower():
                            issues.append({
                                "type": "warning",
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": i,
                                "issue": "asyncio.run usage in Streamlit context",
                                "content": line.strip()
                            })
                            
                        # Check for await without proper async wrapper
                        if "await " in line and "async def" not in content:
                            issues.append({
                                "type": "warning",
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": i,
                                "issue": "await usage without async function",
                                "content": line.strip()
                            })
            except Exception as e:
                continue
        
        return issues
    
    def run_full_audit(self) -> Dict[str, List[Dict[str, Any]]]:
        """Run complete security audit"""
        return {
            "unsafe_html": self.audit_unsafe_html(),
            "hardcoded_values": self.audit_hardcoded_values(),
            "input_validation": self.audit_input_validation(),
            "error_handling": self.audit_error_handling(),
            "async_safety": self.audit_async_safety()
        }
    
    def print_audit_report(self, results: Dict[str, List[Dict[str, Any]]]):
        """Print formatted audit report"""
        print("🔒 SECURITY AUDIT REPORT")
        print("=" * 50)
        
        total_issues = sum(len(issues) for issues in results.values())
        
        for category, issues in results.items():
            print(f"\n📋 {category.upper().replace('_', ' ')}")
            print("-" * 30)
            
            if not issues:
                print("✅ No issues found")
                continue
            
            for issue in issues:
                icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue["type"], "⚪")
                print(f"{icon} {issue['file']}:{issue['line']}")
                print(f"   {issue['issue']}")
                if issue['content']:
                    print(f"   Content: {issue['content']}")
                print()
        
        print(f"\n📊 SUMMARY: {total_issues} total issues found")
        
        # Count by severity
        all_issues = [issue for issues in results.values() for issue in issues]
        errors = len([i for i in all_issues if i['type'] == 'error'])
        warnings = len([i for i in all_issues if i['type'] == 'warning'])
        infos = len([i for i in all_issues if i['type'] == 'info'])
        
        print(f"   🔴 Errors: {errors}")
        print(f"   🟡 Warnings: {warnings}")
        print(f"   🔵 Info: {infos}")

def main():
    """Run security audit"""
    project_root = "/home/silentcodinglegendkali/scl-llamaapi"
    
    auditor = SecurityAuditor(project_root)
    results = auditor.run_full_audit()
    auditor.print_audit_report(results)

if __name__ == "__main__":
    main()

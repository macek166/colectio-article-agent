"""
Property-based tests for code quality verification.

Feature: tcg-content-generator, Property 12: Type hint completeness
Feature: tcg-content-generator, Property 13: Pylint code quality
Validates: Requirements 11.2, 11.3
"""

import ast
import os
import subprocess
from pathlib import Path
from typing import List, Tuple

import pytest
from hypothesis import given, settings, strategies as st


def get_all_python_files() -> List[Path]:
    """Get all Python files in the src directory."""
    src_dir = Path("src")
    if not src_dir.exists():
        return []
    
    python_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                python_files.append(Path(root) / file)
    
    return python_files


def extract_functions_and_methods(file_path: Path) -> List[Tuple[str, ast.FunctionDef]]:
    """Extract all function and method definitions from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return []
    
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append((str(file_path), node))
    
    return functions


def has_type_hints(func_def: ast.FunctionDef) -> Tuple[bool, List[str]]:
    """
    Check if a function has type hints for all parameters and return value.
    
    Returns:
        Tuple of (has_complete_hints, list_of_missing_hints)
    """
    missing = []
    
    # Check parameters (skip 'self' and 'cls')
    for arg in func_def.args.args:
        if arg.arg not in ('self', 'cls') and arg.annotation is None:
            missing.append(f"parameter '{arg.arg}'")
    
    # Check return type (skip __init__ methods)
    if func_def.name != '__init__' and func_def.returns is None:
        missing.append("return type")
    
    return len(missing) == 0, missing


def test_property_12_type_hint_completeness():
    """
    Feature: tcg-content-generator, Property 12: Type hint completeness
    
    For any function definition in the src directory, the system should include
    type hints for all parameters (except 'self' and 'cls') and return values
    (except __init__ methods).
    
    **Validates: Requirements 11.2**
    """
    python_files = get_all_python_files()
    
    # Property verification: There should be Python files to check
    assert len(python_files) > 0, "No Python files found in src directory"
    
    functions_without_hints = []
    
    for file_path in python_files:
        functions = extract_functions_and_methods(file_path)
        
        for file_name, func_def in functions:
            has_hints, missing = has_type_hints(func_def)
            
            if not has_hints:
                functions_without_hints.append({
                    'file': file_name,
                    'function': func_def.name,
                    'line': func_def.lineno,
                    'missing': missing
                })
    
    # Property verification: All functions should have complete type hints
    if functions_without_hints:
        error_msg = "\n\nFunctions missing type hints:\n"
        for item in functions_without_hints:
            error_msg += f"\n  {item['file']}:{item['line']} - {item['function']}()"
            error_msg += f"\n    Missing: {', '.join(item['missing'])}"
        
        pytest.fail(error_msg)


def run_pylint_on_file(file_path: Path) -> Tuple[float, str]:
    """
    Run Pylint on a single file and return the score.
    
    Returns:
        Tuple of (score, output)
    """
    try:
        result = subprocess.run(
            ['pylint', str(file_path), '--output-format=text'],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        output = result.stdout
        
        # Extract score from output
        # Pylint outputs: "Your code has been rated at X.XX/10"
        for line in output.split('\n'):
            if 'rated at' in line:
                try:
                    score_str = line.split('rated at')[1].split('/')[0].strip()
                    score = float(score_str)
                    return score, output
                except (IndexError, ValueError):
                    pass
        
        # If we can't find the score, return 0
        return 0.0, output
        
    except subprocess.TimeoutExpired:
        return 0.0, "Pylint timed out"
    except FileNotFoundError:
        return 0.0, "Pylint not found - please install: pip install pylint"


def test_property_13_pylint_code_quality():
    """
    Feature: tcg-content-generator, Property 13: Pylint code quality
    
    For any Python module in the src directory, running Pylint should produce
    a score of at least 8.0/10.
    
    **Validates: Requirements 11.3**
    """
    python_files = get_all_python_files()
    
    # Property verification: There should be Python files to check
    assert len(python_files) > 0, "No Python files found in src directory"
    
    min_score = 8.0
    files_below_threshold = []
    
    for file_path in python_files:
        score, output = run_pylint_on_file(file_path)
        
        if score < min_score:
            files_below_threshold.append({
                'file': str(file_path),
                'score': score,
                'output': output
            })
    
    # Property verification: All files should meet minimum Pylint score
    if files_below_threshold:
        error_msg = f"\n\nFiles below Pylint threshold ({min_score}/10):\n"
        for item in files_below_threshold:
            error_msg += f"\n  {item['file']}: {item['score']:.2f}/10"
            
            # Include first few lines of Pylint output for context
            output_lines = item['output'].split('\n')[:20]
            error_msg += "\n    " + "\n    ".join(output_lines)
        
        pytest.fail(error_msg)


@given(file_index=st.integers(min_value=0, max_value=100))
@settings(max_examples=10, deadline=60000)
def test_property_12_type_hints_for_random_files(file_index: int):
    """
    Feature: tcg-content-generator, Property 12: Type hint completeness (property test)
    
    For any randomly selected Python file, all functions should have complete
    type hints.
    
    **Validates: Requirements 11.2**
    """
    python_files = get_all_python_files()
    
    if not python_files:
        pytest.skip("No Python files found")
    
    # Select a file using modulo to wrap around
    file_path = python_files[file_index % len(python_files)]
    
    functions = extract_functions_and_methods(file_path)
    
    if not functions:
        # File has no functions, which is acceptable
        return
    
    functions_without_hints = []
    
    for file_name, func_def in functions:
        has_hints, missing = has_type_hints(func_def)
        
        if not has_hints:
            functions_without_hints.append({
                'function': func_def.name,
                'line': func_def.lineno,
                'missing': missing
            })
    
    # Property verification: All functions in this file should have type hints
    if functions_without_hints:
        error_msg = f"\n\nFile {file_path} has functions missing type hints:\n"
        for item in functions_without_hints:
            error_msg += f"\n  Line {item['line']} - {item['function']}()"
            error_msg += f"\n    Missing: {', '.join(item['missing'])}"
        
        pytest.fail(error_msg)


@given(file_index=st.integers(min_value=0, max_value=100))
@settings(max_examples=5, deadline=60000)
def test_property_13_pylint_quality_for_random_files(file_index: int):
    """
    Feature: tcg-content-generator, Property 13: Pylint code quality (property test)
    
    For any randomly selected Python file, Pylint should produce a score of
    at least 8.0/10.
    
    **Validates: Requirements 11.3**
    """
    python_files = get_all_python_files()
    
    if not python_files:
        pytest.skip("No Python files found")
    
    # Select a file using modulo to wrap around
    file_path = python_files[file_index % len(python_files)]
    
    min_score = 8.0
    score, output = run_pylint_on_file(file_path)
    
    # Property verification: File should meet minimum Pylint score
    if score < min_score:
        error_msg = f"\n\nFile {file_path} scored {score:.2f}/10 (minimum: {min_score}/10)\n"
        
        # Include first few lines of Pylint output for context
        output_lines = output.split('\n')[:30]
        error_msg += "\n" + "\n".join(output_lines)
        
        pytest.fail(error_msg)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

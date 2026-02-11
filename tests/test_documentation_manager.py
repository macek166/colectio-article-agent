"""Unit tests for Documentation Manager."""

import tempfile
from pathlib import Path

from src.utils.documentation_manager import DocumentationManager


def test_documentation_manager_initialization():
    """Test that DocumentationManager initializes correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Verify files were created
        assert doc_manager.documentation_file.exists()
        assert doc_manager.problems_file.exists()
        
        # Verify initial content
        with open(doc_manager.documentation_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "System Documentation" in content
        
        with open(doc_manager.problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "System Problems" in content


def test_log_event():
    """Test logging an event to DOCUMENTATION.md."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log an event
        doc_manager.log_event("Test Event", "This is a test event")
        
        # Verify content
        with open(doc_manager.documentation_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test Event" in content
            assert "This is a test event" in content
            assert "Timestamp:" in content


def test_log_problem():
    """Test logging a problem to PROBLEMS.md."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log a problem
        doc_manager.log_problem("Test Issue", "active", "This is a test issue")
        
        # Verify content
        with open(doc_manager.problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test Issue" in content
            assert "active" in content
            assert "This is a test issue" in content
            assert "Timestamp:" in content


def test_update_problem_status():
    """Test updating problem status in PROBLEMS.md."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log a problem
        doc_manager.log_problem("Test Issue", "active", "This is a test issue")
        
        # Update status
        doc_manager.update_problem_status("Test Issue", "resolved")
        
        # Verify updated status
        with open(doc_manager.problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "**Status:** resolved" in content


def test_multiple_events():
    """Test logging multiple events."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log multiple events
        doc_manager.log_event("Event 1", "First event")
        doc_manager.log_event("Event 2", "Second event")
        doc_manager.log_event("Event 3", "Third event")
        
        # Verify all events are present
        with open(doc_manager.documentation_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Event 1" in content
            assert "Event 2" in content
            assert "Event 3" in content


def test_multiple_problems():
    """Test logging multiple problems."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log multiple problems
        doc_manager.log_problem("Issue 1", "active", "First issue")
        doc_manager.log_problem("Issue 2", "blocked", "Second issue")
        doc_manager.log_problem("Issue 3", "resolved", "Third issue")
        
        # Verify all problems are present
        with open(doc_manager.problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Issue 1" in content
            assert "Issue 2" in content
            assert "Issue 3" in content
            assert "active" in content
            assert "blocked" in content
            assert "resolved" in content

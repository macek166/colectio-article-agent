"""Unit tests for Streamlit UI components.

This module tests the core functionality of the Streamlit UI without
actually running the Streamlit server.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the functions we want to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import (
    initialize_session_state,
    render_category_results,
)
from src.orchestrator import OrchestratorResult
from src.agents.content_crew import ContentCrewResult


def test_initialize_session_state():
    """Test that session state initialization creates required variables."""
    # Mock streamlit session_state
    mock_session_state = {}
    
    with patch('app.st.session_state', mock_session_state):
        initialize_session_state()
        
        # Verify all required keys are present
        assert 'orchestrator' in mock_session_state
        assert 'execution_result' in mock_session_state
        assert 'is_running' in mock_session_state
        assert 'current_topic' in mock_session_state
        assert 'current_category' in mock_session_state
        assert 'completed_count' in mock_session_state
        assert 'total_count' in mock_session_state
        
        # Verify initial values
        assert mock_session_state['orchestrator'] is None
        assert mock_session_state['execution_result'] is None
        assert mock_session_state['is_running'] is False
        assert mock_session_state['current_topic'] == ""
        assert mock_session_state['current_category'] == ""
        assert mock_session_state['completed_count'] == 0
        assert mock_session_state['total_count'] == 0


def test_render_category_results_no_results():
    """Test rendering category results when no articles exist."""
    # Create mock result with no articles for the category
    result = OrchestratorResult(
        total_topics=0,
        successful=0,
        failed=0,
        topics_generated=[],
        results=[],
        execution_time=0.0
    )
    
    with patch('app.st') as mock_st:
        render_category_results(result, 'pokemon')
        
        # Verify info message is displayed
        mock_st.info.assert_called_once()
        call_args = mock_st.info.call_args[0][0]
        assert 'Pokemon' in call_args or 'pokemon' in call_args.lower()


def test_render_category_results_with_success():
    """Test rendering category results with successful articles."""
    # Create mock successful result
    article_result = ContentCrewResult(
        topic="Best Pokémon Cards 2024",
        article="This is a test article about Pokemon cards...",
        metadata={
            'category': 'pokemon',
            'draft_word_count': 500,
            'research_sources_count': 5,
            'investment_insights_count': 3,
            'seo_keywords_count': 10
        },
        success=True,
        retry_count=0
    )
    
    result = OrchestratorResult(
        total_topics=1,
        successful=1,
        failed=0,
        topics_generated=["Best Pokémon Cards 2024"],
        results=[article_result],
        execution_time=45.5
    )
    
    with patch('app.st') as mock_st:
        # Mock expander context manager
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        
        render_category_results(result, 'pokemon')
        
        # Verify expander was created with topic
        mock_st.expander.assert_called_once()
        call_args = mock_st.expander.call_args[0][0]
        assert "Best Pokémon Cards 2024" in call_args


def test_render_category_results_with_failure():
    """Test rendering category results with failed articles."""
    # Create mock failed result
    article_result = ContentCrewResult(
        topic="Failed Topic",
        article="",
        metadata={
            'category': 'hockey',
            'error': 'API timeout'
        },
        success=False,
        retry_count=3
    )
    
    result = OrchestratorResult(
        total_topics=1,
        successful=0,
        failed=1,
        topics_generated=["Failed Topic"],
        results=[article_result],
        execution_time=120.0
    )
    
    with patch('app.st') as mock_st:
        # Mock expander context manager
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__.return_value = mock_expander
        
        render_category_results(result, 'hockey')
        
        # Verify expander was created
        mock_st.expander.assert_called_once()


def test_documentation_file_not_found():
    """Test rendering documentation when file doesn't exist."""
    from app import render_documentation_file
    
    non_existent_path = Path("non_existent_file.md")
    
    with patch('app.st') as mock_st:
        render_documentation_file(non_existent_path)
        
        # Verify warning is displayed
        mock_st.warning.assert_called_once()


def test_documentation_file_exists():
    """Test rendering documentation when file exists."""
    from app import render_documentation_file
    
    # Create a temporary test file
    test_content = "# Test Documentation\n\nThis is a test."
    test_file = Path("test_doc.md")
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with patch('app.st') as mock_st:
            render_documentation_file(test_file)
            
            # Verify markdown was called with content
            mock_st.markdown.assert_called()
    
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def test_problems_file_with_active_problems():
    """Test rendering problems file with active issues."""
    from app import render_problems_file
    
    # Create a temporary test file with problems
    test_content = """# System Problems

## Test Problem 1
**Timestamp:** 2024-01-01T00:00:00
**Status:** active

Test problem details

---

## Test Problem 2
**Timestamp:** 2024-01-01T00:00:00
**Status:** resolved

Test problem details

---
"""
    test_file = Path("test_problems.md")
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with patch('app.st') as mock_st:
            # Mock columns
            mock_col1 = MagicMock()
            mock_col2 = MagicMock()
            mock_col3 = MagicMock()
            mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]
            
            render_problems_file(test_file)
            
            # Verify metrics were displayed
            mock_st.columns.assert_called()
            mock_st.markdown.assert_called()
    
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

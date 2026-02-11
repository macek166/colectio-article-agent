"""
Property-based tests for Documentation Manager.

Feature: tcg-content-generator, Property 14: Documentation file updates
Feature: tcg-content-generator, Property 15: Problem logging
Validates: Requirements 12.2, 12.4, 12.5
"""

import tempfile
from pathlib import Path

from hypothesis import given, strategies as st

from src.utils.documentation_manager import DocumentationManager


# Hypothesis strategies for generating valid test data
@st.composite
def valid_event_strategy(draw):
    """Generate valid event strings."""
    return draw(st.text(min_size=1, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')  # Exclude surrogates and control chars
    )))


@st.composite
def valid_details_strategy(draw):
    """Generate valid details strings."""
    return draw(st.text(min_size=1, max_size=1000, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')
    )))


@st.composite
def valid_issue_strategy(draw):
    """Generate valid issue strings."""
    return draw(st.text(min_size=1, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')
    )))


@st.composite
def valid_status_strategy(draw):
    """Generate valid status values."""
    return draw(st.sampled_from(['active', 'resolved', 'blocked']))


# Property 14: Documentation file updates
# For any significant event, the system should append a timestamped entry to DOCUMENTATION.md


@given(
    event=valid_event_strategy(),
    details=valid_details_strategy()
)
def test_property_14_documentation_file_updates(
    event: str,
    details: str
) -> None:
    """
    Feature: tcg-content-generator, Property 14: Documentation file updates
    For any significant event, the system should append a timestamped entry
    to DOCUMENTATION.md.
    Validates: Requirements 12.2
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Get initial file size
        doc_file = Path(temp_dir) / "DOCUMENTATION.md"
        initial_size = doc_file.stat().st_size
        
        # Log an event
        doc_manager.log_event(event, details)
        
        # Verify file was updated (size increased)
        final_size = doc_file.stat().st_size
        assert final_size > initial_size, "DOCUMENTATION.md should grow after logging event"
        
        # Verify content contains the event and details
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert event in content, "Event should be in DOCUMENTATION.md"
            assert details in content, "Details should be in DOCUMENTATION.md"
            assert "Timestamp:" in content, "Timestamp should be in DOCUMENTATION.md"


@given(
    events=st.lists(
        st.tuples(valid_event_strategy(), valid_details_strategy()),
        min_size=1,
        max_size=10
    )
)
def test_property_14_multiple_documentation_entries(
    events: list
) -> None:
    """
    Feature: tcg-content-generator, Property 14: Documentation file updates
    For any sequence of events, all events should be appended to DOCUMENTATION.md
    in order.
    Validates: Requirements 12.2
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log all events
        for event, details in events:
            doc_manager.log_event(event, details)
        
        # Verify all events are in the file
        doc_file = Path(temp_dir) / "DOCUMENTATION.md"
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for event, details in events:
                assert event in content, f"Event '{event}' should be in DOCUMENTATION.md"
                assert details in content, f"Details '{details}' should be in DOCUMENTATION.md"


# Property 15: Problem logging
# For any error or issue encountered, the system should log it to PROBLEMS.md
# with status information


@given(
    issue=valid_issue_strategy(),
    status=valid_status_strategy(),
    details=valid_details_strategy()
)
def test_property_15_problem_logging(
    issue: str,
    status: str,
    details: str
) -> None:
    """
    Feature: tcg-content-generator, Property 15: Problem logging
    For any error or issue encountered, the system should log it to PROBLEMS.md
    with status information.
    Validates: Requirements 12.4, 12.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Get initial file size
        problems_file = Path(temp_dir) / "PROBLEMS.md"
        initial_size = problems_file.stat().st_size
        
        # Log a problem
        doc_manager.log_problem(issue, status, details)
        
        # Verify file was updated (size increased)
        final_size = problems_file.stat().st_size
        assert final_size > initial_size, "PROBLEMS.md should grow after logging problem"
        
        # Verify content contains the issue, status, and details
        with open(problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert issue in content, "Issue should be in PROBLEMS.md"
            assert status in content, "Status should be in PROBLEMS.md"
            assert details in content, "Details should be in PROBLEMS.md"
            assert "Timestamp:" in content, "Timestamp should be in PROBLEMS.md"


@given(
    problems=st.lists(
        st.tuples(valid_issue_strategy(), valid_status_strategy(), valid_details_strategy()),
        min_size=1,
        max_size=10
    )
)
def test_property_15_multiple_problem_entries(
    problems: list
) -> None:
    """
    Feature: tcg-content-generator, Property 15: Problem logging
    For any sequence of problems, all problems should be appended to PROBLEMS.md
    with their status.
    Validates: Requirements 12.4, 12.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log all problems
        for issue, status, details in problems:
            doc_manager.log_problem(issue, status, details)
        
        # Verify all problems are in the file
        problems_file = Path(temp_dir) / "PROBLEMS.md"
        with open(problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for issue, status, details in problems:
                assert issue in content, f"Issue '{issue}' should be in PROBLEMS.md"
                assert status in content, f"Status '{status}' should be in PROBLEMS.md"
                assert details in content, f"Details '{details}' should be in PROBLEMS.md"


@given(
    issue=valid_issue_strategy(),
    initial_status=valid_status_strategy(),
    new_status=valid_status_strategy(),
    details=valid_details_strategy()
)
def test_property_15_problem_status_update(
    issue: str,
    initial_status: str,
    new_status: str,
    details: str
) -> None:
    """
    Feature: tcg-content-generator, Property 15: Problem logging
    For any problem with a status, updating the status should change it in
    PROBLEMS.md.
    Validates: Requirements 12.4, 12.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_manager = DocumentationManager(docs_dir=temp_dir)
        
        # Log a problem with initial status
        doc_manager.log_problem(issue, initial_status, details)
        
        # Update the status
        doc_manager.update_problem_status(issue, new_status)
        
        # Verify the new status is in the file
        problems_file = Path(temp_dir) / "PROBLEMS.md"
        with open(problems_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # The new status should be present
            assert f"**Status:** {new_status}" in content, \
                f"New status '{new_status}' should be in PROBLEMS.md"

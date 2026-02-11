"""
Property-based tests for Context7 MCP integration.

Feature: tcg-content-generator
Tests Context7 MCP client properties.
"""

import sys
from typing import Optional
from unittest.mock import MagicMock, patch

from hypothesis import given, settings, strategies as st

from src.models.config import Config
from src.tools.context7_client import Context7Client


# Hypothesis strategies for generating valid test data
@st.composite
def valid_library_name_strategy(draw):
    """Generate valid library names."""
    # Common library names for testing
    common_libs = ['crewai', 'streamlit', 'pydantic', 'pytest', 'hypothesis']
    return draw(st.sampled_from(common_libs))


@st.composite
def valid_library_id_strategy(draw):
    """Generate valid Context7-compatible library IDs."""
    org = draw(st.text(min_size=3, max_size=20, alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd'),
        blacklist_characters='-_'
    )))
    project = draw(st.text(min_size=3, max_size=30, alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd'),
        blacklist_characters='-_'
    )))
    return f"/{org}/{project}"


@st.composite
def valid_topic_strategy(draw):
    """Generate valid documentation topics."""
    topics = [
        'getting-started',
        'api-reference',
        'configuration',
        'examples',
        'best-practices',
        None  # General documentation
    ]
    return draw(st.sampled_from(topics))


@st.composite
def valid_mode_strategy(draw):
    """Generate valid documentation modes."""
    return draw(st.sampled_from(['code', 'info']))


# Property 8: Context7 MCP integration
# For any agent request for library documentation, the system should use
# Context7 MCP to retrieve the information


@given(library_name=valid_library_name_strategy())
@settings(max_examples=100)
def test_property_8_context7_mcp_integration_resolve_library(
    library_name: str
) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    For any agent request for library documentation, the system should use
    Context7 MCP to retrieve the information - testing library resolution.
    Validates: Requirements 3.2
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Create a mock kiro_mcp module
    mock_kiro_mcp = MagicMock()
    expected_id = f"/org/{library_name}"
    mock_kiro_mcp.mcp_Context7_resolve_library_id.return_value = {'library_id': expected_id}
    
    # Mock the module import
    with patch.dict('sys.modules', {'kiro_mcp': mock_kiro_mcp}):
        # Resolve library
        result = client.resolve_library(library_name)

        # Property: Context7 MCP should be called for library resolution
        assert mock_kiro_mcp.mcp_Context7_resolve_library_id.called, \
            "Context7 MCP resolve_library_id should be called"

        # Property: The library name should be passed to MCP
        call_args = mock_kiro_mcp.mcp_Context7_resolve_library_id.call_args
        assert call_args[1]['libraryName'] == library_name, \
            f"Library name '{library_name}' should be passed to MCP"

        # Property: A valid library ID should be returned
        assert result is not None, \
            "Should return a library ID when MCP succeeds"
        assert result == expected_id, \
            f"Should return the library ID from MCP: {expected_id}"


@given(
    library_id=valid_library_id_strategy(),
    topic=valid_topic_strategy(),
    mode=valid_mode_strategy()
)
@settings(max_examples=100)
def test_property_8_context7_mcp_integration_get_docs(
    library_id: str,
    topic: Optional[str],
    mode: str
) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    For any agent request for library documentation, the system should use
    Context7 MCP to retrieve the information - testing documentation retrieval.
    Validates: Requirements 3.2
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Create a mock kiro_mcp module
    mock_kiro_mcp = MagicMock()
    expected_docs = f"Documentation for {library_id}"
    mock_kiro_mcp.mcp_Context7_get_library_docs.return_value = {'content': expected_docs}
    
    # Mock the module import
    with patch.dict('sys.modules', {'kiro_mcp': mock_kiro_mcp}):
        # Get documentation
        result = client.get_docs(library_id, topic=topic, mode=mode)

        # Property: Context7 MCP should be called for documentation retrieval
        assert mock_kiro_mcp.mcp_Context7_get_library_docs.called, \
            "Context7 MCP get_library_docs should be called"

        # Property: The library ID should be passed to MCP
        call_args = mock_kiro_mcp.mcp_Context7_get_library_docs.call_args
        assert call_args[1]['context7CompatibleLibraryID'] == library_id, \
            f"Library ID '{library_id}' should be passed to MCP"

        # Property: The mode should be passed to MCP
        assert call_args[1]['mode'] == mode, \
            f"Mode '{mode}' should be passed to MCP"

        # Property: The topic should be passed to MCP if provided
        if topic:
            assert call_args[1]['topic'] == topic, \
                f"Topic '{topic}' should be passed to MCP"

        # Property: Documentation content should be returned
        assert result == expected_docs, \
            "Should return the documentation content from MCP"


@given(library_name=valid_library_name_strategy())
@settings(max_examples=50)
def test_property_8_context7_graceful_failure_on_mcp_unavailable(
    library_name: str
) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    When Context7 MCP is unavailable, the system should continue without docs.
    Validates: Requirements 3.2
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Attempt to resolve library without mocking (MCP not available)
    result = client.resolve_library(library_name)

    # Property: Should return None when MCP is unavailable
    assert result is None, \
        "Should return None when Context7 MCP is unavailable"

    # Property: Should not raise an exception
    # (test passes if we reach here without exception)


@given(
    library_id=valid_library_id_strategy(),
    mode=valid_mode_strategy()
)
@settings(max_examples=50)
def test_property_8_context7_graceful_failure_on_mcp_error(
    library_id: str,
    mode: str
) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    When Context7 MCP encounters an error, the system should continue without docs.
    Validates: Requirements 3.2
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Create a mock kiro_mcp module that raises an error
    mock_kiro_mcp = MagicMock()
    mock_kiro_mcp.mcp_Context7_get_library_docs.side_effect = Exception("MCP connection failed")
    
    # Mock the module import
    with patch.dict('sys.modules', {'kiro_mcp': mock_kiro_mcp}):
        # Attempt to get documentation
        result = client.get_docs(library_id, mode=mode)

        # Property: Should return empty string when MCP fails
        assert result == "", \
            "Should return empty string when Context7 MCP fails"

        # Property: Should not raise an exception
        # (test passes if we reach here without exception)


@given(
    library_name=valid_library_name_strategy(),
    library_id=valid_library_id_strategy()
)
@settings(max_examples=50)
def test_property_8_context7_caching_behavior(
    library_name: str,
    library_id: str
) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    Context7 client should cache frequently accessed documentation.
    Validates: Requirements 3.2
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Create a mock kiro_mcp module
    mock_kiro_mcp = MagicMock()
    mock_kiro_mcp.mcp_Context7_resolve_library_id.return_value = {'library_id': library_id}
    
    # Mock the module import
    with patch.dict('sys.modules', {'kiro_mcp': mock_kiro_mcp}):
        # First call - should hit MCP
        result1 = client.resolve_library(library_name)
        first_call_count = mock_kiro_mcp.mcp_Context7_resolve_library_id.call_count

        # Second call - should use cache
        result2 = client.resolve_library(library_name)
        second_call_count = mock_kiro_mcp.mcp_Context7_resolve_library_id.call_count

        # Property: First call should invoke MCP
        assert first_call_count == 1, \
            "First call should invoke Context7 MCP"

        # Property: Second call should NOT invoke MCP again (cached)
        assert second_call_count == 1, \
            "Second call should use cache, not invoke MCP again"

        # Property: Both calls should return the same result
        assert result1 == result2, \
            "Cached result should match original result"

        # Property: Cache should contain the entry
        cache_stats = client.get_cache_stats()
        assert cache_stats['entries'] > 0, \
            "Cache should contain entries after successful calls"


@given(
    library_id=valid_library_id_strategy(),
    topic=valid_topic_strategy(),
    mode=valid_mode_strategy()
)
@settings(max_examples=50)
def test_property_8_context7_documentation_caching(
    library_id: str,
    topic: Optional[str],
    mode: str
) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    Context7 client should cache documentation content.
    Validates: Requirements 3.2
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Create a mock kiro_mcp module
    mock_kiro_mcp = MagicMock()
    expected_docs = f"Documentation for {library_id}"
    mock_kiro_mcp.mcp_Context7_get_library_docs.return_value = {'content': expected_docs}
    
    # Mock the module import
    with patch.dict('sys.modules', {'kiro_mcp': mock_kiro_mcp}):
        # First call - should hit MCP
        result1 = client.get_docs(library_id, topic=topic, mode=mode)
        first_call_count = mock_kiro_mcp.mcp_Context7_get_library_docs.call_count

        # Second call with same parameters - should use cache
        result2 = client.get_docs(library_id, topic=topic, mode=mode)
        second_call_count = mock_kiro_mcp.mcp_Context7_get_library_docs.call_count

        # Property: First call should invoke MCP
        assert first_call_count == 1, \
            "First call should invoke Context7 MCP"

        # Property: Second call should NOT invoke MCP again (cached)
        assert second_call_count == 1, \
            "Second call should use cache, not invoke MCP again"

        # Property: Both calls should return the same documentation
        assert result1 == result2, \
            "Cached documentation should match original"


@given(mode=st.text(min_size=1, max_size=20))
@settings(max_examples=50)
def test_property_8_context7_invalid_mode_handling(mode: str) -> None:
    """
    Feature: tcg-content-generator, Property 8: Context7 MCP integration
    Context7 client should handle invalid modes gracefully.
    Validates: Requirements 3.2
    """
    # Skip if mode is valid
    if mode in ('code', 'info'):
        return

    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )

    # Create Context7Client
    client = Context7Client(config)

    # Create a mock kiro_mcp module
    mock_kiro_mcp = MagicMock()
    mock_kiro_mcp.mcp_Context7_get_library_docs.return_value = {'content': "Documentation"}
    
    # Mock the module import
    with patch.dict('sys.modules', {'kiro_mcp': mock_kiro_mcp}):
        # Call with invalid mode
        _ = client.get_docs("/org/project", mode=mode)

        # Property: Should default to 'code' mode for invalid modes
        if mock_kiro_mcp.mcp_Context7_get_library_docs.called:
            call_args = mock_kiro_mcp.mcp_Context7_get_library_docs.call_args
            actual_mode = call_args[1]['mode']
            assert actual_mode == 'code', \
                f"Invalid mode '{mode}' should default to 'code'"

        # Property: Should not raise an exception
        # (test passes if we reach here without exception)

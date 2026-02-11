"""Property-based tests for Orchestrator sequential processing.

This module contains property-based tests that verify the Orchestrator's
sequential topic processing behavior using Hypothesis.
"""

from typing import List
from unittest.mock import Mock, MagicMock, patch

import pytest
from hypothesis import given, strategies as st, settings

from src.orchestrator import Orchestrator
from src.agents.content_crew import ContentCrewResult
from src.config.settings import Config


# Strategy for generating valid topic lists
@st.composite
def topic_list_strategy(draw):
    """Generate valid topic lists with 1-20 topics.
    
    Args:
        draw: Hypothesis draw function
        
    Returns:
        List of topic strings
    """
    # Generate 1-20 topics
    num_topics = draw(st.integers(min_value=1, max_value=20))
    
    # Generate unique topic titles
    topics = []
    for i in range(num_topics):
        # Generate topic with reasonable length (10-200 chars)
        topic = draw(st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' '
            ),
            min_size=10,
            max_size=200
        ))
        # Ensure uniqueness
        if topic not in topics:
            topics.append(topic)
    
    return topics


@given(topics=topic_list_strategy())
@settings(max_examples=100, deadline=None)
def test_property_5_sequential_processing(topics: List[str]):
    """
    Feature: tcg-content-generator, Property 5: Sequential topic processing
    
    For any topic list, the Execution Phase should process topics one at a time
    in the exact order they appear in the list.
    
    This test verifies that:
    1. Topics are processed in the order they appear in the input list
    2. Each topic is processed completely before the next one starts
    3. The order is preserved in the results
    
    Validates: Requirements 2.1, 2.3
    """
    # Skip if no topics
    if not topics:
        return
    
    # Track the order of topic processing
    processed_order = []
    
    # Create mock components
    mock_config = Mock(spec=Config)
    mock_config.max_retries = 3
    mock_config.default_topic_distribution = {
        'pokemon': 5,
        'hockey': 3,
        'soccer': 2
    }
    
    mock_neon_client = Mock()
    mock_context7_client = Mock()
    mock_seo_tools = Mock()
    mock_doc_manager = Mock()
    
    # Create orchestrator
    orchestrator = Orchestrator(
        config=mock_config,
        neon_client=mock_neon_client,
        context7_client=mock_context7_client,
        seo_tools=mock_seo_tools,
        doc_manager=mock_doc_manager
    )
    
    # Mock the strategy phase to return our test topics
    with patch.object(
        orchestrator,
        '_execute_strategy_phase',
        return_value=topics
    ):
        # Mock ContentCrew to track processing order
        def mock_content_crew_init(
            topic, category, context_manager, neon_client,
            context7_client, seo_tools, config, doc_manager
        ):
            """Mock ContentCrew initialization."""
            mock_crew = MagicMock()
            
            # Track when this topic is processed
            def mock_execute(max_retries=3):
                """Mock execute that records processing order."""
                processed_order.append(topic)
                return ContentCrewResult(
                    topic=topic,
                    article=f"Article for {topic}",
                    metadata={'category': category},
                    success=True,
                    retry_count=0
                )
            
            mock_crew.execute = mock_execute
            return mock_crew
        
        # Patch ContentCrew class
        with patch(
            'src.orchestrator.ContentCrew',
            side_effect=mock_content_crew_init
        ):
            # Execute the orchestrator
            result = orchestrator.run(topic_distribution=None)
            
            # PROPERTY VERIFICATION:
            # The processed order must match the input order exactly
            assert processed_order == topics, (
                f"Topics were not processed in sequential order. "
                f"Expected: {topics}, Got: {processed_order}"
            )
            
            # Additional verification: results should also be in order
            result_topics = [r.topic for r in result.results]
            assert result_topics == topics, (
                f"Results are not in the same order as input topics. "
                f"Expected: {topics}, Got: {result_topics}"
            )
            
            # Verify all topics were processed
            assert len(processed_order) == len(topics), (
                f"Not all topics were processed. "
                f"Expected {len(topics)}, got {len(processed_order)}"
            )


@given(topics=topic_list_strategy())
@settings(max_examples=50, deadline=None)
def test_sequential_processing_with_failures(topics: List[str]):
    """
    Test that sequential processing continues even when some topics fail.
    
    This verifies that:
    1. Failed topics don't stop the processing of subsequent topics
    2. Order is maintained even with failures
    3. All topics are attempted regardless of failures
    """
    # Skip if no topics
    if not topics:
        return
    
    # Track processing order
    processed_order = []
    
    # Create mock components
    mock_config = Mock(spec=Config)
    mock_config.max_retries = 3
    mock_config.default_topic_distribution = {
        'pokemon': 5,
        'hockey': 3,
        'soccer': 2
    }
    
    mock_neon_client = Mock()
    mock_context7_client = Mock()
    mock_seo_tools = Mock()
    mock_doc_manager = Mock()
    
    # Create orchestrator
    orchestrator = Orchestrator(
        config=mock_config,
        neon_client=mock_neon_client,
        context7_client=mock_context7_client,
        seo_tools=mock_seo_tools,
        doc_manager=mock_doc_manager
    )
    
    # Mock the strategy phase
    with patch.object(
        orchestrator,
        '_execute_strategy_phase',
        return_value=topics
    ):
        # Mock ContentCrew with some failures
        def mock_content_crew_init(
            topic, category, context_manager, neon_client,
            context7_client, seo_tools, config, doc_manager
        ):
            """Mock ContentCrew with failures for even-indexed topics."""
            mock_crew = MagicMock()
            
            def mock_execute(max_retries=3):
                """Mock execute with failures."""
                processed_order.append(topic)
                
                # Fail every other topic (based on position in list)
                topic_index = topics.index(topic)
                success = (topic_index % 2 == 0)
                
                return ContentCrewResult(
                    topic=topic,
                    article=f"Article for {topic}" if success else "",
                    metadata={'category': category},
                    success=success,
                    retry_count=0 if success else max_retries
                )
            
            mock_crew.execute = mock_execute
            return mock_crew
        
        with patch(
            'src.orchestrator.ContentCrew',
            side_effect=mock_content_crew_init
        ):
            # Execute
            result = orchestrator.run(topic_distribution=None)
            
            # PROPERTY: Order is maintained even with failures
            assert processed_order == topics, (
                f"Processing order not maintained with failures. "
                f"Expected: {topics}, Got: {processed_order}"
            )
            
            # Verify all topics were attempted
            assert len(processed_order) == len(topics), (
                f"Not all topics were attempted. "
                f"Expected {len(topics)}, got {len(processed_order)}"
            )


def test_sequential_processing_single_topic():
    """
    Test sequential processing with a single topic.
    
    This is an edge case test to ensure the system handles
    single-topic lists correctly.
    """
    topics = ["Single Test Topic About Pokemon Cards"]
    processed_order = []
    
    # Create mock components
    mock_config = Mock(spec=Config)
    mock_config.max_retries = 3
    mock_config.default_topic_distribution = {
        'pokemon': 5,
        'hockey': 3,
        'soccer': 2
    }
    
    mock_neon_client = Mock()
    mock_context7_client = Mock()
    mock_seo_tools = Mock()
    mock_doc_manager = Mock()
    
    # Create orchestrator
    orchestrator = Orchestrator(
        config=mock_config,
        neon_client=mock_neon_client,
        context7_client=mock_context7_client,
        seo_tools=mock_seo_tools,
        doc_manager=mock_doc_manager
    )
    
    # Mock the strategy phase
    with patch.object(
        orchestrator,
        '_execute_strategy_phase',
        return_value=topics
    ):
        # Mock ContentCrew
        def mock_content_crew_init(
            topic, category, context_manager, neon_client,
            context7_client, seo_tools, config, doc_manager
        ):
            """Mock ContentCrew."""
            mock_crew = MagicMock()
            
            def mock_execute(max_retries=3):
                """Mock execute."""
                processed_order.append(topic)
                return ContentCrewResult(
                    topic=topic,
                    article=f"Article for {topic}",
                    metadata={'category': category},
                    success=True,
                    retry_count=0
                )
            
            mock_crew.execute = mock_execute
            return mock_crew
        
        with patch(
            'src.orchestrator.ContentCrew',
            side_effect=mock_content_crew_init
        ):
            # Execute
            result = orchestrator.run(topic_distribution=None)
            
            # Verify single topic was processed
            assert processed_order == topics
            assert len(result.results) == 1
            assert result.results[0].topic == topics[0]


def test_sequential_processing_empty_list():
    """
    Test sequential processing with an empty topic list.
    
    This edge case ensures the system handles empty lists gracefully.
    """
    topics = []
    
    # Create mock components
    mock_config = Mock(spec=Config)
    mock_config.max_retries = 3
    mock_config.default_topic_distribution = {
        'pokemon': 5,
        'hockey': 3,
        'soccer': 2
    }
    
    mock_neon_client = Mock()
    mock_context7_client = Mock()
    mock_seo_tools = Mock()
    mock_doc_manager = Mock()
    
    # Create orchestrator
    orchestrator = Orchestrator(
        config=mock_config,
        neon_client=mock_neon_client,
        context7_client=mock_context7_client,
        seo_tools=mock_seo_tools,
        doc_manager=mock_doc_manager
    )
    
    # Mock the strategy phase
    with patch.object(
        orchestrator,
        '_execute_strategy_phase',
        return_value=topics
    ):
        # Mock ContentCrew (should not be called)
        with patch('src.orchestrator.ContentCrew') as mock_crew_class:
            # Execute
            result = orchestrator.run(topic_distribution=None)
            
            # Verify no topics were processed
            assert len(result.results) == 0
            assert result.total_topics == 0
            assert result.successful == 0
            assert result.failed == 0
            
            # ContentCrew should not have been instantiated
            mock_crew_class.assert_not_called()


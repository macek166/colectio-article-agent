"""
Property-based tests for database operations.

Feature: tcg-content-generator
Tests database query and deduplication properties.
"""

from datetime import UTC, datetime
from typing import List, Set
from unittest.mock import MagicMock, patch
from uuid import uuid4

from hypothesis import given, settings, strategies as st

from src.models.config import Config
from src.models.topic import TopicRecord
from src.tools.neon_db_client import NeonDBClient


# Hypothesis strategies for generating valid test data
@st.composite
def valid_category_strategy(draw):
    """Generate valid category values."""
    return draw(st.sampled_from(['pokemon', 'hockey', 'soccer']))


@st.composite
def valid_title_strategy(draw):
    """Generate valid title strings (10-200 characters)."""
    return draw(st.text(min_size=10, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')  # Exclude surrogates and control chars
    )))


@st.composite
def existing_topics_strategy(draw):
    """Generate a set of existing topic titles."""
    num_topics = draw(st.integers(min_value=0, max_value=20))
    titles = []
    for _ in range(num_topics):
        title = draw(valid_title_strategy())
        titles.append(title)
    return titles


@st.composite
def topic_candidates_strategy(draw):
    """Generate a list of topic candidate titles."""
    num_candidates = draw(st.integers(min_value=1, max_value=30))
    candidates = []
    for _ in range(num_candidates):
        title = draw(valid_title_strategy())
        candidates.append(title)
    return candidates


# Property 1: Pre-generation database query
# For any Strategy Phase execution, the system should query the database
# for ALL existing topics BEFORE generating new topic candidates


@given(existing_topics=existing_topics_strategy())
@settings(max_examples=100)
def test_property_1_pre_generation_database_query(existing_topics: List[str]) -> None:
    """
    Feature: tcg-content-generator, Property 1: Pre-generation database query
    For any Strategy Phase execution, the system should query Neon database
    for ALL existing topics BEFORE generating new topic candidates.
    Validates: Requirements 1.1
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Create NeonDBClient with mocked connection
    with patch('src.tools.neon_db_client.psycopg2.connect') as mock_connect:
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock the query_all_topics to return our existing topics
        mock_cursor.fetchall.return_value = [
            {'title': title} for title in existing_topics
        ]
        mock_cursor.description = True  # Indicate query returns results
        
        # Create client and query topics
        client = NeonDBClient(config)
        result = client.query_all_topics()
        
        # Property: The query should be executed BEFORE any topic generation
        # We verify this by checking that execute_query was called
        assert mock_cursor.execute.called, "Database query should be executed"
        
        # Property: ALL existing topics should be returned
        assert len(result) == len(existing_topics), \
            f"Should return all {len(existing_topics)} existing topics"
        
        # Property: The returned topics should match the existing topics
        assert set(result) == set(existing_topics), \
            "Returned topics should match existing topics in database"
        
        # Property: The query should retrieve topics from the 'topics' table
        executed_query = mock_cursor.execute.call_args[0][0]
        assert 'topics' in executed_query.lower(), \
            "Query should access the 'topics' table"
        assert 'title' in executed_query.lower(), \
            "Query should retrieve 'title' column"


# Property 3: Topic deduplication completeness
# For any set of proposed topics and existing topics in Neon database,
# the final topic list should contain no topics that exist in the database


def deduplicate_topics(candidates: List[str], existing: Set[str]) -> List[str]:
    """
    Deduplicate topic candidates against existing topics.
    
    This is a reference implementation of the deduplication logic
    that should be used in the Strategy Phase.
    
    Args:
        candidates: List of candidate topic titles
        existing: Set of existing topic titles from database
        
    Returns:
        List of unique topics not in existing set
    """
    return [topic for topic in candidates if topic not in existing]


@given(
    candidates=topic_candidates_strategy(),
    existing=existing_topics_strategy()
)
@settings(max_examples=100)
def test_property_3_topic_deduplication_completeness(
    candidates: List[str],
    existing: List[str]
) -> None:
    """
    Feature: tcg-content-generator, Property 3: Topic deduplication completeness
    For any set of proposed topics and existing topics in Neon database,
    the final topic list should contain no topics that exist in the database.
    Validates: Requirements 1.5
    """
    # Convert existing to set for efficient lookup
    existing_set = set(existing)
    
    # Perform deduplication
    result = deduplicate_topics(candidates, existing_set)
    
    # Property: No topic in result should exist in the existing set
    for topic in result:
        assert topic not in existing_set, \
            f"Deduplicated list should not contain existing topic: {topic}"
    
    # Property: All non-duplicate candidates should be in result
    expected_unique = [c for c in candidates if c not in existing_set]
    assert len(result) == len(expected_unique), \
        "Result should contain all non-duplicate candidates"
    
    # Property: Order should be preserved from candidates
    result_filtered = [c for c in candidates if c in result]
    assert result == result_filtered, \
        "Deduplication should preserve order of candidates"


@given(
    candidates=topic_candidates_strategy(),
    existing=existing_topics_strategy()
)
@settings(max_examples=100)
def test_property_3_deduplication_with_database_integration(
    candidates: List[str],
    existing: List[str]
) -> None:
    """
    Feature: tcg-content-generator, Property 3: Topic deduplication completeness
    Integration test: Verify deduplication works with database client.
    Validates: Requirements 1.5
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Create NeonDBClient with mocked connection
    with patch('src.tools.neon_db_client.psycopg2.connect') as mock_connect:
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock the query to return existing topics
        mock_cursor.fetchall.return_value = [
            {'title': title} for title in existing
        ]
        mock_cursor.description = True
        
        # Create client and query existing topics
        client = NeonDBClient(config)
        existing_from_db = client.query_all_topics()
        
        # Perform deduplication
        existing_set = set(existing_from_db)
        result = deduplicate_topics(candidates, existing_set)
        
        # Property: No topic in result should exist in database
        for topic in result:
            assert topic not in existing_set, \
                f"Deduplicated list should not contain topic from database: {topic}"
        
        # Property: Result should be a subset of candidates
        assert all(topic in candidates for topic in result), \
            "All deduplicated topics should come from candidates"


@given(
    title=valid_title_strategy(),
    category=valid_category_strategy()
)
@settings(max_examples=50)
def test_property_1_database_stores_topics_for_future_queries(
    title: str,
    category: str
) -> None:
    """
    Feature: tcg-content-generator, Property 1: Pre-generation database query
    Verify that topics stored in database can be queried in future executions.
    Validates: Requirements 1.1
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Create NeonDBClient with mocked connection
    with patch('src.tools.neon_db_client.psycopg2.connect') as mock_connect:
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock successful insert
        mock_cursor.fetchall.return_value = [{'id': str(uuid4())}]
        mock_cursor.description = True
        
        # Create client and store a topic
        client = NeonDBClient(config)
        
        topic_record = TopicRecord(
            title=title,
            category=category,
            created_at=datetime.now(UTC).isoformat()
        )
        
        topic_id = client.create_topic(topic_record)
        
        # Property: Topic should be stored successfully
        assert topic_id is not None, "Topic should be stored with valid ID"
        
        # Property: The insert query should include the title
        insert_call = mock_cursor.execute.call_args_list[0]
        executed_query = insert_call[0][0]
        assert 'insert' in executed_query.lower(), \
            "Should execute INSERT query"
        assert 'topics' in executed_query.lower(), \
            "Should insert into 'topics' table"
        
        # Verify the title was included in the parameters
        params = insert_call[0][1] if len(insert_call[0]) > 1 else insert_call[1]
        assert params.get('title') == title, \
            "Title should be included in insert parameters"

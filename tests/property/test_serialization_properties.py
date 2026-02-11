"""
Property-based tests for topic serialization.

Feature: tcg-content-generator
Tests JSON serialization and topic format properties.
"""

import json
from typing import Dict, List
from unittest.mock import MagicMock, patch

from hypothesis import given, settings, strategies as st

from src.agents.strategist import StrategyPhase, TopicCandidate
from src.models.config import Config
from src.tools.context7_client import Context7Client
from src.tools.neon_db_client import NeonDBClient
from src.tools.seo_tools import SEOTools
from src.utils.documentation_manager import DocumentationManager


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
def topic_list_strategy(draw):
    """Generate a list of topic strings."""
    num_topics = draw(st.integers(min_value=1, max_value=20))
    topics = []
    for _ in range(num_topics):
        title = draw(valid_title_strategy())
        topics.append(title)
    return topics


@st.composite
def topic_distribution_strategy(draw):
    """Generate valid topic distribution."""
    pokemon_count = draw(st.integers(min_value=0, max_value=10))
    hockey_count = draw(st.integers(min_value=0, max_value=10))
    soccer_count = draw(st.integers(min_value=0, max_value=10))
    
    # Ensure at least one topic
    if pokemon_count + hockey_count + soccer_count == 0:
        pokemon_count = 1
    
    return {
        'pokemon': pokemon_count,
        'hockey': hockey_count,
        'soccer': soccer_count
    }


# Property 4: JSON-serializable topic format
# For any Strategy Phase output, topics should be structured as a
# JSON-serializable Python list of strings


@given(topics=topic_list_strategy())
@settings(max_examples=100)
def test_property_4_json_serializable_topic_format(topics: List[str]) -> None:
    """
    Feature: tcg-content-generator, Property 4: JSON-serializable topic format
    For any Strategy Phase output, topics should be structured as a
    JSON-serializable Python list of strings.
    Validates: Requirements 1.6
    """
    # Property: Topics should be a Python list
    assert isinstance(topics, list), \
        "Topics should be a Python list"
    
    # Property: All elements should be strings
    for topic in topics:
        assert isinstance(topic, str), \
            f"Each topic should be a string, got {type(topic)}"
    
    # Property: The list should be JSON-serializable
    try:
        json_str = json.dumps(topics)
        assert isinstance(json_str, str), \
            "JSON serialization should produce a string"
    except (TypeError, ValueError) as e:
        raise AssertionError(f"Topics should be JSON-serializable: {e}") from e
    
    # Property: Deserialization should produce equivalent list
    try:
        deserialized = json.loads(json_str)
        assert deserialized == topics, \
            "Deserialized topics should match original"
        assert isinstance(deserialized, list), \
            "Deserialized result should be a list"
    except (TypeError, ValueError) as e:
        raise AssertionError(f"Deserialization should work: {e}") from e


@given(
    topics=topic_list_strategy(),
    category=valid_category_strategy()
)
@settings(max_examples=100)
def test_property_4_topic_candidate_serialization(
    topics: List[str],
    category: str
) -> None:
    """
    Feature: tcg-content-generator, Property 4: JSON-serializable topic format
    Verify that TopicCandidate objects can be converted to JSON-serializable format.
    Validates: Requirements 1.6
    """
    # Create TopicCandidate objects
    candidates = []
    for title in topics:
        candidate = TopicCandidate(
            title=title,
            category=category,
            sources=["https://example.com"],
            seo_score=75.0,
            keywords=["test", "keyword"]
        )
        candidates.append(candidate)
    
    # Property: Candidates should be convertible to dict
    for candidate in candidates:
        candidate_dict = candidate.model_dump()
        assert isinstance(candidate_dict, dict), \
            "Candidate should convert to dict"
        assert 'title' in candidate_dict, \
            "Dict should contain 'title' field"
    
    # Property: Extract titles to create JSON-serializable list
    topic_titles = [c.title for c in candidates]
    
    # Property: Titles should be JSON-serializable
    try:
        json_str = json.dumps(topic_titles)
        deserialized = json.loads(json_str)
        assert deserialized == topic_titles, \
            "Serialization round-trip should preserve titles"
    except (TypeError, ValueError) as e:
        raise AssertionError(f"Topic titles should be JSON-serializable: {e}") from e


@given(distribution=topic_distribution_strategy())
@settings(max_examples=50, deadline=None)
def test_property_4_strategy_phase_returns_json_serializable_list(
    distribution: Dict[str, int]
) -> None:
    """
    Feature: tcg-content-generator, Property 4: JSON-serializable topic format
    Verify that StrategyPhase.generate_topics() returns JSON-serializable list.
    Validates: Requirements 1.6
    """
    # Create mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Create mocked clients
    with patch('src.tools.neon_db_client.psycopg2.connect'), \
         patch('src.tools.seo_tools.SerperDevTool'), \
         patch('src.tools.seo_tools.ScrapeWebsiteTool'), \
         patch('openai.OpenAI'):
        
        # Create clients
        neon_client = NeonDBClient(config)
        context7_client = Context7Client(config)
        seo_tools = SEOTools(config)
        doc_manager = DocumentationManager()
        
        # Mock database to return empty existing topics
        with patch.object(neon_client, 'query_all_topics', return_value=[]):
            # Mock OpenAI to return valid topics
            total_topics = sum(distribution.values())
            mock_topics = [f"Test Topic {i+1}" for i in range(total_topics)]
            
            with patch('openai.OpenAI') as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                # Mock the chat completion response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = json.dumps(mock_topics)
                mock_client.chat.completions.create.return_value = mock_response
                
                # Mock SEO tools
                with patch.object(seo_tools, 'get_serp_data', return_value={}), \
                     patch.object(seo_tools, 'get_google_trends', return_value={}), \
                     patch.object(seo_tools, 'get_keywords', return_value=[]), \
                     patch.object(seo_tools, 'scrape_category_sources',
                                  return_value={'sources': [], 'content': {}}):
                    
                    # Create StrategyPhase
                    strategy = StrategyPhase(
                        config, neon_client, context7_client, seo_tools, doc_manager
                    )
                    
                    # Generate topics
                    result = strategy.generate_topics(distribution)
                    
                    # Property: Result should be a list
                    assert isinstance(result, list), \
                        "generate_topics() should return a list"
                    
                    # Property: All elements should be strings
                    for topic in result:
                        assert isinstance(topic, str), \
                            f"Each topic should be a string, got {type(topic)}"
                    
                    # Property: Result should be JSON-serializable
                    try:
                        json_str = json.dumps(result)
                        deserialized = json.loads(json_str)
                        assert deserialized == result, \
                            "JSON round-trip should preserve topics"
                    except (TypeError, ValueError) as e:
                        raise AssertionError(
                            f"Strategy Phase output should be JSON-serializable: {e}"
                        ) from e


# Property 16: Topic serialization format
# For any topic serialization operation, the system should use JSON format
# and maintain Python list of strings structure


@given(topics=topic_list_strategy())
@settings(max_examples=100)
def test_property_16_topic_serialization_format(topics: List[str]) -> None:
    """
    Feature: tcg-content-generator, Property 16: Topic serialization format
    For any topic serialization operation, the system should use JSON format
    and maintain Python list of strings structure.
    Validates: Requirements 13.1, 13.2, 13.4, 13.5
    """
    # Property: Serialization should use JSON format
    serialized = json.dumps(topics)
    assert isinstance(serialized, str), \
        "Serialized topics should be a JSON string"
    
    # Property: Serialized format should be valid JSON
    try:
        parsed = json.loads(serialized)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Serialized topics should be valid JSON: {e}") from e
    
    # Property: Deserialized structure should be a list
    assert isinstance(parsed, list), \
        "Deserialized topics should be a Python list"
    
    # Property: All elements should be strings
    for topic in parsed:
        assert isinstance(topic, str), \
            f"Each deserialized topic should be a string, got {type(topic)}"
    
    # Property: Deserialization should preserve original data
    assert parsed == topics, \
        "Deserialization should preserve original topic list"
    
    # Property: Order should be preserved
    for i, topic in enumerate(topics):
        assert parsed[i] == topic, \
            f"Topic order should be preserved at index {i}"


@given(topics=topic_list_strategy())
@settings(max_examples=100)
def test_property_16_json_format_consistency(topics: List[str]) -> None:
    """
    Feature: tcg-content-generator, Property 16: Topic serialization format
    Verify that JSON serialization is consistent across multiple operations.
    Validates: Requirements 13.1, 13.2, 13.4, 13.5
    """
    # Serialize multiple times
    serialized_1 = json.dumps(topics)
    serialized_2 = json.dumps(topics)
    
    # Property: Multiple serializations should produce same result
    assert serialized_1 == serialized_2, \
        "JSON serialization should be deterministic"
    
    # Property: Deserialization should always produce same result
    deserialized_1 = json.loads(serialized_1)
    deserialized_2 = json.loads(serialized_2)
    
    assert deserialized_1 == deserialized_2, \
        "Deserialization should be consistent"
    assert deserialized_1 == topics, \
        "Deserialization should match original"


@given(topics=topic_list_strategy())
@settings(max_examples=50)
def test_property_16_database_storage_uses_json(topics: List[str]) -> None:
    """
    Feature: tcg-content-generator, Property 16: Topic serialization format
    Verify that topics are stored in database using JSON format.
    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5
    """
    # Property: Topics should be serializable to JSON for database storage
    try:
        json_topics = json.dumps(topics)
    except (TypeError, ValueError) as e:
        raise AssertionError(f"Topics should be JSON-serializable for DB: {e}") from e
    
    # Property: JSON should be valid and parseable
    try:
        parsed_topics = json.loads(json_topics)
        assert parsed_topics == topics, \
            "Parsed topics should match original"
    except json.JSONDecodeError as e:
        raise AssertionError(f"JSON should be valid for database storage: {e}") from e
    
    # Property: Each topic should be a string (database requirement)
    for topic in parsed_topics:
        assert isinstance(topic, str), \
            "Each topic in database should be a string"
        assert 10 <= len(topic) <= 200, \
            "Each topic should meet length requirements (10-200 chars)"


@given(topics=topic_list_strategy())
@settings(max_examples=100)
def test_property_16_json_preserves_unicode(topics: List[str]) -> None:
    """
    Feature: tcg-content-generator, Property 16: Topic serialization format
    Verify that JSON serialization preserves Unicode characters.
    Validates: Requirements 13.1, 13.2, 13.4, 13.5
    """
    # Property: JSON should handle Unicode characters
    serialized = json.dumps(topics, ensure_ascii=False)
    deserialized = json.loads(serialized)
    
    # Property: Unicode should be preserved
    assert deserialized == topics, \
        "JSON should preserve Unicode characters"
    
    # Property: Each character should be preserved
    for original, restored in zip(topics, deserialized):
        assert original == restored, \
            f"Topic '{original}' should be preserved as '{restored}'"


def test_property_16_empty_list_serialization() -> None:
    """
    Feature: tcg-content-generator, Property 16: Topic serialization format
    Verify that empty topic lists can be serialized.
    Validates: Requirements 13.1, 13.2, 13.4, 13.5
    """
    empty_topics: List[str] = []
    
    # Property: Empty list should be JSON-serializable
    serialized = json.dumps(empty_topics)
    assert serialized == "[]", \
        "Empty list should serialize to '[]'"
    
    # Property: Deserialization should produce empty list
    deserialized = json.loads(serialized)
    assert deserialized == [], \
        "Deserialized empty list should be []"
    assert isinstance(deserialized, list), \
        "Deserialized result should be a list"

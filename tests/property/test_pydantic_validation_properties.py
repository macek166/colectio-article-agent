"""
Property-based tests for Pydantic model validation.

Feature: tcg-content-generator, Property 11: Pydantic model usage
Validates: Requirements 11.1, 11.4, 11.5
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from src.models.topic import Topic, TopicRecord
from src.models.content import Content, ContentRecord
from src.models.agent_output import AgentOutput
from src.models.config import Config


# Hypothesis strategies for generating valid test data
@st.composite
def valid_category_strategy(draw):
    """Generate valid category values."""
    return draw(st.sampled_from(['pokemon', 'hockey', 'soccer']))


@st.composite
def valid_status_strategy(draw):
    """Generate valid status values."""
    return draw(st.sampled_from(['pending', 'in_progress', 'completed', 'failed']))


@st.composite
def valid_title_strategy(draw):
    """Generate valid title strings (10-200 characters)."""
    return draw(st.text(min_size=10, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')  # Exclude surrogates and control chars
    )))


@st.composite
def valid_content_strategy(draw):
    """Generate valid content strings (min 500 characters)."""
    return draw(st.text(min_size=500, max_size=2000, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')
    )))


@st.composite
def valid_draft_strategy(draw):
    """Generate valid draft strings (min 100 characters)."""
    return draw(st.text(min_size=100, max_size=1000, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')
    )))


@st.composite
def valid_topic_distribution_strategy(draw):
    """Generate valid topic distribution dictionaries."""
    pokemon_count = draw(st.integers(min_value=0, max_value=20))
    hockey_count = draw(st.integers(min_value=0, max_value=20))
    soccer_count = draw(st.integers(min_value=0, max_value=20))
    
    # Ensure total is between 1 and 50
    total = pokemon_count + hockey_count + soccer_count
    if total < 1:
        pokemon_count = 1
    elif total > 50:
        # Scale down proportionally
        scale = 50 / total
        pokemon_count = max(0, int(pokemon_count * scale))
        hockey_count = max(0, int(hockey_count * scale))
        soccer_count = max(0, int(soccer_count * scale))
        # Ensure at least 1 total
        if pokemon_count + hockey_count + soccer_count == 0:
            pokemon_count = 1
    
    return {
        'pokemon': pokemon_count,
        'hockey': hockey_count,
        'soccer': soccer_count
    }


# Property 11: Pydantic model usage
# For any valid data, Pydantic models should validate and create instances successfully


@given(
    title=valid_title_strategy(),
    category=valid_category_strategy(),
    status=valid_status_strategy()
)
def test_property_11_topic_model_validates_correct_data(
    title: str,
    category: str,
    status: str
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any valid title, category, and status, the Topic model should
    successfully validate and create an instance.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    topic = Topic(title=title, category=category, status=status)
    
    # Verify all fields are set correctly
    assert isinstance(topic.id, UUID)
    assert topic.title == title.strip()  # Title should be stripped
    assert topic.category == category
    assert topic.status == status
    assert isinstance(topic.created_at, datetime)


@given(category=st.text().filter(lambda x: x not in ['pokemon', 'hockey', 'soccer']))
def test_property_11_topic_model_rejects_invalid_category(category: str) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any invalid category value, the Topic model should raise ValidationError.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    with pytest.raises(ValidationError):
        Topic(title="Valid Title Here", category=category)


@given(
    topic_id=st.uuids(),
    topic_title=valid_title_strategy(),
    category=valid_category_strategy(),
    draft=valid_draft_strategy(),
    final_content=valid_content_strategy(),
    research_sources=st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=10)
)
def test_property_11_content_model_validates_correct_data(
    topic_id: UUID,
    topic_title: str,
    category: str,
    draft: str,
    final_content: str,
    research_sources: list
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any valid content data, the Content model should successfully
    validate and create an instance.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    content = Content(
        topic_id=topic_id,
        topic_title=topic_title,
        category=category,
        draft=draft,
        final_content=final_content,
        research_sources=research_sources,
        metadata={"test": "data"}
    )
    
    # Verify all fields are set correctly
    assert isinstance(content.id, UUID)
    assert content.topic_id == topic_id
    assert content.topic_title == topic_title
    assert content.category == category
    assert content.draft == draft
    assert content.final_content == final_content
    assert content.research_sources == research_sources
    assert isinstance(content.created_at, datetime)
    assert isinstance(content.updated_at, datetime)


@given(
    agent_name=st.text(min_size=1, max_size=50),
    output=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=100),
        min_size=1,
        max_size=10
    )
)
def test_property_11_agent_output_model_validates_correct_data(
    agent_name: str,
    output: dict
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any valid agent output data, the AgentOutput model should
    successfully validate and create an instance.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    agent_output = AgentOutput(agent_name=agent_name, output=output)
    
    # Verify all fields are set correctly
    assert agent_output.agent_name == agent_name
    assert agent_output.output == output
    assert isinstance(agent_output.timestamp, datetime)
    assert isinstance(agent_output.metadata, dict)


@given(distribution=valid_topic_distribution_strategy())
def test_property_11_config_model_validates_correct_distribution(
    distribution: dict
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any valid topic distribution (total between 1-50), the Config model
    should successfully validate and create an instance.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30,
        default_topic_distribution=distribution
    )
    
    # Verify distribution is validated correctly
    assert config.default_topic_distribution == distribution
    total = sum(distribution.values())
    assert 1 <= total <= 50


@given(
    pokemon=st.integers(min_value=0, max_value=100),
    hockey=st.integers(min_value=0, max_value=100),
    soccer=st.integers(min_value=0, max_value=100)
)
def test_property_11_config_model_rejects_invalid_distribution(
    pokemon: int,
    hockey: int,
    soccer: int
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any topic distribution where total is not between 1-50, the Config
    model should raise ValidationError.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    total = pokemon + hockey + soccer
    
    # Only test cases that should fail validation
    if total < 1 or total > 50:
        with pytest.raises(ValidationError):
            Config(
                neon_connection_string="postgresql://user:pass@host:5432/db",
                openai_api_key="sk-" + "x" * 40,
                serper_api_key="serper_" + "x" * 30,
                default_topic_distribution={
                    'pokemon': pokemon,
                    'hockey': hockey,
                    'soccer': soccer
                }
            )


@given(
    title=valid_title_strategy(),
    category=valid_category_strategy()
)
def test_property_11_topic_record_model_validates_correct_data(
    title: str,
    category: str
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any valid data, the TopicRecord model should successfully
    validate and create an instance.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    topic_record = TopicRecord(
        title=title,
        category=category,
        created_at=datetime.now(UTC).isoformat()
    )
    
    # Verify all fields are set correctly
    assert isinstance(topic_record.id, UUID)
    assert topic_record.title == title
    assert topic_record.category == category
    assert topic_record.status == 'pending'


@given(
    topic_id=st.uuids(),
    topic_title=valid_title_strategy(),
    category=valid_category_strategy(),
    final_content=valid_content_strategy(),
    research_sources=st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=10)
)
def test_property_11_content_record_model_validates_correct_data(
    topic_id: UUID,
    topic_title: str,
    category: str,
    final_content: str,
    research_sources: list
) -> None:
    """
    Feature: tcg-content-generator, Property 11: Pydantic model usage
    For any valid data, the ContentRecord model should successfully
    validate and create an instance.
    Validates: Requirements 11.1, 11.4, 11.5
    """
    content_record = ContentRecord(
        topic_id=topic_id,
        topic_title=topic_title,
        category=category,
        final_content=final_content,
        research_sources=research_sources,
        metadata={"test": "data"},
        created_at=datetime.now(UTC).isoformat()
    )
    
    # Verify all fields are set correctly
    assert isinstance(content_record.id, UUID)
    assert content_record.topic_id == topic_id
    assert content_record.topic_title == topic_title
    assert content_record.category == category
    assert content_record.final_content == final_content
    assert content_record.research_sources == research_sources

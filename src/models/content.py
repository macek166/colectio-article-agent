"""Content data models with Pydantic validation."""

from datetime import UTC, datetime
from typing import Any, Dict, List, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Content(BaseModel):
    """Represents generated article content.
    
    Attributes:
        id: Unique identifier for the content
        topic_id: Reference to the topic UUID
        topic_title: Title of the topic
        category: Content category (pokemon, hockey, or soccer)
        draft: Initial draft content
        final_content: Final edited content
        research_sources: List of sources used in research
        metadata: Additional metadata about the content
        created_at: Timestamp when content was created
        updated_at: Timestamp when content was last updated
        status: Current status of the content
    """
    
    id: UUID = Field(default_factory=uuid4)
    topic_id: UUID
    topic_title: str
    category: Literal['pokemon', 'hockey', 'soccer']
    draft: str = Field(..., min_length=100)
    final_content: str = Field(..., min_length=500)
    research_sources: List[str]
    metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = 'completed'
    
    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "topic_id": "123e4567-e89b-12d3-a456-426614174000",
                "topic_title": "Best Pokémon Cards for Investment",
                "category": "pokemon",
                "draft": "Initial draft content...",
                "final_content": "Final edited content...",
                "research_sources": ["https://example.com/source1"],
                "metadata": {"word_count": 1500, "seo_score": 85}
            }
        }
    )


class ContentRecord(BaseModel):
    """Pydantic model for content database record.
    
    Attributes:
        id: Unique identifier for the content
        topic_id: Reference to the topic UUID
        topic_title: Title of the topic
        category: Content category (pokemon, hockey, or soccer)
        final_content: Final edited content
        research_sources: List of sources used in research
        metadata: Additional metadata about the content
        created_at: Timestamp when content was created
        status: Current status of the content
    """
    
    id: UUID = Field(default_factory=uuid4)
    topic_id: UUID
    topic_title: str
    category: Literal['pokemon', 'hockey', 'soccer']
    final_content: str
    research_sources: List[str]
    metadata: Dict[str, Any]
    created_at: str
    status: str = 'completed'
    
    model_config = ConfigDict(validate_assignment=True)

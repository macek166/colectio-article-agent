"""Topic data models with Pydantic validation."""

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Topic(BaseModel):
    """Represents a content topic.

    Attributes:
        id: Unique identifier for the topic
        title: Topic title (10-200 characters)
        category: Content category (pokemon, hockey, or soccer)
        created_at: Timestamp when topic was created
        status: Current status of the topic
    """

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=10, max_length=200)
    category: Literal['pokemon', 'hockey', 'soccer']
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: Literal['pending', 'in_progress', 'completed', 'failed'] = 'pending'

    @field_validator('title')
    @classmethod
    def title_must_be_stripped(cls, v: str) -> str:
        """Validate and normalize title by stripping whitespace."""
        return v.strip()

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "title": "Best Pokémon Cards for Investment in 2024",
                "category": "pokemon",
                "status": "pending"
            }
        }
    )


class TopicRecord(BaseModel):
    """Pydantic model for topic database record.

    Attributes:
        id: Unique identifier for the topic
        title: Topic title
        category: Content category (pokemon, hockey, or soccer)
        created_at: Timestamp when topic was created
        status: Current status of the topic
    """

    id: UUID = Field(default_factory=uuid4)
    title: str
    category: Literal['pokemon', 'hockey', 'soccer']
    created_at: str
    status: Literal['pending', 'in_progress', 'completed', 'failed'] = 'pending'

    model_config = ConfigDict(validate_assignment=True)

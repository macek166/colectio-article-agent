"""Agent output data models with Pydantic validation."""

from datetime import UTC, datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class AgentOutput(BaseModel):
    """Pydantic model for agent output in context management.

    Attributes:
        agent_name: Name of the agent that produced the output
        output: The actual output data from the agent
        timestamp: When the output was generated
        metadata: Additional metadata about the output
    """

    agent_name: str = Field(..., min_length=1)
    output: Any
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "agent_name": "ResearcherAgent",
                "output": {
                    "topic": "Best Pokémon Cards",
                    "sources": ["https://example.com"],
                    "key_points": ["Point 1", "Point 2"]
                },
                "metadata": {"execution_time": 2.5}
            }
        }
    )

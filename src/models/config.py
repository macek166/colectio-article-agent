"""Configuration data models with Pydantic validation."""

from typing import Dict, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Config(BaseModel):
    """System configuration with Pydantic validation.

    Attributes:
        neon_connection_string: PostgreSQL connection string for Neon database
        openai_api_key: API key for OpenAI services
        serper_api_key: API key for Serper.dev SEO services
        kiro_power_name: Name of the Kiro Power for Neon integration
        max_retries: Maximum number of retry attempts for failed operations
        default_topic_distribution: Default distribution of topics by category
        agent_personas: Persona definitions for each agent
        logging_level: Logging level for the application
        pylint_min_score: Minimum acceptable Pylint score
    """

    neon_connection_string: str = Field(..., min_length=10)
    openai_api_key: str = Field(..., min_length=20)
    serper_api_key: str = Field(..., min_length=20)
    kiro_power_name: str = 'neon'
    max_retries: int = Field(default=3, ge=1, le=5)
    default_topic_distribution: Dict[str, int] = Field(
        default={'pokemon': 5, 'hockey': 3, 'soccer': 2}
    )
    agent_personas: Dict[str, str] = Field(default_factory=dict)
    logging_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    pylint_min_score: float = Field(default=8.0, ge=0.0, le=10.0)
    agent_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    agent_max_tokens: int = Field(default=2000, ge=100, le=8000)

    @field_validator('default_topic_distribution')
    @classmethod
    def validate_distribution(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate topic distribution sums to reasonable number.

        Args:
            v: Topic distribution dictionary

        Returns:
            Validated topic distribution

        Raises:
            ValueError: If total topics is not between 1 and 50
        """
        total = sum(v.values())
        if total < 1 or total > 50:
            raise ValueError("Total topics must be between 1 and 50")

        # Validate all categories are present
        required_categories = {'pokemon', 'hockey', 'soccer'}
        if set(v.keys()) != required_categories:
            raise ValueError(
                f"Distribution must contain exactly these categories: {required_categories}"
            )

        # Validate all values are non-negative
        if any(count < 0 for count in v.values()):
            raise ValueError("All topic counts must be non-negative")

        return v

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "neon_connection_string": "postgresql://user:pass@host/db",
                "openai_api_key": "sk-...",
                "serper_api_key": "abc123...",
                "kiro_power_name": "neon",
                "max_retries": 3,
                "default_topic_distribution": {
                    "pokemon": 5,
                    "hockey": 3,
                    "soccer": 2
                },
                "logging_level": "INFO",
                "pylint_min_score": 8.0
            }
        }
    )

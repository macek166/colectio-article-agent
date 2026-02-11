"""
Configuration management with Pydantic validation.

This module provides the main configuration class for the TCG Content Generator,
loading settings from environment variables with comprehensive validation.
"""

import os
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """
    System configuration with Pydantic validation.

    All configuration values are loaded from environment variables and validated
    using Pydantic. This ensures type safety and provides clear error messages
    for misconfiguration.
    """

    # Database Configuration
    neon_connection_string: str = Field(
        ...,
        min_length=10,
        description="PostgreSQL connection string for Neon database"
    )
    kiro_power_name: str = Field(
        default="neon",
        description="Name of the Kiro Power integration for Neon database"
    )

    # API Keys
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI agent operations"
    )
    google_api_key: Optional[str] = Field(
        default=None,
        description="Google API key for Gemini AI operations"
    )
    serper_api_key: str = Field(
        ...,
        min_length=20,
        description="Serper.dev API key for SERP data and Google Trends"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude operations"
    )

    # LLM Provider Configuration
    llm_provider: Literal["openai", "gemini", "anthropic"] = Field(
        default="openai",
        description="LLM provider to use (openai, gemini, or anthropic)"
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model to use"
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model to use"
    )
    anthropic_model: str = Field(
        default="claude-3-haiku-20240307",
        description="Anthropic model to use (Writer)"
    )
    research_model: str = Field(
        default="claude-3-haiku-20240307",
        description="Model to use for Research/Analysis (Faster/Cheaper)"
    )

    # Topic Distribution
    default_topic_distribution: Dict[str, int] = Field(
        default={'pokemon': 5, 'hockey': 3, 'soccer': 2},
        description="Default distribution of topics across categories"
    )

    # System Configuration
    max_retries: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum number of retry attempts for failed operations"
    )
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level for the application"
    )
    pylint_min_score: float = Field(
        default=8.0,
        ge=0.0,
        le=10.0,
        description="Minimum Pylint score required for code quality"
    )

    # Agent Configuration
    agent_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature setting for AI agent creativity"
    )
    agent_max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Maximum tokens for AI agent responses"
    )

    @field_validator('default_topic_distribution')
    @classmethod
    def validate_distribution(cls, v: Dict[str, int]) -> Dict[str, int]:
        """
        Validate topic distribution sums to reasonable number.

        Args:
            v: Topic distribution dictionary

        Returns:
            Validated distribution dictionary

        Raises:
            ValueError: If distribution is invalid
        """
        # Check required categories
        required_categories = {'pokemon', 'hockey', 'soccer'}
        if not all(cat in v for cat in required_categories):
            raise ValueError(
                f"Distribution must include all categories: {required_categories}"
            )

        # Check for invalid categories
        invalid_categories = set(v.keys()) - required_categories
        if invalid_categories:
            raise ValueError(
                f"Invalid categories in distribution: {invalid_categories}"
            )

        # Check total count
        total = sum(v.values())
        if total < 1 or total > 50:
            raise ValueError(
                f"Total topics must be between 1 and 50, got {total}"
            )

        # Check individual counts
        for category, count in v.items():
            if count < 0:
                raise ValueError(
                    f"Category '{category}' has negative count: {count}"
                )

        return v

    @field_validator('neon_connection_string')
    @classmethod
    def validate_connection_string(cls, v: str) -> str:
        """
        Validate Neon connection string format.

        Args:
            v: Connection string

        Returns:
            Validated connection string

        Raises:
            ValueError: If connection string format is invalid
        """
        if not v.startswith('postgresql://'):
            raise ValueError(
                "Connection string must start with 'postgresql://'"
            )
        return v

    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'  # Prevent extra fields
    )


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Config: Validated configuration object

    Raises:
        ValidationError: If configuration is invalid or missing required values
    """
    # Build topic distribution from environment variables
    topic_distribution = {
        'pokemon': int(os.getenv('TOPIC_DISTRIBUTION_POKEMON', '5')),
        'hockey': int(os.getenv('TOPIC_DISTRIBUTION_HOCKEY', '3')),
        'soccer': int(os.getenv('TOPIC_DISTRIBUTION_SOCCER', '2'))
    }

    config_data = {
        'neon_connection_string': os.getenv('NEON_CONNECTION_STRING'),
        'kiro_power_name': os.getenv('KIRO_POWER_NAME', 'neon'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'serper_api_key': os.getenv('SERPER_API_KEY'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
        'gemini_model': os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
        'anthropic_model': os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307'),
        'research_model': os.getenv('RESEARCH_MODEL', 'claude-3-haiku-20240307'),
        'default_topic_distribution': topic_distribution,
        'max_retries': int(os.getenv('MAX_RETRIES', '2')),
        'logging_level': os.getenv('LOGGING_LEVEL', 'INFO'),
        'pylint_min_score': float(os.getenv('PYLINT_MIN_SCORE', '8.0')),
        'agent_temperature': float(os.getenv('AGENT_TEMPERATURE', '0.7')),
        'agent_max_tokens': int(os.getenv('AGENT_MAX_TOKENS', '2000'))
    }

    return Config(**config_data)

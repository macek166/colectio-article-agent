# Configuration Management

This document describes the configuration system for the TCG Content Generator.

## Overview

The configuration system uses **Pydantic** for data validation and **python-dotenv** for environment variable management. All configuration is loaded from environment variables and validated at startup to ensure type safety and catch configuration errors early.

## Configuration Files

### 1. `src/config/settings.py`

Main configuration class with Pydantic validation. Loads all system settings from environment variables.

**Key Features:**
- Type-safe configuration with Pydantic models
- Automatic validation of required fields
- Custom validators for complex rules (e.g., topic distribution)
- Clear error messages for misconfiguration

**Configuration Fields:**
- `neon_connection_string`: PostgreSQL connection string for Neon database
- `kiro_power_name`: Name of Kiro Power integration (default: "neon")
- `openai_api_key`: OpenAI API key for AI operations
- `serper_api_key`: Serper.dev API key for SEO and web research
- `default_topic_distribution`: Default topic counts per category
- `max_retries`: Maximum retry attempts (1-5, default: 3)
- `logging_level`: Application logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `pylint_min_score`: Minimum Pylint code quality score (0.0-10.0, default: 8.0)
- `agent_temperature`: AI agent creativity setting (0.0-2.0, default: 0.7)
- `agent_max_tokens`: Maximum tokens for AI responses (100-8000, default: 2000)

### 2. `src/config/personas.py`

Agent persona definitions for all five specialized agents.

**Agents:**
- **Strategist**: Content Strategy Specialist - generates unique topics with SEO optimization
- **Researcher**: Trading Card Investment Researcher - gathers market data and insights
- **Writer**: Trading Card Content Writer - creates engaging investment articles
- **Editor**: Content Quality Editor - refines and optimizes content
- **Archivist**: Content Archive Manager - stores articles in database

Each persona includes:
- `role`: Agent's professional role
- `goal`: Primary objective
- `backstory`: Context and expertise
- `verbose`: Logging verbosity
- `allow_delegation`: Whether agent can delegate tasks

### 3. `src/config/web_sources.py`

Category-specific web source mappings for research and topic generation.

**Categories:**
- **Pokémon**: 9 sources (eBay, Cardmarket, TCGplayer, Pokebeach, etc.)
- **Hockey**: 8 sources (eBay, COMC, Beckett, Puckjunk, etc.)
- **Soccer**: 7 sources (eBay, COMC, Beckett, Soccer Cards HQ, etc.)

Each source includes:
- `name`: Source name
- `url`: Source URL
- `type`: Source type (marketplace, news, blog, pricing, etc.)
- `description`: Brief description

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Required - Database
NEON_CONNECTION_STRING=postgresql://user:password@host:5432/database
KIRO_POWER_NAME=neon

# Required - API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here

# Optional - Topic Distribution (defaults shown)
TOPIC_DISTRIBUTION_POKEMON=5
TOPIC_DISTRIBUTION_HOCKEY=3
TOPIC_DISTRIBUTION_SOCCER=2

# Optional - System Configuration (defaults shown)
MAX_RETRIES=3
LOGGING_LEVEL=INFO
PYLINT_MIN_SCORE=8.0

# Optional - Agent Configuration (defaults shown)
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2000
```

## Usage Examples

### Loading Configuration

```python
from src.config import load_config

# Load and validate configuration
config = load_config()

# Access configuration values
print(f"Max retries: {config.max_retries}")
print(f"Topic distribution: {config.default_topic_distribution}")
```

### Getting Agent Personas

```python
from src.config import get_persona

# Get persona for a specific agent
strategist_persona = get_persona('strategist')
print(f"Role: {strategist_persona['role']}")
print(f"Goal: {strategist_persona['goal']}")
```

### Accessing Web Sources

```python
from src.config import get_sources_for_category, get_marketplace_sources

# Get all sources for a category
pokemon_sources = get_sources_for_category('pokemon')
for source in pokemon_sources:
    print(f"{source['name']}: {source['url']}")

# Get only marketplace sources
marketplaces = get_marketplace_sources('hockey')
```

## Validation Rules

### Topic Distribution
- Must include all three categories: pokemon, hockey, soccer
- Total topics must be between 1 and 50
- Individual counts cannot be negative
- No invalid categories allowed

### Connection String
- Must start with `postgresql://`
- Must be at least 10 characters long

### Retry Configuration
- Must be between 1 and 5 (inclusive)

### Pylint Score
- Must be between 0.0 and 10.0 (inclusive)

### Agent Temperature
- Must be between 0.0 and 2.0 (inclusive)

### Agent Max Tokens
- Must be between 100 and 8000 (inclusive)

## Error Handling

The configuration system provides clear error messages when validation fails:

```python
from pydantic import ValidationError

try:
    config = load_config()
except ValidationError as e:
    print(f"Configuration error: {e}")
    # Shows exactly which fields are invalid and why
```

## Testing

Run configuration tests:

```bash
pytest tests/test_config.py -v
```

Tests cover:
- Valid configuration creation
- Invalid field validation
- Topic distribution validation
- Persona retrieval
- Web source access
- Edge cases and error conditions

## Best Practices

1. **Never commit `.env` files** - Use `.env.example` as a template
2. **Validate early** - Load configuration at application startup
3. **Use type hints** - Leverage Pydantic's type checking
4. **Document changes** - Update `.env.example` when adding new config
5. **Test validation** - Write tests for custom validators
6. **Fail fast** - Let Pydantic catch configuration errors immediately

## See Also

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- `.env.example` - Template for environment variables
- `examples/config_usage.py` - Working example of configuration usage

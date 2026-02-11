"""
Unit tests for configuration management.

Tests the Config class, environment variable loading, and validation logic.
"""

import pytest
from pydantic import ValidationError
from src.config.settings import Config
from src.config.personas import get_persona, AGENT_PERSONAS
from src.config.web_sources import (
    get_sources_for_category,
    get_source_urls_for_category,
    get_all_categories,
    get_marketplace_sources
)


class TestConfigValidation:
    """Test Config model validation."""
    
    def test_valid_config_creation(self):
        """Test creating a valid Config instance."""
        config = Config(
            neon_connection_string="postgresql://user:pass@host:5432/db",
            openai_api_key="sk-test1234567890123456789012",
            serper_api_key="test_serper_key_12345678"
        )
        assert config.neon_connection_string == "postgresql://user:pass@host:5432/db"
        assert config.max_retries == 3
        assert config.default_topic_distribution == {'pokemon': 5, 'hockey': 3, 'soccer': 2}
    
    def test_invalid_connection_string(self):
        """Test that invalid connection string raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                neon_connection_string="invalid_connection_string",
                openai_api_key="sk-test1234567890123456789012",
                serper_api_key="test_serper_key_12345678"
            )
        assert "Connection string must start with 'postgresql://'" in str(exc_info.value)
    
    def test_invalid_topic_distribution_total(self):
        """Test that invalid total topic count raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                neon_connection_string="postgresql://user:pass@host:5432/db",
                openai_api_key="sk-test1234567890123456789012",
                serper_api_key="test_serper_key_12345678",
                default_topic_distribution={'pokemon': 100, 'hockey': 100, 'soccer': 100}
            )
        assert "Total topics must be between 1 and 50" in str(exc_info.value)
    
    def test_missing_category_in_distribution(self):
        """Test that missing category in distribution raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                neon_connection_string="postgresql://user:pass@host:5432/db",
                openai_api_key="sk-test1234567890123456789012",
                serper_api_key="test_serper_key_12345678",
                default_topic_distribution={'pokemon': 5, 'hockey': 3}
            )
        assert "Distribution must include all categories" in str(exc_info.value)
    
    def test_invalid_category_in_distribution(self):
        """Test that invalid category in distribution raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                neon_connection_string="postgresql://user:pass@host:5432/db",
                openai_api_key="sk-test1234567890123456789012",
                serper_api_key="test_serper_key_12345678",
                default_topic_distribution={'pokemon': 5, 'hockey': 3, 'soccer': 2, 'invalid': 1}
            )
        assert "Invalid categories in distribution" in str(exc_info.value)
    
    def test_max_retries_bounds(self):
        """Test that max_retries is bounded correctly."""
        # Valid value
        config = Config(
            neon_connection_string="postgresql://user:pass@host:5432/db",
            openai_api_key="sk-test1234567890123456789012",
            serper_api_key="test_serper_key_12345678",
            max_retries=3
        )
        assert config.max_retries == 3
        
        # Too low
        with pytest.raises(ValidationError):
            Config(
                neon_connection_string="postgresql://user:pass@host:5432/db",
                openai_api_key="sk-test1234567890123456789012",
                serper_api_key="test_serper_key_12345678",
                max_retries=0
            )
        
        # Too high
        with pytest.raises(ValidationError):
            Config(
                neon_connection_string="postgresql://user:pass@host:5432/db",
                openai_api_key="sk-test1234567890123456789012",
                serper_api_key="test_serper_key_12345678",
                max_retries=10
            )


class TestPersonas:
    """Test agent persona retrieval."""
    
    def test_get_valid_persona(self):
        """Test retrieving valid agent personas."""
        for agent_name in ['strategist', 'researcher', 'writer', 'editor', 'archivist']:
            persona = get_persona(agent_name)
            assert 'role' in persona
            assert 'goal' in persona
            assert 'backstory' in persona
            assert persona['verbose'] is True
            assert persona['allow_delegation'] is False
    
    def test_get_invalid_persona(self):
        """Test that invalid agent name raises error."""
        with pytest.raises(ValueError) as exc_info:
            get_persona('invalid_agent')
        assert "Unknown agent name" in str(exc_info.value)
    
    def test_all_personas_present(self):
        """Test that all required personas are defined."""
        required_agents = ['strategist', 'researcher', 'writer', 'editor', 'archivist']
        for agent in required_agents:
            assert agent in AGENT_PERSONAS


class TestWebSources:
    """Test web source configuration."""
    
    def test_get_sources_for_valid_category(self):
        """Test retrieving sources for valid categories."""
        for category in ['pokemon', 'hockey', 'soccer']:
            sources = get_sources_for_category(category)
            assert len(sources) > 0
            for source in sources:
                assert 'name' in source
                assert 'url' in source
                assert 'type' in source
                assert 'description' in source
    
    def test_get_sources_for_invalid_category(self):
        """Test that invalid category raises error."""
        with pytest.raises(ValueError) as exc_info:
            get_sources_for_category('invalid')
        assert "Unknown category" in str(exc_info.value)
    
    def test_get_source_urls(self):
        """Test retrieving just URLs for a category."""
        urls = get_source_urls_for_category('pokemon')
        assert len(urls) > 0
        assert all(isinstance(url, str) for url in urls)
        assert all(url.startswith('http') for url in urls)
    
    def test_get_all_categories(self):
        """Test retrieving all valid categories."""
        categories = get_all_categories()
        assert set(categories) == {'pokemon', 'hockey', 'soccer'}
    
    def test_get_marketplace_sources(self):
        """Test retrieving marketplace sources."""
        for category in ['pokemon', 'hockey', 'soccer']:
            marketplace_sources = get_marketplace_sources(category)
            assert len(marketplace_sources) > 0
            assert all(source['type'] == 'marketplace' for source in marketplace_sources)
    
    def test_pokemon_sources_include_ebay(self):
        """Test that Pokémon sources include eBay."""
        sources = get_sources_for_category('pokemon')
        source_names = [s['name'] for s in sources]
        assert 'eBay' in source_names
    
    def test_hockey_sources_include_comc(self):
        """Test that Hockey sources include COMC."""
        sources = get_sources_for_category('hockey')
        source_names = [s['name'] for s in sources]
        assert 'COMC' in source_names
    
    def test_soccer_sources_include_beckett(self):
        """Test that Soccer sources include Beckett."""
        sources = get_sources_for_category('soccer')
        source_names = [s['name'] for s in sources]
        assert 'Beckett Soccer' in source_names

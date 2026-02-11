"""
Configuration modules for TCG Content Generator.

This package provides configuration management, agent personas, and web source
mappings for the Trading Card Content Generator system.
"""

from src.config.settings import Config, load_config
from src.config.personas import (
    AGENT_PERSONAS,
    STRATEGIST_PERSONA,
    RESEARCHER_PERSONA,
    WRITER_PERSONA,
    EDITOR_PERSONA,
    ARCHIVIST_PERSONA,
    get_persona
)
from src.config.web_sources import (
    CATEGORY_SOURCES,
    POKEMON_SOURCES,
    HOCKEY_SOURCES,
    SOCCER_SOURCES,
    get_sources_for_category,
    get_source_urls_for_category,
    get_sources_by_type,
    get_all_categories,
    get_marketplace_sources,
    get_news_sources
)

__all__ = [
    # Settings
    'Config',
    'load_config',
    # Personas
    'AGENT_PERSONAS',
    'STRATEGIST_PERSONA',
    'RESEARCHER_PERSONA',
    'WRITER_PERSONA',
    'EDITOR_PERSONA',
    'ARCHIVIST_PERSONA',
    'get_persona',
    # Web Sources
    'CATEGORY_SOURCES',
    'POKEMON_SOURCES',
    'HOCKEY_SOURCES',
    'SOCCER_SOURCES',
    'get_sources_for_category',
    'get_source_urls_for_category',
    'get_sources_by_type',
    'get_all_categories',
    'get_marketplace_sources',
    'get_news_sources'
]

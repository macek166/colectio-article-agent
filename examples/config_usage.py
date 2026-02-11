"""
Example usage of the configuration system.

This script demonstrates how to load and use the configuration,
personas, and web sources in the TCG Content Generator.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    load_config,
    get_persona,
    get_sources_for_category,
    get_all_categories
)


def main():
    """Demonstrate configuration usage."""
    
    print("=" * 60)
    print("TCG Content Generator - Configuration Example")
    print("=" * 60)
    
    # Load configuration from environment variables
    print("\n1. Loading Configuration...")
    try:
        config = load_config()
        print(f"   ✓ Configuration loaded successfully")
        print(f"   - Max Retries: {config.max_retries}")
        print(f"   - Logging Level: {config.logging_level}")
        print(f"   - Pylint Min Score: {config.pylint_min_score}")
        print(f"   - Topic Distribution: {config.default_topic_distribution}")
    except Exception as e:
        print(f"   ✗ Configuration validation failed (expected without .env file)")
        print(f"   Note: Set NEON_CONNECTION_STRING, OPENAI_API_KEY, and SERPER_API_KEY")
        print(f"   Continuing with demonstration of other features...")
    
    # Get agent personas
    print("\n2. Agent Personas...")
    agents = ['strategist', 'researcher', 'writer', 'editor', 'archivist']
    for agent_name in agents:
        persona = get_persona(agent_name)
        print(f"   - {agent_name.capitalize()}: {persona['role']}")
    
    # Get web sources for each category
    print("\n3. Category-Specific Web Sources...")
    categories = get_all_categories()
    for category in categories:
        sources = get_sources_for_category(category)
        print(f"   - {category.capitalize()}: {len(sources)} sources")
        for source in sources[:3]:  # Show first 3 sources
            print(f"     • {source['name']} ({source['type']})")
        if len(sources) > 3:
            print(f"     ... and {len(sources) - 3} more")
    
    print("\n" + "=" * 60)
    print("Configuration system is ready to use!")
    print("=" * 60)


if __name__ == "__main__":
    main()

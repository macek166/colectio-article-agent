"""
Pytest configuration and fixtures for integration tests.
"""

import pytest
from unittest.mock import Mock
from src.config.settings import Config
from src.tools.neon_db_client import NeonDBClient
from src.tools.context7_client import Context7Client


@pytest.fixture
def mock_config():
    """Create mock configuration for testing."""
    return Config(
        neon_connection_string="postgresql://test:test@localhost/test",
        openai_api_key="test_key_" + "x" * 20,
        serper_api_key="test_serper_" + "x" * 20,
        kiro_power_name="neon",
        max_retries=3,
        default_topic_distribution={'pokemon': 5, 'hockey': 3, 'soccer': 2},
        logging_level="INFO",
        pylint_min_score=8.0,
        agent_temperature=0.7,
        agent_max_tokens=2000
    )


@pytest.fixture
def mock_neon_client():
    """Create mock Neon database client."""
    client = Mock(spec=NeonDBClient)
    client.query_all_topics.return_value = []
    client.create_topic.return_value = "test-uuid"
    client.create_content.return_value = "test-uuid"
    client.verify_connection.return_value = True
    return client


@pytest.fixture
def mock_context7_client():
    """Create mock Context7 MCP client."""
    client = Mock(spec=Context7Client)
    client.resolve_library.return_value = "/test/library"
    client.get_docs.return_value = "Test documentation"
    return client


@pytest.fixture
def mock_seo_tools():
    """Create mock SEO tools."""
    from src.tools.seo_tools import SEOTools
    tools = Mock(spec=SEOTools)
    tools.get_serp_data.return_value = {
        'organic_results': [],
        'related_searches': [],
        'search_metadata': {}
    }
    tools.get_keywords.return_value = ['test', 'keyword']
    tools.scrape_category_sources.return_value = {
        'sources': [],
        'content': {},
        'failed_sources': []
    }
    return tools


@pytest.fixture
def mock_doc_manager(temp_docs_dir):
    """Create mock documentation manager."""
    from src.utils.documentation_manager import DocumentationManager
    manager = Mock(spec=DocumentationManager)
    manager.log_event.return_value = None
    manager.log_problem.return_value = None
    manager.update_problem_status.return_value = None
    return manager


@pytest.fixture
def temp_docs_dir(tmp_path):
    """Create temporary docs directory."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    return str(docs_dir)

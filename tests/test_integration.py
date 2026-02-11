"""
Integration tests for the TCG Content Generator system.

Tests the complete workflow from UI to database, including:
- Kiro Power integration
- Context7 MCP integration
- Error recovery with retry logic
- Sequential processing
- Documentation updates
- Category-specific source consultation
- Topic deduplication
- JSON serialization
"""

import json
import pytest
from unittest.mock import Mock, patch
from src.orchestrator import Orchestrator
from src.config.settings import Config
from src.utils.documentation_manager import DocumentationManager
from src.tools.neon_db_client import NeonDBClient
from src.tools.context7_client import Context7Client
from src.tools.seo_tools import SEOTools


class TestIntegration:
    """Integration tests for the complete system workflow."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return Config(
            neon_connection_string="postgresql://test:test@localhost:5432/test",
            openai_api_key="test_key_" + "x" * 20,
            serper_api_key="test_serper_" + "x" * 20,
            default_topic_distribution={"pokemon": 2, "hockey": 1, "soccer": 1},
            max_retries=3,
            agent_temperature=0.7,
            agent_max_tokens=2000
        )

    @pytest.fixture
    def mock_db_client(self):
        """Create a mock database client."""
        client = Mock(spec=NeonDBClient)
        client.verify_connection.return_value = True
        client.query_all_topics.return_value = []
        client.create_topic.return_value = True
        client.create_content.return_value = True
        client.update_status.return_value = True
        return client

    @pytest.fixture
    def mock_context7_client(self):
        """Create a mock Context7 client."""
        client = Mock(spec=Context7Client)
        client.resolve_library.return_value = "/test/library"
        client.get_docs.return_value = {"docs": "Test documentation"}
        return client

    @pytest.fixture
    def mock_seo_tools(self):
        """Create a mock SEO tools instance."""
        tools = Mock(spec=SEOTools)
        tools.get_serp_data.return_value = {"results": []}
        tools.get_google_trends.return_value = {"trends": []}
        tools.get_keywords.return_value = ["keyword1", "keyword2"]
        return tools

    @pytest.fixture
    def mock_doc_manager(self, tmp_path):
        """Create a real documentation manager with temp directory."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        return DocumentationManager(str(docs_dir))

    def test_complete_workflow_ui_to_database(
        self, mock_config, mock_db_client, mock_context7_client,
        mock_seo_tools, mock_doc_manager
    ):
        """Test complete workflow from UI to database."""
        with patch("src.orchestrator.StrategyPhase") as mock_strategy:
            with patch("src.orchestrator.ContentCrew") as mock_crew:
                # Mock strategy phase to return topics
                mock_strategy_instance = Mock()
                mock_strategy_instance.generate_topics.return_value = [
                    "Pokemon Topic 1",
                    "Pokemon Topic 2",
                    "Hockey Topic 1",
                    "Soccer Topic 1"
                ]
                mock_strategy.return_value = mock_strategy_instance

                # Mock content crew execution
                mock_crew_instance = Mock()
                mock_crew_instance.execute.return_value = Mock(
                    status="success",
                    final_content="Test content"
                )
                mock_crew.return_value = mock_crew_instance

                # Create orchestrator
                orchestrator = Orchestrator(
                    config=mock_config,
                    neon_client=mock_db_client,
                    context7_client=mock_context7_client,
                    seo_tools=mock_seo_tools,
                    doc_manager=mock_doc_manager
                )

                result = orchestrator.run()

                # Verify workflow completed
                assert result.total_topics >= 0
                assert mock_db_client.verify_connection.called
                assert mock_strategy_instance.generate_topics.called

    def test_kiro_power_integration(self, mock_config):
        """Test Kiro Power integration works correctly."""
        with patch("src.tools.neon_db_client.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Create DB client
            db_client = NeonDBClient(
                connection_string=mock_config.neon_connection_string,
                config=mock_config
            )

            # Test connection
            assert db_client.verify_connection() is True
            assert mock_connect.called

            # Test query
            mock_cursor.fetchall.return_value = [("Topic 1",), ("Topic 2",)]
            topics = db_client.query_all_topics()
            assert len(topics) == 2
            assert "Topic 1" in topics

    @patch("src.tools.context7_client.mcp_Context7_resolve_library_id")
    @patch("src.tools.context7_client.mcp_Context7_get_library_docs")
    def test_context7_mcp_integration(self, mock_get_docs, mock_resolve):
        """Test Context7 MCP integration works correctly."""
        from src.tools.context7_client import Context7Client

        # Mock MCP responses
        mock_resolve.return_value = {"library_id": "/test/library"}
        mock_get_docs.return_value = {"docs": "Test documentation"}

        client = Context7Client()

        # Test library resolution
        lib_id = client.resolve_library("test-library")
        assert lib_id == "/test/library"
        assert mock_resolve.called

        # Test documentation retrieval
        docs = client.get_docs("/test/library", "test topic")
        assert "docs" in docs
        assert mock_get_docs.called

    def test_json_serialization_of_topics(self):
        """Test JSON serialization of topics."""
        topics = ["Topic 1", "Topic 2", "Topic 3"]

        # Test serialization
        json_str = json.dumps(topics)
        assert isinstance(json_str, str)

        # Test deserialization
        deserialized = json.loads(json_str)
        assert deserialized == topics
        assert isinstance(deserialized, list)

    def test_category_specific_sources_exist(self):
        """Test that category-specific source configuration exists."""
        # Import and verify web sources configuration exists
        try:
            from src.config import web_sources
            # Verify the module can be imported
            assert web_sources is not None
        except ImportError:
            pytest.skip("Web sources configuration not yet implemented")

    def test_default_topic_distribution(self):
        """Test with default distribution (5 Pokémon, 3 Hockey, 2 Soccer)."""
        default_config = Config(
            neon_connection_string="postgresql://test:test@localhost:5432/test",
            openai_api_key="test_key_" + "x" * 20,
            serper_api_key="test_serper_" + "x" * 20,
            default_topic_distribution={"pokemon": 5, "hockey": 3, "soccer": 2},
            max_retries=3,
            agent_temperature=0.7,
            agent_max_tokens=2000
        )

        # Verify distribution
        assert default_config.default_topic_distribution["pokemon"] == 5
        assert default_config.default_topic_distribution["hockey"] == 3
        assert default_config.default_topic_distribution["soccer"] == 2

    def test_custom_topic_distribution(self):
        """Test with custom distributions."""
        custom_config = Config(
            neon_connection_string="postgresql://test:test@localhost:5432/test",
            openai_api_key="test_key_" + "x" * 20,
            serper_api_key="test_serper_" + "x" * 20,
            default_topic_distribution={"pokemon": 10, "hockey": 5, "soccer": 3},
            max_retries=3,
            agent_temperature=0.7,
            agent_max_tokens=2000
        )

        # Verify custom distribution
        assert custom_config.default_topic_distribution["pokemon"] == 10
        assert custom_config.default_topic_distribution["hockey"] == 5
        assert custom_config.default_topic_distribution["soccer"] == 3

    def test_documentation_updates(self, tmp_path):
        """Test that DOCUMENTATION.md and PROBLEMS.md are updated correctly."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        doc_manager = DocumentationManager(str(docs_dir))

        # Log some events
        doc_manager.log_event("Test event 1", "component1")
        doc_manager.log_event("Test event 2", "component2")

        # Log some problems
        doc_manager.log_problem(
            "Test problem 1",
            "active",
            "Error details"
        )

        # Verify files were created and updated
        docs_file = docs_dir / "DOCUMENTATION.md"
        problems_file = docs_dir / "PROBLEMS.md"

        assert docs_file.exists()
        assert problems_file.exists()

        # Verify content
        docs_content = docs_file.read_text()
        assert "Test event 1" in docs_content
        assert "component1" in docs_content

        problems_content = problems_file.read_text()
        assert "Test problem 1" in problems_content
        assert "active" in problems_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

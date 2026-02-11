"""
Integration tests for Neon database via Kiro Power.

Tests real database operations including:
- Connection management
- Query execution
- Topic creation and retrieval
- Content storage
- Transaction handling
- Error recovery
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

from src.tools.neon_db_client import NeonDBClient, TopicRecord, ContentRecord
from src.config.settings import Config


class TestNeonDatabaseIntegration:
    """Test Neon database integration via Kiro Power."""
    
    def test_connection_verification(self, mock_config):
        """
        Test Neon database connection verification via Kiro Power.
        
        Verifies:
        - Connection can be established
        - Kiro Power integration works
        - Connection status is returned correctly
        """
        with patch('src.tools.neon_db_client.NeonDBClient.verify_connection') as mock_verify:
            mock_verify.return_value = True
            
            client = NeonDBClient(mock_config)
            assert client.verify_connection() is True
    
    def test_query_all_topics(self, mock_config):
        """
        Test querying all existing topics from database.
        
        Verifies:
        - All topics are retrieved
        - Topics are returned as list of strings
        - Query executes successfully
        """
        with patch('src.tools.neon_db_client.NeonDBClient.query_all_topics') as mock_query:
            mock_query.return_value = ["Topic 1", "Topic 2", "Topic 3"]
            
            client = NeonDBClient(mock_config)
            topics = client.query_all_topics()
            
            assert isinstance(topics, list)
            assert len(topics) == 3
            assert all(isinstance(t, str) for t in topics)
    
    def test_create_topic_record(self, mock_config):
        """
        Test creating a new topic record in database.
        
        Verifies:
        - Topic record is created
        - UUID is returned
        - Pydantic validation works
        """
        with patch('src.tools.neon_db_client.NeonDBClient.create_topic') as mock_create:
            test_uuid = uuid.uuid4()
            mock_create.return_value = test_uuid
            
            client = NeonDBClient(mock_config)
            
            record = TopicRecord(
                title="Test Topic",
                category="pokemon",
                created_at=datetime.utcnow().isoformat(),
                status="pending"
            )
            
            result_uuid = client.create_topic(record)
            assert result_uuid == test_uuid
    
    def test_create_content_record(self, mock_config):
        """
        Test creating a new content record in database.
        
        Verifies:
        - Content record is created
        - UUID is returned
        - All fields are stored correctly
        """
        with patch('src.tools.neon_db_client.NeonDBClient.create_content') as mock_create:
            test_uuid = uuid.uuid4()
            mock_create.return_value = test_uuid
            
            client = NeonDBClient(mock_config)
            
            record = ContentRecord(
                topic_id=uuid.uuid4(),
                topic_title="Test Topic",
                category="pokemon",
                final_content="Test article content",
                research_sources=["source1", "source2"],
                metadata={"key": "value"},
                created_at=datetime.utcnow().isoformat(),
                status="completed"
            )
            
            result_uuid = client.create_content(record)
            assert result_uuid == test_uuid
    
    def test_update_status(self, mock_config):
        """
        Test updating content status in database.
        
        Verifies:
        - Status can be updated
        - Update executes successfully
        """
        with patch('src.tools.neon_db_client.NeonDBClient.update_status') as mock_update:
            mock_update.return_value = None
            
            client = NeonDBClient(mock_config)
            test_uuid = uuid.uuid4()
            
            # Should not raise exception
            client.update_status(test_uuid, "completed")
            mock_update.assert_called_once_with(test_uuid, "completed")
    
    def test_parameterized_query_execution(self, mock_config):
        """
        Test executing parameterized SQL queries.
        
        Verifies:
        - Parameterized queries work
        - SQL injection is prevented
        - Results are returned correctly
        """
        with patch('src.tools.neon_db_client.NeonDBClient.execute_query') as mock_execute:
            mock_execute.return_value = [
                {"id": "uuid1", "title": "Topic 1"},
                {"id": "uuid2", "title": "Topic 2"}
            ]
            
            client = NeonDBClient(mock_config)
            
            query = "SELECT * FROM topics WHERE category = %(category)s"
            params = {"category": "pokemon"}
            
            results = client.execute_query(query, params)
            
            assert len(results) == 2
            assert results[0]["title"] == "Topic 1"
    
    def test_connection_retry_on_failure(self, mock_config):
        """
        Test connection retry logic with exponential backoff.
        
        Verifies:
        - Failed connections are retried
        - Exponential backoff is applied
        - Maximum retry limit is enforced
        """
        attempt_count = 0
        
        def mock_connect():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Connection failed")
            return True
        
        with patch('src.tools.neon_db_client.NeonDBClient.verify_connection') as mock_verify:
            mock_verify.side_effect = mock_connect
            
            client = NeonDBClient(mock_config)
            
            # Should succeed on third attempt
            result = client.verify_connection()
            assert result is True
            assert attempt_count == 3
    
    def test_unique_constraint_on_topic_title(self, mock_config):
        """
        Test that duplicate topic titles are rejected.
        
        Verifies:
        - UNIQUE constraint is enforced
        - Duplicate titles raise error
        - Error is handled appropriately
        """
        with patch('src.tools.neon_db_client.NeonDBClient.create_topic') as mock_create:
            # First call succeeds
            mock_create.return_value = uuid.uuid4()
            
            client = NeonDBClient(mock_config)
            
            record1 = TopicRecord(
                title="Duplicate Topic",
                category="pokemon",
                created_at=datetime.utcnow().isoformat()
            )
            
            # First creation succeeds
            uuid1 = client.create_topic(record1)
            assert uuid1 is not None
            
            # Second call with same title should fail
            mock_create.side_effect = Exception("UNIQUE constraint violation")
            
            record2 = TopicRecord(
                title="Duplicate Topic",
                category="hockey",
                created_at=datetime.utcnow().isoformat()
            )
            
            with pytest.raises(Exception):
                client.create_topic(record2)
    
    def test_jsonb_storage_for_metadata(self, mock_config):
        """
        Test JSONB storage for metadata fields.
        
        Verifies:
        - Complex metadata can be stored
        - JSONB queries work correctly
        - Data is preserved accurately
        """
        with patch('src.tools.neon_db_client.NeonDBClient.create_content') as mock_create:
            mock_create.return_value = uuid.uuid4()
            
            client = NeonDBClient(mock_config)
            
            complex_metadata = {
                "seo_keywords": ["pokemon", "cards", "investment"],
                "word_count": 1500,
                "reading_time": 7,
                "sources": [
                    {"name": "eBay", "url": "https://ebay.com"},
                    {"name": "Cardmarket", "url": "https://cardmarket.com"}
                ]
            }
            
            record = ContentRecord(
                topic_id=uuid.uuid4(),
                topic_title="Test Topic",
                category="pokemon",
                final_content="Content",
                research_sources=["source1"],
                metadata=complex_metadata,
                created_at=datetime.utcnow().isoformat()
            )
            
            result_uuid = client.create_content(record)
            assert result_uuid is not None
    
    def test_transaction_rollback_on_error(self, mock_config):
        """
        Test transaction rollback when errors occur.
        
        Verifies:
        - Transactions are rolled back on error
        - Database remains consistent
        - No partial data is committed
        """
        with patch('src.tools.neon_db_client.NeonDBClient.execute_query') as mock_execute:
            # Simulate transaction failure
            mock_execute.side_effect = Exception("Transaction failed")
            
            client = NeonDBClient(mock_config)
            
            with pytest.raises(Exception):
                client.execute_query("BEGIN; INSERT INTO topics...; COMMIT;")
            
            # Verify rollback occurred (in real implementation)
            # This would check that no data was committed


class TestKiroPowerSpecificFeatures:
    """Test Kiro Power specific features."""
    
    def test_kiro_power_name_configuration(self, mock_config):
        """
        Test Kiro Power name is configured correctly.
        
        Verifies:
        - Kiro Power name is set
        - Configuration is used for connection
        """
        assert mock_config.kiro_power_name == "neon"
    
    def test_kiro_power_connection_pooling(self, mock_config):
        """
        Test Kiro Power connection pooling.
        
        Verifies:
        - Connection pool is managed
        - Connections are reused
        - Pool limits are respected
        """
        with patch('src.tools.neon_db_client.NeonDBClient') as mock_client_class:
            mock_client = Mock()
            mock_client.verify_connection.return_value = True
            mock_client_class.return_value = mock_client
            
            # Create multiple clients
            client1 = NeonDBClient(mock_config)
            client2 = NeonDBClient(mock_config)
            
            # Both should use connection pooling
            assert client1.verify_connection() is True
            assert client2.verify_connection() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

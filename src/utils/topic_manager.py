"""Topic management utilities for deduplication and storage.

This module provides synchronous wrappers around the async database operations
for easy integration with CrewAI agents.
"""

import asyncio
import logging
from typing import List, Set, Dict, Any
from .database import NeonDatabaseClient

logger = logging.getLogger(__name__)


class TopicManager:
    """Synchronous wrapper for topic management operations."""
    
    def __init__(self):
        """Initialize the topic manager."""
        self.client = NeonDatabaseClient()
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop for async operations."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def get_existing_topics(self, category: str = None) -> List[str]:
        """Get existing topic titles from database.
        
        Args:
            category: Optional category filter (pokemon, hockey, soccer)
            
        Returns:
            List of existing topic titles
        """
        try:
            loop = self._get_loop()
            return loop.run_until_complete(
                self.client.get_existing_topics(category)
            )
        except Exception as e:
            logger.error(f"Failed to get existing topics: {e}")
            return []
    
    def deduplicate_topics(self, new_topics: List[str], category: str = None) -> List[str]:
        """Remove topics that already exist in database.
        
        Args:
            new_topics: List of new topic candidates
            category: Optional category filter
            
        Returns:
            List of unique topics not in database
        """
        try:
            existing = set(self.get_existing_topics(category))
            unique_topics = [topic for topic in new_topics if topic not in existing]
            
            logger.info(f"Filtered {len(new_topics)} topics -> {len(unique_topics)} unique")
            if len(new_topics) > len(unique_topics):
                duplicates = len(new_topics) - len(unique_topics)
                logger.info(f"Removed {duplicates} duplicate topics")
            
            return unique_topics
        except Exception as e:
            logger.error(f"Failed to deduplicate topics: {e}")
            return new_topics  # Return original list if deduplication fails
    
    def save_topic(self, title: str, category: str) -> str:
        """Save a new topic to database.
        
        Args:
            title: Topic title
            category: Category (pokemon, hockey, soccer)
            
        Returns:
            Topic ID (UUID)
        """
        try:
            loop = self._get_loop()
            return loop.run_until_complete(
                self.client.save_topic(title, category)
            )
        except Exception as e:
            logger.error(f"Failed to save topic: {e}")
            raise
    
    def update_topic_status(self, topic_id: str, status: str) -> None:
        """Update topic status.
        
        Args:
            topic_id: Topic UUID
            status: New status (pending, in_progress, completed, failed)
        """
        try:
            loop = self._get_loop()
            loop.run_until_complete(
                self.client.update_topic_status(topic_id, status)
            )
        except Exception as e:
            logger.error(f"Failed to update topic status: {e}")
            raise
    
    def save_content(self, topic_id: str, topic_title: str, category: str,
                    final_content: str, research_sources: List[str] = None,
                    metadata: Dict[str, Any] = None) -> str:
        """Save article content to database.
        
        Args:
            topic_id: Topic UUID
            topic_title: Topic title
            category: Category
            final_content: Final article content
            research_sources: List of research source URLs
            metadata: Additional metadata
            
        Returns:
            Content ID (UUID)
        """
        try:
            loop = self._get_loop()
            return loop.run_until_complete(
                self.client.save_content(
                    topic_id, topic_title, category, final_content,
                    research_sources, metadata
                )
            )
        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            loop = self._get_loop()
            return loop.run_until_complete(self.client.test_connection())
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self) -> None:
        """Close database connections."""
        try:
            loop = self._get_loop()
            loop.run_until_complete(self.client.disconnect())
        except Exception as e:
            logger.error(f"Failed to close database connection: {e}")


# Global instance for easy access
_topic_manager = None

def get_topic_manager() -> TopicManager:
    """Get global topic manager instance."""
    global _topic_manager
    if _topic_manager is None:
        _topic_manager = TopicManager()
    return _topic_manager


def deduplicate_topics(topics: List[str], category: str = None) -> List[str]:
    """Convenience function to deduplicate topics against database.
    
    Args:
        topics: List of topic candidates
        category: Optional category filter
        
    Returns:
        List of unique topics not in database
    """
    manager = get_topic_manager()
    return manager.deduplicate_topics(topics, category)


def save_topic(title: str, category: str) -> str:
    """Convenience function to save a topic.
    
    Args:
        title: Topic title
        category: Category (pokemon, hockey, soccer)
        
    Returns:
        Topic ID (UUID)
    """
    manager = get_topic_manager()
    return manager.save_topic(title, category)


if __name__ == "__main__":
    # Test the topic manager
    manager = TopicManager()
    
    print("Testing topic manager...")
    if manager.test_connection():
        print("✅ Database connection successful!")
        
        # Test getting existing topics
        topics = manager.get_existing_topics()
        print(f"Found {len(topics)} existing topics")
        
        # Test deduplication
        test_topics = ["Test Topic 1", "Test Topic 2", "Test Topic 3"]
        unique = manager.deduplicate_topics(test_topics, "pokemon")
        print(f"Unique topics: {unique}")
        
    else:
        print("❌ Database connection failed!")
    
    manager.close()
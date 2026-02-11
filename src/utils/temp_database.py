"""Temporary in-memory database for topic management during setup.

This module provides a simple in-memory solution for topic deduplication
while we set up the Neon database connection.
"""

import json
import os
from typing import List, Set, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TempTopicDatabase:
    """Temporary file-based topic storage for development."""
    
    def __init__(self, storage_file: str = "temp_topics.json"):
        """Initialize temporary database.
        
        Args:
            storage_file: Path to JSON file for storing topics
        """
        self.storage_file = Path(storage_file)
        self.topics = self._load_topics()
    
    def _load_topics(self) -> Dict[str, List[str]]:
        """Load topics from storage file."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load topics from {self.storage_file}: {e}")
        
        return {"pokemon": [], "hockey": [], "soccer": []}
    
    def _save_topics(self) -> None:
        """Save topics to storage file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.topics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save topics to {self.storage_file}: {e}")
    
    def get_existing_topics(self, category: str = None) -> List[str]:
        """Get existing topic titles.
        
        Args:
            category: Optional category filter (pokemon, hockey, soccer)
            
        Returns:
            List of existing topic titles
        """
        if category:
            return self.topics.get(category, [])
        else:
            all_topics = []
            for cat_topics in self.topics.values():
                all_topics.extend(cat_topics)
            return all_topics
    
    def add_topic(self, title: str, category: str) -> bool:
        """Add a new topic.
        
        Args:
            title: Topic title
            category: Category (pokemon, hockey, soccer)
            
        Returns:
            True if added, False if already exists
        """
        if category not in self.topics:
            self.topics[category] = []
        
        if title not in self.topics[category]:
            self.topics[category].append(title)
            self._save_topics()
            logger.info(f"Added topic: {title} ({category})")
            return True
        else:
            logger.info(f"Topic already exists: {title} ({category})")
            return False
    
    def deduplicate_topics(self, new_topics: List[str], category: str = None) -> List[str]:
        """Remove topics that already exist.
        
        Args:
            new_topics: List of new topic candidates
            category: Optional category filter
            
        Returns:
            List of unique topics not in database
        """
        existing = set(self.get_existing_topics(category))
        unique_topics = [topic for topic in new_topics if topic not in existing]
        
        logger.info(f"Filtered {len(new_topics)} topics -> {len(unique_topics)} unique")
        if len(new_topics) > len(unique_topics):
            duplicates = len(new_topics) - len(unique_topics)
            logger.info(f"Removed {duplicates} duplicate topics")
        
        return unique_topics
    
    def get_stats(self) -> Dict[str, int]:
        """Get topic statistics.
        
        Returns:
            Dictionary with topic counts per category
        """
        stats = {}
        for category, topics in self.topics.items():
            stats[category] = len(topics)
        stats['total'] = sum(stats.values())
        return stats


# Global instance
_temp_db = None

def get_temp_database() -> TempTopicDatabase:
    """Get global temporary database instance."""
    global _temp_db
    if _temp_db is None:
        _temp_db = TempTopicDatabase()
    return _temp_db


def deduplicate_topics_temp(topics: List[str], category: str = None) -> List[str]:
    """Convenience function to deduplicate topics using temp database.
    
    Args:
        topics: List of topic candidates
        category: Optional category filter
        
    Returns:
        List of unique topics not in database
    """
    db = get_temp_database()
    return db.deduplicate_topics(topics, category)


def add_topic_temp(title: str, category: str) -> bool:
    """Convenience function to add a topic using temp database.
    
    Args:
        title: Topic title
        category: Category (pokemon, hockey, soccer)
        
    Returns:
        True if added, False if already exists
    """
    db = get_temp_database()
    return db.add_topic(title, category)


if __name__ == "__main__":
    # Test the temporary database
    db = TempTopicDatabase("test_topics.json")
    
    print("Testing temporary topic database...")
    
    # Add some test topics
    db.add_topic("Pikachu Trading Card Analysis", "pokemon")
    db.add_topic("Wayne Gretzky Rookie Card", "hockey")
    db.add_topic("Messi World Cup Cards", "soccer")
    
    # Test deduplication
    test_topics = [
        "Pikachu Trading Card Analysis",  # Duplicate
        "Charizard Market Trends",       # New
        "Wayne Gretzky Rookie Card",     # Duplicate
        "Connor McDavid Cards"           # New
    ]
    
    unique = db.deduplicate_topics(test_topics, "pokemon")
    print(f"Unique Pokemon topics: {unique}")
    
    # Show stats
    stats = db.get_stats()
    print(f"Topic statistics: {stats}")
    
    # Clean up test file
    if Path("test_topics.json").exists():
        os.remove("test_topics.json")
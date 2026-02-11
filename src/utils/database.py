"""Database utility for Neon PostgreSQL connection and operations.

This module provides a simple interface for connecting to Neon PostgreSQL
and performing basic operations for topic management.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
import asyncpg
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class NeonDatabaseClient:
    """Simple client for Neon PostgreSQL database operations."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize the database client.
        
        Args:
            connection_string: PostgreSQL connection string. If None, reads from env.
        """
        self.connection_string = connection_string or os.getenv('NEON_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("NEON_CONNECTION_STRING environment variable is required")
        
        self.pool = None
    
    async def connect(self) -> None:
        """Create connection pool to the database."""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=5,
                command_timeout=30
            )
            logger.info("Connected to Neon database")
        except Exception as e:
            logger.error(f"Failed to connect to Neon database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from Neon database")
            self.pool = None

    async def _ensure_connection(self) -> None:
        """Ensure valid connection pool on the current event loop."""
        should_reconnect = False
        if self.pool:
            try:
                # Check if pool belongs to current loop to avoid "different loop" errors
                current_loop = asyncio.get_running_loop()
                # Accessing _loop is common pattern for this check, though private
                pool_loop = getattr(self.pool, '_loop', None)
                if pool_loop is not None and pool_loop is not current_loop:
                    logger.warning("DB pool loop mismatch detected. Reconnecting...")
                    should_reconnect = True
            except Exception as e:
                logger.warning(f"Error checking pool loop: {e}")
        
        if self.pool is None or should_reconnect:
            # If we need to reconnect, discard the old pool reference
            # We cannot close it nicely if it belongs to a closed loop
            self.pool = None
            await self.connect()
    
    async def execute_migrations(self) -> None:
        """Execute database migrations from the migrations folder."""
        migration_files = [
            "migrations/001_create_topics_table.sql",
            "migrations/002_create_content_table.sql", 
            "migrations/003_create_context_table.sql"
        ]
        
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            for migration_file in migration_files:
                try:
                    if os.path.exists(migration_file):
                        with open(migration_file, 'r', encoding='utf-8') as f:
                            sql = f.read()
                        await conn.execute(sql)
                        logger.info(f"Executed migration: {migration_file}")
                    else:
                        logger.warning(f"Migration file not found: {migration_file}")
                except Exception as e:
                    logger.error(f"Failed to execute migration {migration_file}: {e}")
                    raise
    
    async def get_existing_topics(self, category: Optional[str] = None) -> List[str]:
        """Get list of existing topic titles from database.
        
        Args:
            category: Optional category filter (pokemon, hockey, soccer)
            
        Returns:
            List of existing topic titles
        """
        await self._ensure_connection()
        
        try:
            async with self.pool.acquire() as conn:
                if category:
                    query = "SELECT title FROM topics WHERE category = $1 ORDER BY created_at DESC"
                    rows = await conn.fetch(query, category)
                else:
                    query = "SELECT title FROM topics ORDER BY created_at DESC"
                    rows = await conn.fetch(query)
                
                return [row['title'] for row in rows]
        except Exception as e:
            logger.error(f"Failed to get existing topics: {e}")
            return []
    
    async def save_topic(self, title: str, category: str, source_url: str = None) -> str:
        """Save a new topic to the database.
        
        Args:
            title: Topic title
            category: Category (pokemon, hockey, soccer)
            source_url: Optional source URL
            
        Returns:
            Topic ID (UUID)
        """
        await self._ensure_connection()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO topics (title, category, source_url, status)
                    VALUES ($1, $2, $3, 'pending')
                    ON CONFLICT (title) DO NOTHING
                    RETURNING id
                """
                result = await conn.fetchrow(query, title, category, source_url)
                if result:
                    topic_id = str(result['id'])
                    logger.info(f"Saved topic: {title} (ID: {topic_id})")
                    return topic_id
                else:
                    # Topic already exists, get its ID
                    existing = await conn.fetchrow(
                        "SELECT id FROM topics WHERE title = $1", title
                    )
                    if existing:
                        return str(existing['id'])
                    else:
                        raise Exception(f"Failed to save or find topic: {title}")
        except Exception as e:
            logger.error(f"Failed to save topic {title}: {e}")
            raise
    
    async def update_topic_status(self, topic_id: str, status: str) -> None:
        """Update topic status.
        
        Args:
            topic_id: Topic UUID
            status: New status (pending, in_progress, completed, failed)
        """
        await self._ensure_connection()
        
        try:
            async with self.pool.acquire() as conn:
                query = "UPDATE topics SET status = $1 WHERE id = $2"
                await conn.execute(query, status, topic_id)
                logger.info(f"Updated topic {topic_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update topic status: {e}")
            raise
    
    async def save_content(self, topic_id: str, topic_title: str, category: str, 
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
        await self._ensure_connection()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO content (topic_id, topic_title, category, final_content, 
                                       research_sources, metadata)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                    RETURNING id
                """
                # Convert to JSONB format
                sources_json = json.dumps(research_sources or [])
                metadata_json = json.dumps(metadata or {})
                
                result = await conn.fetchrow(
                    query, topic_id, topic_title, category, final_content,
                    sources_json, metadata_json
                )
                content_id = str(result['id'])
                logger.info(f"Saved content for topic: {topic_title} (ID: {content_id})")
                return content_id
        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self._ensure_connection()
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Convenience functions for synchronous usage
def create_client() -> NeonDatabaseClient:
    """Create a new database client instance."""
    return NeonDatabaseClient()


async def test_database_connection() -> bool:
    """Test database connection and return result."""
    client = create_client()
    try:
        return await client.test_connection()
    finally:
        await client.disconnect()


async def setup_database() -> None:
    """Setup database by running migrations."""
    client = create_client()
    try:
        await client.execute_migrations()
        logger.info("Database setup completed successfully")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    # Test the database connection
    async def main():
        print("Testing Neon database connection...")
        success = await test_database_connection()
        if success:
            print("✅ Database connection successful!")
            print("Setting up database...")
            await setup_database()
            print("✅ Database setup completed!")
        else:
            print("❌ Database connection failed!")
    
    asyncio.run(main())
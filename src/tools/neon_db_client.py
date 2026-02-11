"""Neon database client with Kiro Power integration."""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from src.models.config import Config
from src.models.content import ContentRecord
from src.models.topic import TopicRecord


logger = logging.getLogger(__name__)


class NeonDBClient:
    """Client for interacting with Neon PostgreSQL database via Kiro Power.

    This client provides an abstraction layer over the Neon database,
    handling connection management, retries, and data validation using
    Pydantic models.

    Attributes:
        config: System configuration containing connection details
        connection: Active database connection (None if not connected)
        max_retries: Maximum number of retry attempts for operations
    """

    def __init__(self, config: Config):
        """Initialize Neon database client using Kiro Power.

        Args:
            config: System configuration with database connection details
        """
        self.config = config
        self.connection: Optional[Any] = None
        self.max_retries = config.max_retries
        logger.info("NeonDBClient initialized with Kiro Power: %s", config.kiro_power_name)

    def _connect(self) -> Any:
        """Establish connection to Neon database.

        Returns:
            Database connection object

        Raises:
            psycopg2.Error: If connection fails after all retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                conn = psycopg2.connect(
                    self.config.neon_connection_string,
                    cursor_factory=RealDictCursor
                )
                logger.info("Successfully connected to Neon database")
                return conn
            except psycopg2.Error as e:
                wait_time = 2 ** (attempt - 1)  # Exponential backoff: 1, 2, 4 seconds
                logger.warning(
                    "Connection attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to connect to Neon database after %d attempts", self.max_retries)
                    raise

    def _get_connection(self) -> Any:
        """Get active database connection, creating one if needed.

        Returns:
            Active database connection
        """
        if self.connection is None or self.connection.closed:
            self.connection = self._connect()
        return self.connection

    def verify_connection(self) -> bool:
        """Test connectivity to Neon database via Kiro Power.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Neon database connection verified successfully")
                return result is not None
        except psycopg2.Error as e:
            logger.error("Neon database connection verification failed: %s", str(e))
            return False

    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SQL query through Kiro Power with parameterization.

        Args:
            query: SQL query string with named parameters (e.g., %(param_name)s)
            params: Dictionary of parameter values for the query

        Returns:
            List of result rows as dictionaries

        Raises:
            psycopg2.Error: If query execution fails after all retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                conn = self._get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(query, params or {})

                    # Check if query returns results
                    if cursor.description:
                        results = cursor.fetchall()
                        conn.commit()
                        logger.debug("Query executed successfully, returned %d rows", len(results))
                        return [dict(row) for row in results]
                    else:
                        conn.commit()
                        logger.debug("Query executed successfully, no results returned")
                        return []

            except psycopg2.Error as e:
                if conn:
                    conn.rollback()
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "Query execution attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                    # Reconnect on next attempt
                    self.connection = None
                else:
                    logger.error("Query execution failed after %d attempts", self.max_retries)
                    raise

    def query_all_topics(self) -> List[str]:
        """Retrieve ALL existing topic titles from Neon database.

        This method is used for deduplication during the Strategy Phase
        to ensure no duplicate topics are generated.

        Returns:
            List of topic title strings

        Raises:
            psycopg2.Error: If query fails after all retries
        """
        logger.info("Querying all existing topics from Neon database")
        query = "SELECT title FROM topics ORDER BY created_at DESC"

        try:
            results = self.execute_query(query)
            titles = [row['title'] for row in results]
            logger.info("Retrieved %d existing topics from database", len(titles))
            return titles
        except psycopg2.Error as e:
            logger.error("Failed to query topics: %s", str(e))
            raise

    def create_topic(self, record: TopicRecord) -> UUID:
        """Create a new topic record in Neon database.

        Args:
            record: TopicRecord Pydantic model with validated data

        Returns:
            UUID of the created topic

        Raises:
            psycopg2.Error: If creation fails after all retries
            psycopg2.IntegrityError: If topic title already exists (UNIQUE constraint)
        """
        logger.info("Creating new topic: %s (category: %s)", record.title, record.category)

        query = """
            INSERT INTO topics (id, title, category, created_at, status)
            VALUES (%(id)s, %(title)s, %(category)s, %(created_at)s, %(status)s)
            RETURNING id
        """

        params = {
            'id': str(record.id),
            'title': record.title,
            'category': record.category,
            'created_at': record.created_at,
            'status': record.status
        }

        try:
            results = self.execute_query(query, params)
            topic_id = UUID(results[0]['id'])
            logger.info("Successfully created topic with ID: %s", topic_id)
            return topic_id
        except psycopg2.IntegrityError:
            logger.error("Topic creation failed - duplicate title: %s", record.title)
            raise
        except psycopg2.Error:
            logger.error("Failed to create topic")
            raise

    def create_content(self, record: ContentRecord) -> UUID:
        """Create a new content record in Neon database.

        Args:
            record: ContentRecord Pydantic model with validated data

        Returns:
            UUID of the created content

        Raises:
            psycopg2.Error: If creation fails after all retries
        """
        logger.info(
            "Creating new content for topic: %s (category: %s)",
            record.topic_title, record.category
        )

        query = """
            INSERT INTO content (
                id, topic_id, topic_title, category, final_content,
                research_sources, metadata, created_at, status
            )
            VALUES (
                %(id)s, %(topic_id)s, %(topic_title)s, %(category)s, %(final_content)s,
                %(research_sources)s, %(metadata)s, %(created_at)s, %(status)s
            )
            RETURNING id
        """

        params = {
            'id': str(record.id),
            'topic_id': str(record.topic_id),
            'topic_title': record.topic_title,
            'category': record.category,
            'final_content': record.final_content,
            'research_sources': json.dumps(record.research_sources),
            'metadata': json.dumps(record.metadata),
            'created_at': record.created_at,
            'status': record.status
        }

        try:
            results = self.execute_query(query, params)
            content_id = UUID(results[0]['id'])
            logger.info("Successfully created content with ID: %s", content_id)
            return content_id
        except psycopg2.Error:
            logger.error("Failed to create content")
            raise

    def update_status(self, record_id: UUID, status: str, table: str = 'topics') -> None:
        """Update the status of a record in Neon database.

        Args:
            record_id: UUID of the record to update
            status: New status value
            table: Table name ('topics' or 'content')

        Raises:
            psycopg2.Error: If update fails after all retries
            ValueError: If table name is invalid
        """
        if table not in ('topics', 'content'):
            raise ValueError(f"Invalid table name: {table}. Must be 'topics' or 'content'")

        logger.info("Updating %s status to '%s' for ID: %s", table, status, record_id)

        query = sql.SQL("UPDATE {} SET status = %(status)s WHERE id = %(id)s").format(
            sql.Identifier(table)
        )

        params = {
            'id': str(record_id),
            'status': status
        }

        try:
            self.execute_query(query.as_string(self._get_connection()), params)
            logger.info("Successfully updated %s status", table)
        except psycopg2.Error:
            logger.error("Failed to update %s status", table)
            raise

    def close(self) -> None:
        """Close the database connection.

        This should be called when the client is no longer needed
        to properly release database resources.
        """
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Neon database connection closed")
            self.connection = None

    def __enter__(self) -> 'NeonDBClient':
        """Context manager entry.

        Returns:
            Self for use in with statements
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes connection.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        self.close()

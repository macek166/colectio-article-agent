"""Archivist Agent for storing completed articles in Neon database.

This module implements the Archivist Agent, responsible for persisting
completed articles to the Neon database along with context and metadata.
"""

import logging
import time
from datetime import UTC, datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.agents.editor import EditedArticle
from src.models.content import ContentRecord
from src.utils.topic_manager import get_topic_manager
from src.utils.google_drive_client import create_google_drive_client
from src.utils.context_manager import ContextManager


logger = logging.getLogger(__name__)


class ArchivedContent(BaseModel):
    """Pydantic model for archived content.

    Attributes:
        id: Unique identifier for the archived content
        topic: Topic of the article
        category: Content category (pokemon, hockey, or soccer)
        content: Final article content
        created_at: Timestamp when content was archived
    """

    id: UUID = Field(default_factory=uuid4)
    topic: str = Field(..., min_length=10, max_length=200)
    category: str = Field(..., pattern="^(pokemon|hockey|soccer)$")
    content: str = Field(..., min_length=500)
    created_at: str


class ArchivistAgent:
    """Archivist Agent for storing completed articles in Neon database.

    This agent persists completed articles to the Neon database along
    with context history and metadata. It integrates with NeonDBClient
    for database operations and ContextManager for retrieving the
    complete workflow context.

    Attributes:
        neon_client: Neon database client for persistence
        context_manager: Context manager for retrieving context
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        context_manager: ContextManager,
        max_retries: int = 3,
        enable_google_drive: bool = True
    ):
        """Initialize archivist with Neon database and Google Drive.

        Args:
            context_manager: Context manager for retrieving context
            max_retries: Maximum retry attempts
            enable_google_drive: Whether to enable Google Drive storage
        """
        self.topic_manager = get_topic_manager()
        self.context_manager = context_manager
        self.max_retries = max_retries
        self.enable_google_drive = enable_google_drive
        
        # Initialize Google Drive client if enabled
        self.google_drive_client = None
        if self.enable_google_drive:
            try:
                self.google_drive_client = create_google_drive_client()
                logger.info("Google Drive client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Drive client: {e}")
                self.google_drive_client = None

        logger.info("ArchivistAgent initialized")

    def archive(
        self,
        article: EditedArticle,
        topic: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> ArchivedContent:
        """Store completed article in Neon database.

        This method:
        1. Retrieves the full context history from ContextManager
        2. Creates a ContentRecord with article and metadata
        3. Persists to Neon database with retry logic
        4. Returns ArchivedContent confirmation

        Args:
            article: EditedArticle from Editor Agent
            topic: Topic of the article
            category: Content category (pokemon, hockey, or soccer)
            metadata: Additional metadata about the article

        Returns:
            ArchivedContent with database record ID

        Raises:
            Exception: If archiving fails after all retries
        """
        logger.info("Starting article archiving for topic: %s", topic)

        for attempt in range(1, self.max_retries + 1):
            try:
                # Step 1: Retrieve full context history
                logger.info("Retrieving context history")
                context_history = self.context_manager.get_full_history()

                # Step 2: Extract research sources from context
                research_sources = self._extract_research_sources(context_history)

                # Step 3: Build comprehensive metadata
                full_metadata = self._build_metadata(
                    metadata,
                    context_history,
                    article
                )

                # Step 4: Save topic to Neon database
                logger.info("Saving topic to Neon database")
                topic_id = self.topic_manager.save_topic(topic, category)
                logger.info(f"Topic saved with ID: {topic_id}")

                # Step 5: Create content record (for context)
                logger.info("Creating content record")
                content_record = ContentRecord(
                    id=uuid4(),
                    topic_id=topic_id,
                    topic_title=topic,
                    category=category,
                    final_content=article.content,
                    research_sources=research_sources,
                    metadata=full_metadata,
                    created_at=datetime.now(UTC).isoformat(),
                    status='completed'
                )

                # Step 6: Save content to Neon database
                content_id = self.topic_manager.save_content(
                    topic_id=topic_id,
                    topic_title=topic,
                    category=category,
                    final_content=article.content,
                    research_sources=research_sources,
                    metadata=full_metadata
                )
                logger.info("Content archived to Neon database with ID: %s", content_id)
                
                # Step 7: Upload to Google Drive (if enabled)
                google_drive_file_id = None
                if self.google_drive_client:
                    try:
                        logger.info("Uploading article to Google Drive...")
                        
                        # Prepare metadata for Google Drive
                        drive_metadata = {
                            'category': category,
                            'word_count': len(article.content.split()),
                            'research_sources': research_sources,
                            'neon_content_id': str(content_id),
                            'neon_topic_id': str(topic_id)
                        }
                        
                        # Add SEO keywords if available
                        if 'keywords' in full_metadata:
                            drive_metadata['keywords'] = full_metadata['keywords']
                        
                        # Authenticate and setup folders
                        if self.google_drive_client.authenticate():
                            if self.google_drive_client.setup_article_folders():
                                google_drive_file_id = self.google_drive_client.upload_article(
                                    title=topic,
                                    content=article.content,
                                    category=category,
                                    metadata=drive_metadata
                                )
                                
                                if google_drive_file_id:
                                    logger.info(f"Article uploaded to Google Drive with ID: {google_drive_file_id}")
                                    # Add Google Drive file ID to metadata
                                    full_metadata['google_drive_file_id'] = google_drive_file_id
                                else:
                                    logger.warning("Failed to upload article to Google Drive")
                            else:
                                logger.warning("Failed to setup Google Drive folders")
                        else:
                            logger.warning("Failed to authenticate with Google Drive")
                            
                    except Exception as e:
                        logger.error(f"Google Drive upload failed: {e}")
                        # Don't fail the entire archiving process if Google Drive fails
                
                logger.info("Content archived with ID: %s", content_id)

                # Step 8: Create archived content response
                archived = ArchivedContent(
                    id=content_id,
                    topic=topic,
                    category=category,
                    content=article.content,
                    created_at=content_record.created_at
                )

                # Store in context manager
                self.context_manager.add_context(
                    "ArchivistAgent",
                    archived.model_dump(),
                    metadata={"attempt": attempt, "content_id": str(content_id)}
                )

                logger.info(
                    "Article archiving complete for topic: %s (ID: %s)",
                    topic, content_id
                )

                return archived

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "Archiving attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )

                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Archiving failed after %d attempts for topic: %s",
                        self.max_retries, topic
                    )
                    raise

        # Should never reach here
        raise RuntimeError(f"Archiving failed after all retries for topic: {topic}")

    def _extract_research_sources(self, context_history: list) -> list:
        """Extract research sources from context history.

        Args:
            context_history: List of AgentOutput instances

        Returns:
            List of source URLs
        """
        sources = []

        for agent_output in context_history:
            if agent_output.agent_name == "ResearcherAgent":
                output = agent_output.output
                if isinstance(output, dict):
                    agent_sources = output.get('sources', [])
                    sources.extend(agent_sources)

        # Remove duplicates while preserving order
        seen = set()
        unique_sources = []
        for source in sources:
            if source not in seen:
                seen.add(source)
                unique_sources.append(source)

        logger.info("Extracted %d unique research sources", len(unique_sources))
        return unique_sources

    def _build_metadata(
        self,
        base_metadata: Dict[str, Any],
        context_history: list,
        article: EditedArticle
    ) -> Dict[str, Any]:
        """Build comprehensive metadata for the content record.

        Args:
            base_metadata: Base metadata provided
            context_history: Full context history
            article: Edited article

        Returns:
            Comprehensive metadata dictionary
        """
        metadata = base_metadata.copy()

        # Add article statistics
        metadata['word_count'] = len(article.content.split())
        metadata['improvements_count'] = len(article.improvements)
        metadata['improvements'] = article.improvements

        # Add context statistics
        metadata['agent_executions'] = len(context_history)
        metadata['agents_involved'] = list(set(
            output.agent_name for output in context_history
        ))

        # Add timestamps
        metadata['archived_at'] = datetime.now(UTC).isoformat()

        # Add context history (serialized)
        metadata['context_history'] = [
            {
                'agent': output.agent_name,
                'timestamp': output.timestamp.isoformat(),
                'metadata': output.metadata
            }
            for output in context_history
        ]

        logger.info("Built comprehensive metadata with %d fields", len(metadata))
        return metadata



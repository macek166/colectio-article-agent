"""Orchestrator for managing the two-phase content generation workflow.

This module implements the main Orchestrator class that coordinates the complete
TCG Content Generator workflow:
1. Strategy Phase: Generate unique topics with SEO optimization and deduplication
2. Execution Phase: Create articles sequentially for each topic

The Orchestrator handles error recovery, progress tracking, and logging to
DOCUMENTATION.md and PROBLEMS.md files.
"""

import logging
import time
from typing import Dict, List, Optional, Callable
from uuid import uuid4

from pydantic import BaseModel, Field

from src.agents.content_crew import ContentCrew, ContentCrewResult
from src.agents.strategist import StrategyPhase
from src.config.settings import Config
from src.models.topic import TopicRecord
from src.tools.context7_client import Context7Client
from src.tools.neon_db_client import NeonDBClient
from src.tools.seo_tools import SEOTools
from src.utils.context_manager import ContextManager
from src.utils.documentation_manager import DocumentationManager
from src.utils.documentation_generator import DocumentationGenerator


logger = logging.getLogger(__name__)


class OrchestratorResult(BaseModel):
    """Pydantic model for Orchestrator execution result.

    Attributes:
        total_topics: Total number of topics processed
        successful: Number of successfully completed articles
        failed: Number of failed topics
        topics_generated: List of generated topic strings
        results: List of ContentCrewResult for each topic
        execution_time: Total execution time in seconds
    """

    total_topics: int = Field(default=0, ge=0)
    successful: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    topics_generated: List[str] = Field(default_factory=list)
    results: List[ContentCrewResult] = Field(default_factory=list)
    execution_time: float = Field(default=0.0, ge=0.0)


class Orchestrator:
    """Main orchestrator for the two-phase content generation workflow.

    The Orchestrator coordinates the complete system workflow:
    - Phase 1 (Strategy): Generate unique topics with web research and deduplication
    - Phase 2 (Execution): Create articles sequentially (one at a time)

    It provides:
    - Error recovery with exponential backoff (max 3 retries per topic)
    - Progress tracking and logging
    - Checkpoint pattern for resumability
    - Documentation of all significant events and errors

    Attributes:
        config: System configuration
        neon_client: Neon database client
        context7_client: Context7 MCP client
        seo_tools: SEO and web scraping tools
        doc_manager: Documentation manager
        strategy_phase: Strategy phase instance
    """

    def __init__(
        self,
        config: Config,
        neon_client: NeonDBClient,
        context7_client: Context7Client,
        seo_tools: SEOTools,
        doc_manager: DocumentationManager
    ):
        """Initialize orchestrator with configuration and clients.

        Args:
            config: System configuration
            neon_client: Neon database client for data persistence
            context7_client: Context7 MCP client for documentation
            seo_tools: SEO and web scraping tools
            doc_manager: Documentation manager for logging
        """
        self.config = config
        self.neon_client = neon_client
        self.context7_client = context7_client
        self.seo_tools = seo_tools
        self.doc_manager = doc_manager

        # Initialize Strategy Phase
        self.strategy_phase = StrategyPhase(
            config=config,
            context7_client=context7_client,
            seo_tools=seo_tools,
            doc_manager=doc_manager
        )

        # Generate/update AGENT_STRUCTURE.md documentation
        doc_generator = DocumentationGenerator()
        if not doc_generator.verify_exists():
            logger.info("Generating AGENT_STRUCTURE.md documentation")
            doc_generator.generate()
        
        logger.info("Orchestrator initialized")
        self.doc_manager.log_event(
            "Orchestrator Initialized",
            "Two-phase orchestration system initialized with all components"
        )

    def run(
        self,
        topic_distribution: Optional[Dict[str, int]] = None,
        progress_callback: Optional[Callable[[str, int, int, str], None]] = None
    ) -> OrchestratorResult:
        """Execute the complete two-phase workflow.

        This is the main entry point for the content generation system.
        It orchestrates:
        1. Strategy Phase: Generate unique topics
        2. Execution Phase: Create articles sequentially

        Args:
            topic_distribution: Dict with keys 'pokemon', 'hockey', 'soccer' and int values
            progress_callback: Optional callback(topic, completed, total, category) for UI updates

        Returns:
            OrchestratorResult containing execution summary and results

        Raises:
            Exception: If critical errors occur during execution
        """
        start_time = time.time()

        # Use default distribution if not provided
        if topic_distribution is None:
            topic_distribution = self.config.default_topic_distribution

        logger.info(
            "Starting Orchestrator execution with distribution: %s",
            topic_distribution
        )
        self.doc_manager.log_event(
            "Orchestrator Execution Started",
            f"Topic Distribution: {topic_distribution}"
        )

        try:
            # Phase 1: Strategy Phase - Generate Topics
            logger.info("=" * 60)
            logger.info("PHASE 1: STRATEGY PHASE - TOPIC GENERATION")
            logger.info("=" * 60)

            topics = self._execute_strategy_phase(topic_distribution)

            logger.info(
                "Strategy Phase complete: %d topics generated",
                len(topics)
            )
            self.doc_manager.log_event(
                "Strategy Phase Complete",
                f"Generated {len(topics)} unique topics: {topics}"
            )

            # Phase 2: Execution Phase - Create Articles
            logger.info("=" * 60)
            logger.info("PHASE 2: EXECUTION PHASE - ARTICLE CREATION")
            logger.info("=" * 60)

            results = self._execute_execution_phase(
                topics, 
                topic_distribution, 
                progress_callback
            )

            # Calculate statistics
            successful = sum(1 for r in results if r.success)
            failed = sum(1 for r in results if not r.success)

            execution_time = time.time() - start_time

            logger.info("=" * 60)
            logger.info("ORCHESTRATOR EXECUTION COMPLETE")
            logger.info("=" * 60)
            logger.info("Total Topics Processed: %d", len(results))
            logger.info("Successful: %d", successful)
            logger.info("Failed: %d", failed)
            logger.info("Execution Time: %.2f seconds", execution_time)

            self.doc_manager.log_event(
                "Orchestrator Execution Complete",
                f"Processed: {len(results)}, Successful: {successful}, "
                f"Failed: {failed}, Time: {execution_time:.2f}s"
            )

            # Extract titles for result summary
            topic_titles = [
                t.title if hasattr(t, 'title') else str(t) 
                for t in topics
            ]

            # Build result
            result = OrchestratorResult(
                total_topics=len(results),
                successful=successful,
                failed=failed,
                topics_generated=topic_titles,
                results=results,
                execution_time=execution_time
            )

            return result

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Orchestrator execution failed: %s", str(e))
            self.doc_manager.log_problem(
                "Orchestrator Execution Failed",
                "active",
                f"Critical error during execution: {str(e)}"
            )
            raise

    def _execute_strategy_phase(
        self,
        distribution: Dict[str, int]
    ) -> List[str]:
        """Execute Phase 1: Topic generation with web research and deduplication.

        This method:
        1. Queries Neon database for existing topics BEFORE generation
        2. Uses SEO tools to gather insights
        3. Scrapes category-specific web sources
        4. Generates topic candidates using OpenAI
        5. Deduplicates against existing topics
        6. Returns JSON-serializable list of topic strings

        Args:
            distribution: Dict with 'pokemon', 'hockey', 'soccer' counts

        Returns:
            List of unique topic strings

        Raises:
            Exception: If strategy phase fails after all retries
        """
        logger.info("Executing Strategy Phase with distribution: %s", distribution)

        for attempt in range(1, self.config.max_retries + 1):
            try:
                # Generate topics using Strategy Phase
                # Generate EXTRA candidates (2x buffer) to allow discarding weak/invalid topics
                # without falling short of the target count.
                augmented_dist = {k: v * 2 for k, v in distribution.items()}
                topics = self.strategy_phase.generate_topics(augmented_dist)

                logger.info(
                    "Strategy Phase successful: %d topics generated",
                    len(topics)
                )

                # Store topics in database for checkpoint
                self._store_topics_checkpoint(topics, distribution)

                return topics

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "Strategy Phase attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.config.max_retries, str(e), wait_time
                )

                self.doc_manager.log_problem(
                    f"Strategy Phase Attempt {attempt} Failed",
                    "active",
                    f"Error: {str(e)}"
                )

                if attempt < self.config.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Strategy Phase failed after %d attempts",
                        self.config.max_retries
                    )
                    self.doc_manager.log_problem(
                        "Strategy Phase Failed",
                        "active",
                        f"Failed after {self.config.max_retries} attempts. "
                        f"Last error: {str(e)}"
                    )
                    raise

        # Should never reach here
        raise RuntimeError("Strategy Phase failed after all retries")

    def _execute_execution_phase(
        self,
        topics: List[str],
        distribution: Dict[str, int],
        progress_callback: Optional[Callable[[str, int, int, str], None]] = None
    ) -> List[ContentCrewResult]:
        """Execute Phase 2: Sequential article creation with Goal-Oriented Retry.

        This method processes topics candidates until the TARGET COUNT (distribution)
        is met for each category. It uses the buffer topics generated in Phase 1
        as backups if a topic is rejected.

        Args:
            topics: List of topic candidates (including buffer)
            distribution: Target count per category
            progress_callback: Optional callback for UI updates

        Returns:
            List of ContentCrewResult for processed topics
        """
        target_total = sum(distribution.values())
        logger.info(
            "Executing Execution Phase. Candidates: %d. Target Successes: %d",
            len(topics), target_total
        )

        results: List[ContentCrewResult] = []
        success_counts = {k: 0 for k in distribution}
        
        # Track topics processed count for UI
        processed_count = 0

        # Process topics sequentially
        for index, topic in enumerate(topics, start=1):
            
            # Check if we have met all targets
            current_total_success = sum(success_counts.values())
            if current_total_success >= target_total:
                logger.info("All article targets met! Stopping execution phase.")
                break

            # Extract topic details
            if hasattr(topic, 'title'):
                topic_title = topic.title
                writing_style = str(getattr(topic, 'writing_style', 'investor'))
                category = getattr(topic, 'category', 'pokemon')
                # Extract source_url and cached_content
                sources_list = getattr(topic, 'sources', [])
                source_url = sources_list[0] if sources_list and len(sources_list) > 0 else None
                cached_content = getattr(topic, 'cached_content', None)
                
                # Anti-Hallucination Check
                if source_url and ("example.com" in source_url or "test.com" in source_url):
                    logger.warning(f"⚠️ Skipping hallucinated/placeholder source URL: {source_url}")
                    continue
            else:
                topic_title = str(topic)
                writing_style = 'investor'
                category = 'pokemon' # Fallback
                source_url = None
                cached_content = None

            # SKIP if quota for this category is full
            if success_counts.get(category, 0) >= distribution.get(category, 0):
                logger.info(
                    "Skipping topic '%s' - Quota met for category '%s' (%d/%d)",
                    topic_title, category, success_counts.get(category, 0), distribution.get(category, 0)
                )
                continue

            processed_count += 1
            
            logger.info("=" * 60)
            logger.info(
                "Attempt %d (Target %d/%d): %s (Style: %s, Cat: %s)",
                processed_count, current_total_success + 1, target_total, 
                topic_title, writing_style, category
            )
            logger.info("=" * 60)

            try:
                # Notify progress
                # We show 'processed_count' as current step, but 'len(topics)' as max potential steps
                # This shows the user we are "working through" the candidates
                if progress_callback:
                    try:
                        status_msg = f"Candidate {processed_count}/{len(topics)}. Researching global sources (EN, DE, ES, IT)..."
                        progress_callback(topic_title, current_total_success, target_total, category, status_msg)
                    except Exception as e:
                        logger.warning(f"Progress callback failed: {e}")

                # Create fresh context manager for this topic
                context_manager = ContextManager()

                # Instantiate ContentCrew
                content_crew = ContentCrew(
                    topic=topic_title,
                    category=category,
                    context_manager=context_manager,
                    neon_client=self.neon_client,
                    context7_client=self.context7_client,
                    seo_tools=self.seo_tools,
                    config=self.config,
                    doc_manager=self.doc_manager,
                    writing_style=writing_style,
                    source_url=source_url,
                    source_content=cached_content
                )

                # Define granular update wrapper
                def update_status_wrapper(msg):
                    if progress_callback:
                        try:
                            # Keep the header info (Candidate X/Y) but update the status message
                            header = f"Candidate {processed_count}/{len(topics)}"
                            full_msg = f"{header}: {msg}"
                            progress_callback(topic_title, current_total_success, target_total, category, full_msg)
                        except Exception:
                            pass

                # Execute ContentCrew
                result = content_crew.execute(
                    max_retries=self.config.max_retries,
                    status_callback=update_status_wrapper
                )
                results.append(result)

                # Rate limit protection (Wait 5s between articles)
                if index < len(topics):
                    logger.info("Waiting 5s for API rate limits to recover...")
                    time.sleep(5)

                if result.success:
                    success_counts[category] += 1
                    logger.info(
                        "SUCCESS: Created article for '%s' (%s: %d/%d)",
                        topic_title, category, success_counts[category], distribution.get(category, 0)
                    )
                    self.doc_manager.log_event(
                        f"Topic Completed: {topic_title}",
                        f"Success ({category}). Count: {success_counts[category]}/{distribution.get(category, 0)}"
                    )
                else:
                    logger.warning(
                        "FAILED: Could not create article for '%s'. Trying next candidate...",
                        topic_title
                    )

            except Exception as e:
                logger.error("Unexpected critical error processing topic %s: %s", topic_title, e)
                results.append(ContentCrewResult(
                    topic=topic_title,
                    article="",
                    metadata={'error': str(e)},
                    success=False
                ))

        logger.info("Execution Phase complete. Successes: %s / Targets: %s", success_counts, distribution)
        return results

    def _store_topics_checkpoint(
        self,
        topics: List[str],
        distribution: Dict[str, int]
    ) -> None:
        """Store generated topics in database for checkpoint/resumability.

        This method creates topic records in the database with 'pending' status,
        allowing the system to resume from this checkpoint if needed.

        Args:
            topics: List of generated topic strings or TopicCandidate objects
            distribution: Topic distribution used for generation
        """
        logger.info("Storing topics checkpoint in database")

        for topic in topics:
            # Handle TopicCandidate object vs string
            if hasattr(topic, 'title'):
                topic_title = topic.title
                # TRUST THE TOPIC OBJECT'S CATEGORY
                category = getattr(topic, 'category', 'pokemon')
            else:
                topic_title = str(topic)
                # Fallback: Default to pokemon if no metadata available
                # (This should rarely happen given Strategist implementation)
                category = 'pokemon'
                logger.warning(
                    "Topic '%s' lacks metadata. Defaulting category to '%s'.", 
                    topic_title, category
                )

            try:
                # Create topic record
                topic_record = TopicRecord(
                    id=uuid4(),
                    title=topic_title,
                    category=category,
                    created_at=time.strftime('%Y-%m-%d %H:%M:%S'),
                    status='pending'
                )

                # Store in database
                self.neon_client.create_topic(topic_record)

                logger.debug("Stored topic checkpoint: %s (%s)", topic_title, category)

            except Exception as e:  # pylint: disable=broad-except
                # Log but don't fail - checkpoint is optional
                logger.warning(
                    "Failed to store topic checkpoint for '%s': %s",
                    topic_title, str(e)
                )

        logger.info(
            "Topics checkpoint stored: %d topics across categories",
            len(topics)
        )


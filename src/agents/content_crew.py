"""ContentCrew for orchestrating article creation pipeline.

This module implements the ContentCrew class, which coordinates all five agents
(Researcher, Writer, Editor, Archivist) to create a complete article for a single
topic. It includes retry logic, error handling, and context management.
"""

import logging
import time
from typing import Any, Dict

from pydantic import BaseModel, Field

from src.agents.archivist import ArchivistAgent
from src.agents.editor import EditorAgent
from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent
from src.config.settings import Config
from src.tools.context7_client import Context7Client
from src.tools.neon_db_client import NeonDBClient
from src.tools.seo_tools import SEOTools
from src.utils.context_manager import ContextManager
from src.utils.documentation_manager import DocumentationManager


logger = logging.getLogger(__name__)


class ContentCrewResult(BaseModel):
    """Pydantic model for ContentCrew result.

    Attributes:
        topic: Topic that was processed
        article: Final article content
        metadata: Additional metadata about the execution
        success: Whether the execution was successful
        retry_count: Number of retry attempts made
    """

    topic: str = Field(..., min_length=10, max_length=200)
    article: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = Field(default=False)
    retry_count: int = Field(default=0, ge=0)


class ContentCrew:
    """ContentCrew for orchestrating article creation pipeline.

    This class coordinates all five agents to create a complete article
    for a single topic. It manages the execution pipeline, handles errors,
    implements retry logic, and maintains context throughout the workflow.

    The pipeline executes in sequence:
    1. Research → Gather information from category-specific sources
    2. Write → Generate draft article based on research
    3. Edit → Refine and optimize the draft
    4. Archive → Store completed article in Neon database

    Attributes:
        topic: Topic to process
        category: Content category (pokemon, hockey, or soccer)
        context_manager: Context manager for agent communication
        neon_client: Neon database client for persistence
        context7_client: Context7 MCP client for documentation
        seo_tools: SEO and web scraping tools
        config: System configuration
        doc_manager: Documentation manager for logging
        researcher: Researcher agent instance
        writer: Writer agent instance
        editor: Editor agent instance
        archivist: Archivist agent instance
    """

    def __init__(
        self,
        topic: str,
        category: str,
        context_manager: ContextManager,
        neon_client: NeonDBClient,
        context7_client: Context7Client,
        seo_tools: SEOTools,
        config: Config,
        doc_manager: DocumentationManager,
        writing_style: str = "investor",
        source_url: str = None,
        source_content: str = None # NEW: Pre-fetched content
    ):
        """Initialize ContentCrew for a specific topic."""
        self.topic = topic
        self.category = category
        self.context_manager = context_manager
        self.neon_client = neon_client
        self.context7_client = context7_client
        self.seo_tools = seo_tools
        self.config = config
        self.doc_manager = doc_manager
        self.writing_style = writing_style
        self.source_url = source_url
        self.source_content = source_content


        # Agent instances (initialized in _setup_agents)
        self.researcher = None
        self.writer = None
        self.editor = None
        self.archivist = None

        logger.info(
            "ContentCrew initialized for topic: %s (category: %s)",
            topic, category
        )

    def execute(self, max_retries: int = 3, status_callback=None) -> ContentCrewResult:
        """Execute the complete article creation pipeline with retry logic.

        This method orchestrates the entire workflow:
        1. Sets up all five agents
        2. Runs the pipeline (Research → Write → Edit → Archive)
        3. Handles errors with exponential backoff retry
        4. Logs failures to PROBLEMS.md after max retries
        5. Clears context after completion

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            status_callback: Optional function(msg) to report progress

        Returns:
            ContentCrewResult with article and metadata

        Raises:
            Exception: If execution fails after all retries
        """
        logger.info(
            "Starting ContentCrew execution for topic: %s (max_retries: %d)",
            self.topic, max_retries
        )

        # Log event to documentation
        self.doc_manager.log_event(
            f"ContentCrew Execution Started: {self.topic}",
            f"Category: {self.category}, Style: {self.writing_style}, Max Retries: {max_retries}"
        )

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "ContentCrew attempt %d/%d for topic: %s",
                    attempt, max_retries, self.topic
                )

                # Step 1: Setup agents
                if status_callback:
                    status_callback(f"Setting up agents (Attempt {attempt})...")
                logger.info("Setting up agents")
                self._setup_agents()

                # Step 2: Run pipeline
                logger.info("Running article creation pipeline")
                result_data = self._run_pipeline(status_callback)

                # Step 3: Create success result
                result = ContentCrewResult(
                    topic=self.topic,
                    article=result_data.get('article', ''),
                    metadata=result_data.get('metadata', {}),
                    success=True,
                    retry_count=attempt - 1  # Number of retries before success
                )

                # Log success
                logger.info(
                    "ContentCrew execution successful for topic: %s (attempt %d)",
                    self.topic, attempt
                )

                self.doc_manager.log_event(
                    f"ContentCrew Execution Successful: {self.topic}",
                    f"Completed on attempt {attempt}/{max_retries}"
                )

                # Clear context after successful completion
                logger.info("Clearing context after successful completion")
                self.context_manager.clear()

                return result

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "ContentCrew attempt %d/%d failed for topic: %s. Error: %s",
                    attempt, max_retries, self.topic, str(e)
                )
                
                if status_callback:
                     status_callback(f"⚠️ Error encountered: {str(e)}. Retrying in {wait_time}s...")

                if attempt < max_retries:
                    logger.info("Retrying in %d seconds...", wait_time)
                    time.sleep(wait_time)
                else:
                    # Max retries exceeded - log to PROBLEMS.md
                    logger.error(
                        "ContentCrew failed after %d attempts for topic: %s",
                        max_retries, self.topic
                    )
                    
                    if status_callback:
                        status_callback(f"❌ Failed after {max_retries} attempts. See logs.")

                    self.doc_manager.log_problem(
                        f"ContentCrew Failed: {self.topic}",
                        "active",
                        f"Failed after {max_retries} attempts. "
                        f"Category: {self.category}. "
                        f"Error: {str(e)}"
                    )

                    # Clear context after failure
                    logger.info("Clearing context after failure")
                    self.context_manager.clear()

                    # Return failure result
                    return ContentCrewResult(
                        topic=self.topic,
                        article="",
                        metadata={
                            'error': str(e),
                            'category': self.category,
                            'attempts': max_retries
                        },
                        success=False,
                        retry_count=max_retries
                    )

        # Should never reach here
        raise RuntimeError(
            f"ContentCrew execution failed after all retries for topic: {self.topic}"
        )


    def _setup_agents(self) -> None:
        """Initialize all five agents with proper configuration.

        This method creates instances of:
        - ResearcherAgent: For gathering information
        - WriterAgent: For drafting articles
        - EditorAgent: For refining content
        - ArchivistAgent: For storing completed articles

        Note: The Strategist agent is not part of ContentCrew as it operates
        in the Strategy Phase before ContentCrew instantiation.
        """
        logger.info("Initializing agents for ContentCrew")

        # Initialize Researcher Agent
        self.researcher = ResearcherAgent(
            context_manager=self.context_manager,
            context7_client=self.context7_client,
            seo_tools=self.seo_tools,
            config=self.config
        )
        logger.info("ResearcherAgent initialized")

        # Initialize Writer Agent
        self.writer = WriterAgent(
            context_manager=self.context_manager,
            context7_client=self.context7_client,
            config=self.config
        )
        logger.info("WriterAgent initialized")

        # Initialize Editor Agent
        self.editor = EditorAgent(
            context_manager=self.context_manager,
            context7_client=self.context7_client,
            config=self.config
        )
        logger.info("EditorAgent initialized")

        # Initialize Archivist Agent
        self.archivist = ArchivistAgent(
            context_manager=self.context_manager
        )
        logger.info("ArchivistAgent initialized")

        logger.info("All agents initialized successfully")

    def _run_pipeline(self, status_callback=None) -> Dict[str, Any]:
        """Execute agents in sequence: Research → Write → Edit → Archive.

        This method runs the complete article creation pipeline:
        1. Research: Gather information from category-specific sources
        2. Write: Generate draft article based on research
        3. Edit: Refine and optimize the draft
        4. Archive: Store completed article in Neon database

        Returns:
            Dictionary containing:
                - article: Final article content
                - metadata: Execution metadata including agent outputs

        Raises:
            Exception: If any agent fails during execution
        """
        logger.info("Starting pipeline execution for topic: %s", self.topic)

        # Step 1: Research
        logger.info("Step 1/4: Research phase")
        if status_callback:
            status_callback("Agent: RESEARCHER (Gathering data...)")
            
        research_result = self.researcher.research(
            self.topic, 
            self.category, 
            status_callback, 
            active_url=self.source_url,
            source_content=self.source_content
        )
        
        logger.info(
            "Research complete: %d sources, %d insights",
            len(research_result.sources), len(research_result.investment_insights)
        )

        # Step 2: Write
        logger.info("Step 2/4: Writing phase (Style: %s)", self.writing_style)
        if status_callback:
            status_callback("Agent: WRITER (Drafting article based on findings...)")
            
        draft_article = self.writer.write(
            self.topic, 
            research_result,
            writing_style=self.writing_style
        )
        logger.info("Draft complete: %d words", draft_article.word_count)

        # Step 3: Edit
        logger.info("Step 3/4: Editing phase")
        if status_callback:
            status_callback("Agent: EDITOR (Refining style and tone...)")
            
        edited_article = self.editor.edit(draft_article, self.topic)
        logger.info(
            "Editing complete: %d improvements",
            len(edited_article.improvements)
        )

        # Step 4: Archive
        logger.info("Step 4/4: Archiving phase")
        if status_callback:
            status_callback("Agent: ARCHIVIST (Saving to NeonDB & Drive...)")
            
        archived_content = self.archivist.archive(
            article=edited_article,
            topic=self.topic,
            category=self.category,
            metadata={
                'research_sources_count': len(research_result.sources),
                'investment_insights_count': len(research_result.investment_insights),
                'seo_keywords_count': len(research_result.seo_keywords),
                'draft_word_count': draft_article.word_count,
                'improvements_count': len(edited_article.improvements)
            }
        )
        logger.info("Archiving complete: ID %s", archived_content.id)

        # Build result
        result = {
            'article': edited_article.content,
            'metadata': {
                'topic': self.topic,
                'category': self.category,
                'writing_style': self.writing_style,
                'content_id': str(archived_content.id),
                'research_sources': research_result.sources,
                'seo_keywords': research_result.seo_keywords,
                'investment_insights': research_result.investment_insights,
                'draft_word_count': draft_article.word_count,
                'improvements': edited_article.improvements,
                'archived_at': archived_content.created_at
            }
        }

        logger.info("Pipeline execution complete for topic: %s", self.topic)
        return result

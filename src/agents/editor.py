"""Editor Agent for refining and optimizing article content.

This module implements the Editor Agent, responsible for refining
draft articles for clarity, investment insights, and SEO optimization
using OpenAI API and Context7 MCP for style guidelines.
"""

import logging
import time
import datetime
from typing import List

import openai
from pydantic import BaseModel, Field

from src.agents.writer import DraftArticle
from src.config.settings import Config
from src.tools.context7_client import Context7Client
from src.utils.context_manager import ContextManager
from src.utils.llm_client import get_llm_client


logger = logging.getLogger(__name__)


class EditedArticle(BaseModel):
    """Pydantic model for edited article.

    Attributes:
        topic: The topic of the article
        content: The edited article content
        improvements: List of improvements made during editing
    """

    topic: str = Field(..., min_length=10, max_length=200)
    content: str = Field(..., min_length=500)
    improvements: List[str] = Field(default_factory=list)


class EditorAgent:
    """Editor Agent for refining and optimizing article content.

    This agent uses OpenAI API to refine draft articles for clarity,
    investment insights, and SEO optimization. It integrates with
    Context Manager to access the draft and Context7 MCP for style
    guidelines.

    Attributes:
        context_manager: Context manager for accessing draft
        context7_client: Context7 MCP client for style guidelines
        config: System configuration
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        context_manager: ContextManager,
        context7_client: Context7Client,
        config: Config
    ):
        """Initialize editor with context and Context7.

        Args:
            context_manager: Context manager for accessing draft
            context7_client: Context7 MCP client for documentation
            config: System configuration
        """
        self.context_manager = context_manager
        self.context7_client = context7_client
        self.config = config
        self.max_retries = config.max_retries
        self.llm_client = get_llm_client(config)

        logger.info("EditorAgent initialized")

    def edit(self, draft: DraftArticle, topic: str) -> EditedArticle:
        """Refine and optimize the draft article.

        This method:
        1. Retrieves Context7 documentation for style guidelines
        2. Builds an editing prompt with the draft content
        3. Uses OpenAI API to refine the article
        4. Identifies improvements made
        5. Validates and returns the edited article

        Args:
            draft: DraftArticle from Writer Agent
            topic: Topic of the article

        Returns:
            EditedArticle with refined content

        Raises:
            Exception: If editing fails after all retries
        """
        logger.info("Starting article editing for topic: %s", topic)

        for attempt in range(1, self.max_retries + 1):
            try:
                # Step 1: Get Context7 documentation for style guidelines
                logger.info("Retrieving style guidelines from Context7")
                style_guidelines = self._get_style_guidelines()

                # Step 2: Build editing prompt
                logger.info("Building article editing prompt")
                prompt = self._build_editing_prompt(
                    draft,
                    topic,
                    style_guidelines
                )

                # Step 3: Edit article using OpenAI
                logger.info("Editing article with OpenAI API")
                edited_content, improvements = self._edit_article_with_openai(prompt)

                # Step 4: Create and validate edited article
                edited = EditedArticle(
                    topic=topic,
                    content=edited_content,
                    improvements=improvements
                )

                # Store in context manager
                self.context_manager.add_context(
                    "EditorAgent",
                    edited.model_dump(),
                    metadata={
                        "attempt": attempt,
                        "improvements_count": len(improvements)
                    }
                )

                logger.info(
                    "Article editing complete for topic: %s (%d improvements)",
                    topic, len(improvements)
                )

                return edited

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "Editing attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )

                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Editing failed after %d attempts for topic: %s",
                        self.max_retries, topic
                    )
                    raise

        # Should never reach here
        raise RuntimeError(f"Editing failed after all retries for topic: {topic}")

    def _get_style_guidelines(self) -> str:
        """Get style guidelines from Context7.

        Returns:
            Style guidelines string (empty if unavailable)
        """
        try:
            # Try to get editorial style documentation
            lib_id = self.context7_client.resolve_library("editorial-style")
            if lib_id:
                docs = self.context7_client.get_docs(
                    lib_id,
                    topic="investment content editing",
                    mode="info"
                )
                logger.info("Retrieved style guidelines (%d chars)", len(docs))
                return docs

            logger.info("Style guidelines not available, using defaults")
            return ""

        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to get style guidelines: %s", str(e))
            return ""

    def _build_editing_prompt(
        self,
        draft: DraftArticle,
        topic: str,
        style_guidelines: str
    ) -> str:
        """Build prompt for OpenAI article editing.

        Args:
            draft: Draft article to edit
            topic: Topic of the article
            style_guidelines: Style guidelines

        Returns:
            Formatted prompt string
        """
        current_date_str = datetime.date.today().strftime("%Y-%m-%d")

        prompt = f"""You are a ruthless Senior Editor for a premium trading card magazine.
Current Date: {current_date_str}.

Your job is to polish the article into a masterpiece.

Edit and refine the following draft article about: {topic}

CORE EDITING PHILOSOPHY:
1. **EXPAND & DEEPEN**: If the article is short (< 800 words), you MUST expand it. Add details, explanations, and context. Aim for 1000+ words.
2. **ENFORCE COHERENCE**: Ensure every paragraph logically leads to the next. Connect thoughts using transitions.
3. **MAXIMIZE FACT DENSITY**: If a section is generic, refine the phrasing to be more precise.
4. **KILL SENTIMENTALITY**: Remove "magical", "nostalgic tears", "childhood memories". Make it sound professional.
5. **HUMANIZE THE TONE**: It should sound like a smart person talking to a smart friend.

═══════════════════════════════════════════════════════════════
MANDATORY FIXES & VALIDATION (CHECKLIST)
═══════════════════════════════════════════════════════════════

CRITICAL: TOPIC & CATEGORY VERIFICATION
- **PHYSICAL CARDS ONLY**: If this article is about a video game (NHL 24, FIFA), digital cards, or anything other than PHYSICAL trading cards, you MUST REJECT IT by starting your response with "REJECTED: Topic mismatch - [Reason]".
- **TOPIC MATCH**: Does the title and content match the requested topic: {topic}? If it's about a different subject, REJECT IT.
- **CATEGORY MATCH**: Ensure it's about physical cards from the correct category.

A. **NO FINANCIAL ADVICE / PRICES**: 
   - DELETE any mention of "Investment", "ROI", "Profit", "Buy now".
   - DELETE any specific prices ($100, 5000 Kč).

B. **REMOVE DEMONSTRATIVES**: 
   - ELIMINATE "Tato karta", "Tento set", "Tyto důvody". 
   - Rewrite using specific names or implicit subjects.

C. **FACT CHECK & SPECIFICITY**:
   - Verify that set names look real.
   - If the text says "Many variations exist", CHANGE IT TO "Variations include Red, Blue, and Gold parallels..." (be specific!).

D. **LENGTH & SUBSTANCE**:
   - Do NOT just shorten the article. If you cut fluff, REPLACE it with substance (facts, history, mechanics).
   - Aim for 1000+ words of QUALITY.

E. **TITLE & HEADINGS**:
   - Ensure headings are creative (Not "Introduction", "Conclusion").
   - Ensure Professional Headings (Auto-capitalized or Title Case as appropriate).
   - Use Markdown H2 (##) or H3 (###).

DRAFT ARTICLE CONTENT:
{draft.content}

OUTPUT FORMAT:
Return the response in this EXACT text format:

[IMPROVEMENTS]
- Improvement 1
- Improvement 2
...

[ARTICLE]
# Title
... full article content ...

Edit the article now in CZECH language using the format above:"""

        return prompt

    def _edit_article_with_openai(self, prompt: str) -> tuple[str, List[str]]:
        """Edit article using OpenAI API.

        Args:
            prompt: Formatted prompt for OpenAI

        Returns:
            Tuple of (edited_content, improvements_list)

        Raises:
            Exception: If OpenAI API call fails after retries
        """
        logger.info("Calling OpenAI API for article editing")

        for attempt in range(1, self.max_retries + 1):
            try:
                # Use unified LLM client
                content = self.llm_client.call(
                    system_prompt="You are an expert editor with deep knowledge of "
                                 "investment content and trading card markets. "
                                 "You edit exclusively for a Czech audience. "
                                 "You MUST ensure the output is in CZECH language (Čeština).",
                    user_prompt=prompt,
                    temperature=self.config.agent_temperature * 0.8  # Lower temp for editing
                )

                # Check for explicit rejection
                if content.strip().startswith("REJECTED"):
                    logger.error("Article REJECTED by Editor: %s", content)
                    raise ValueError(f"Article REJECTED by Editor: {content}")

                # Parse Text Block Response
                try:
                    # Clean markdown code blocks if present
                    clean_text = content.replace("```json", "").replace("```markdown", "").replace("```", "").strip()
                    
                    if "[ARTICLE]" in clean_text:
                        parts = clean_text.split("[ARTICLE]")
                        
                        # Extract Improvements
                        imp_section = parts[0].replace("[IMPROVEMENTS]", "").strip()
                        improvements = [line.strip("- *").strip() for line in imp_section.split('\n') if line.strip()]
                        
                        # Extract Article
                        edited_content = parts[1].strip()
                    else:
                        # Fallback: Handle missing [ARTICLE] tag
                        if "[IMPROVEMENTS]" in clean_text:
                            # Try to find where the article starts (usually with a Markdown header)
                            import re
                            # Look for first H1 or H2 header after improvements
                            match = re.search(r'\n#+\s', clean_text)
                            if match:
                                split_idx = match.start()
                                imp_part = clean_text[:split_idx]
                                edited_content = clean_text[split_idx:].strip()
                                improvements = [line.strip("- *").strip() for line in imp_part.replace("[IMPROVEMENTS]", "").split('\n') if line.strip()]
                            else:
                                # Can't find clear start, just use clean_text but warn
                                logger.warning("Could not separate improvements from article content")
                                edited_content = clean_text
                                improvements = ["Parsing execution warning"]
                        else:
                            # Assume whole text is the article
                            edited_content = clean_text
                            improvements = ["Refined flow and clarity (Auto-detected)"]

                    # Validate
                    if not edited_content or len(edited_content) < 500:
                        raise ValueError("Edited content too short or missing")

                    logger.info(
                        "Successfully edited article (%d chars, %d improvements)",
                        len(edited_content), len(improvements)
                    )
                    return edited_content, improvements

                except Exception as parse_error:
                    logger.warning("Failed to parse response: %s", str(parse_error))
                    # Fallback returns content as is
                    return content, ["Parsed failed - Raw content returned"]

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)
                logger.warning(
                    "OpenAI API attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )

                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Failed to edit article with OpenAI after %d attempts",
                        self.max_retries
                    )
                    raise

        # Should never reach here
        raise RuntimeError("Article editing failed after all retries")

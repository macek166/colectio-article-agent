"""Writer Agent for generating investment-focused draft articles.

This module implements the Writer Agent, responsible for generating
investment-focused draft articles based on research findings using
OpenAI API and Context7 MCP for best practices.
"""

import logging
import time
import datetime
import json
from typing import List, Dict, Any, Optional

import openai
from pydantic import BaseModel, Field

from src.agents.researcher import ResearchResult
from src.config.settings import Config
from src.config.writing_styles import get_all_styles
from src.tools.context7_client import Context7Client
from src.utils.context_manager import ContextManager
from src.utils.llm_client import get_llm_client


logger = logging.getLogger(__name__)


class DraftArticle(BaseModel):
    """Pydantic model for draft article.

    Attributes:
        topic: The topic of the article
        content: The draft article content
        word_count: Number of words in the content
    """

    topic: str = Field(..., min_length=10, max_length=200)
    content: str = Field(..., min_length=500)
    word_count: int = Field(default=0, ge=0)

    @classmethod
    def create(cls, topic: str, content: str) -> 'DraftArticle':
        """Create a DraftArticle with automatic word count calculation.
        
        Args:
            topic: The topic of the article
            content: The draft article content
            
        Returns:
            DraftArticle instance with calculated word count
        """
        word_count = len(content.split())
        return cls(topic=topic, content=content, word_count=word_count)


class WriterAgent:
    """Writer Agent for generating investment-focused draft articles.

    This agent uses OpenAI API to generate draft articles based on
    research findings. It integrates with Context Manager to access
    research data and Context7 MCP for writing best practices.

    Attributes:
        context_manager: Context manager for accessing research
        context7_client: Context7 MCP client for best practices
        config: System configuration
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        context_manager: ContextManager,
        context7_client: Context7Client,
        config: Config
    ):
        """Initialize writer with context and Context7.

        Args:
            context_manager: Context manager for accessing research
            context7_client: Context7 MCP client for documentation
            config: System configuration
        """
        self.context_manager = context_manager
        self.context7_client = context7_client
        self.config = config
        self.max_retries = config.max_retries
        self.llm_client = get_llm_client(config)

        logger.info("WriterAgent initialized")

    def write(
        self,
        topic: str,
        research: ResearchResult,
        writing_style: str = "investor"
    ) -> DraftArticle:
        """Generate draft article in single shot to ensure completion."""
        logger.info("Starting single-shot article generation for: %s", topic)
        
        # Get guidelines and style
        writing_guidelines = self._get_writing_guidelines()
        styles = get_all_styles()
        style = styles.get(writing_style, styles.get("investor"))
        
        # Get the ORIGINAL source text (this is the main input!)
        original_text = getattr(research, "original_source_text", "")
        research_summary = getattr(research, "detailed_summary", "")
        
        # Use original text if available, otherwise fall back to summary
        source_content_for_prompt = original_text if original_text and len(original_text) > 200 else research_summary
        
        if not source_content_for_prompt or len(source_content_for_prompt) < 100:
            source_content_for_prompt = "\n".join(f"- {point}" for point in research.key_points)
        
        # Get master source URL
        master_source_url = "N/A"
        if research.sources:
            master_source_url = research.sources[0]
        
        # Build comprehensive single prompt with STRICT source-based instructions
        prompt = f"""You are an expert Czech editor and translator for a TRADING CARD magazine.

**MASTER SOURCE URL:** {master_source_url}
        
**ASSIGNMENT:** TRANSLATE AND ADAPT the original English article below into a high-quality Czech article.

⚠️ ABSOLUTE RULES - YOU MUST FOLLOW THESE:
1. **TRANSLATE THE SOURCE ONLY**: Your article must be based 100% on the source text below. 
2. **DO NOT INVENT CONTENT**: Never add information that is not in the source.
3. **PRESERVE THE SOURCE'S INTRO**: The source article's introduction is your introduction. Translate it.
4. **PRESERVE THE SOURCE'S CONCLUSION**: The source's conclusion is your conclusion. Translate it.
5. **NO GENERIC HISTORY**: Do NOT write generic "history of Pokemon/Hockey/Soccer cards" - stick to what the source says.
6. **PUT SOURCE URL AT TOP**: Your article must start with "**Původní zdroj:** {master_source_url}"

❌ FORBIDDEN:
- Do NOT invent statistics or facts not in the source
- Do NOT add "history and origins" unless the source discusses it
- Do NOT generate placeholder content
- Do NOT write generic introductions about "the world of collecting"

✅ REQUIRED:
- Translate the source article faithfully
- Adapt the language to be natural Czech
- Keep the same structure as the source
- Focus on trading cards, collectibles, and the hobby

=== ORIGINAL SOURCE ARTICLE (TRANSLATE THIS) ===
{source_content_for_prompt[:12000]}
=== END OF SOURCE ===

**STYLE:** {style.name} - {style.objective}
**TARGET:** 800-1200 words (Based on source length)
**LANGUAGE:** Czech (Čeština)

**KEY INSIGHTS FROM RESEARCH:**
{chr(10).join(f'- {insight}' for insight in research.investment_insights[:5])}

**STRUCTURE REQUIREMENTS:**
Your article MUST have these sections IN ORDER:

1. **Header with Source** (Start with: "**Původní zdroj:** {master_source_url}")
2. **Title** (# {topic})
3. **Úvod** (Introduction - TRANSLATE from source intro, 100-150 words)
4. **2-4 Body Sections** (## Headings in Czech - TRANSLATE from source body)
   - Preserve the source's structure
   - Use facts from source only
5. **Závěr** (## Závěr - TRANSLATE from source conclusion, 80-120 words)

**CRITICAL RULES:**
❌ DO NOT stop mid-sentence
❌ DO NOT skip the Závěr section
❌ DO NOT write short, superficial summaries - Go DEEP
❌ DO NOT hallucinate facts - use only research data
❌ DO NOT generate a "Zdroje", "Literatura", "Sources", or "Reference" section - sources are handled automatically in the document header
✅ ALWAYS finish with a complete Závěr
✅ If running out of space, make body shorter but KEEP Závěr
✅ Use Markdown formatting (# ## **bold**)

**WRITE THE COMPLETE ARTICLE NOW:**
"""

        logger.info("Calling LLM for full article generation...")
        
        try:
            # Generate complete article in one call
            content = self.llm_client.call(
                system_prompt="You are a professional Czech writer. ALWAYS write complete articles with proper conclusions. Never stop mid-sentence.",
                user_prompt=prompt,
                max_tokens=4000  # Maximum limit to prevent truncation
            )
            
            # Prepend Master Source URL explicitly
            if master_source_url and master_source_url != "N/A":
                content = f"Původní zdroj: {master_source_url}\n\n{content}"

            # Smart Truncation Handling
            content_lower = content.lower()
            
            # Check if conclusion is missing
            if "závěr" not in content_lower and "shrnutí" not in content_lower:
                logger.warning("⚠️ Article missing conclusion! Fixing content...")
                
                # Check if it stopped mid-sentence (no punctuation at end)
                if content and content[-1] not in ['.', '!', '?', '"', '`', '\n']:
                    # Find last full sentence end
                    import re
                    last_period = max(content.rfind('.'), content.rfind('!'), content.rfind('?'))
                    if last_period > len(content) * 0.8: # Only cut if we preserve most content
                        logger.info("Trimming truncated sentence at position %d", last_period)
                        content = content[:last_period+1]
                    else:
                        # Fallback if no punctuation found nearby (just append newline)
                        content += "."
                
                # Append Emergency Conclusion
                content += "\n\n## Závěr\n\nTento článek shrnul klíčové aspekty tématu a poskytl pohled na aktuální situaci v oblasti sběratelství. Ať už jste začínající sběratel nebo zkušený investor, je důležité sledovat trendy a rozhodovat se na základě ověřených informací."
                logger.info("✅ Appended emergency conclusion.")

            # POST-PROCESSING: Remove any fake "Zdroje" / "Literatura" / "Sources" sections
            # These should NOT be in the article - sources are in document header
            import re
            fake_sources_patterns = [
                r'\n##\s*Zdroje[^\n]*\n[\s\S]*?(?=\n##|$)',  # ## Zdroje ... until next heading or end
                r'\n##\s*Literatura[^\n]*\n[\s\S]*?(?=\n##|$)',
                r'\n##\s*Sources[^\n]*\n[\s\S]*?(?=\n##|$)',
                r'\n##\s*Reference[^\n]*\n[\s\S]*?(?=\n##|$)',
                r'\n##\s*Hlavní zdroje[^\n]*\n[\s\S]*?(?=\n##|$)',
                r'\n##\s*Zdroje a literatura[^\n]*\n[\s\S]*?(?=\n##|$)',
            ]
            
            content_before = len(content)
            for pattern in fake_sources_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            if len(content) < content_before:
                logger.info("🧹 Stripped fake sources section from article (removed %d chars)", content_before - len(content))

            # Create draft
            draft = DraftArticle.create(topic=topic, content=content)
            
            # Store in context
            self.context_manager.add_context(
                "WriterAgent",
                draft.model_dump(),
                metadata={"method": "single_shot_complete", "word_count": draft.word_count, "style": writing_style}
            )
            
            logger.info("✅ Article complete: %d words", draft.word_count)
            return draft
            
        except Exception as e:
            logger.error("Article generation failed: %s", str(e))
            raise


    def _plan_structure(self, topic: str, research: ResearchResult, writing_style_key: str) -> List[dict]:
        """Dynamically plan the article sections based on topic and style."""
        styles = get_all_styles()
        style = styles.get(writing_style_key, styles.get("investor"))
        
        prompt = f"""You are the Chief Editor.
Topic: {topic}. DO NOT REPEAT GENERAL INFORMATION. Focus on unique details.
Style: {style.name} ({style.objective})

Research Details:
{str(getattr(research, 'key_points', []))[:500]}...

Your task: Plan the structure of an Article (600-800 words total).
Create a JSON list of 4-6 SECTIONS.
Each section object must have:
- "title": Creative Czech title for the section (Use Sentence case).
- "instruction": Specific instruction on what to write in this section (in English or Czech).
- "type": "intro", "body", "conclusion", or "sources".

REQURIEMENTS:
1. First section MUST be "type": "intro" (The Hook).
2. The section BEFORE "sources" MUST be "type": "conclusion" (Závěr / Shrnutí).
3. Last section MUST be "type": "sources" (Zdroje & Trivia - integrate cool facts).
4. The MIDDLE sections (Body) must be creative and tailored to the topic.
5. IF style is "Investor", focus sections on "Market Analysis", "Value Potential", "Risks".
6. AVOID generic history lessons. Focus on the specific topic, current relevance, and unique details.

Return ONLY correctly formatted JSON data like:
[
  {{"type": "intro", "title": "...", "instruction": "..."}},
  ...
]
"""
        logger.info("Planning article structure...")
        for attempt in range(3):
            try:
                content = self.llm_client.call(
                    system_prompt="You are a JSON generator. Output only valid JSON array.",
                    user_prompt=prompt,
                    force_provider="gemini"  # Use Gemini for planning to save costs
                )
                # Clean code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                plan = json.loads(content)
                if isinstance(plan, list) and len(plan) >= 3:
                    logger.info("Generated structure with %d sections", len(plan))
                    return plan
            except Exception as e:
                logger.warning("Structure planning failed (attempt %d): %s", attempt, e)
        
        # Fallback if planning fails
        logger.warning("Using fallback structure")
        return [
            {"type": "intro", "title": "Úvod do problematiky", "instruction": "Write a gripping hook."},
            {"type": "body", "title": "Hlavní téma", "instruction": "Deep dive into the main topic."},
            {"type": "body", "title": "Analýza a souvislosti", "instruction": "Analyze context and details."},
            {"type": "conclusion", "title": "Závěr a verdikt", "instruction": "Summarize key findings and provide a final thought or recommendation."},
            {"type": "sources", "title": "Zdroje a zajímavosti", "instruction": "Mention key sources and trivia."}
        ]

    def _get_writing_guidelines(self) -> str:
        """Get writing best practices from Context7.

        Returns:
            Writing guidelines string (empty if unavailable)
        """
        try:
            # Try to get content writing documentation
            lib_id = self.context7_client.resolve_library("content-writing")
            if lib_id:
                docs = self.context7_client.get_docs(
                    lib_id,
                    topic="investment article writing",
                    mode="info"
                )
                logger.info("Retrieved writing guidelines (%d chars)", len(docs))
                return docs

            logger.info("Writing guidelines not available, using defaults")
            return ""

        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Failed to get writing guidelines: %s", str(e))
            return ""

    def _build_section_prompt(
        self,
        topic: str,
        section: dict,
        research: ResearchResult,
        writing_guidelines: str,
        writing_style_key: str,
        previous_content: str
    ) -> str:
        """Build prompt for a specific section."""
        
        # Format research findings
        detailed_summary = getattr(research, "detailed_summary", "")
        if not detailed_summary or len(detailed_summary) < 100:
             detailed_summary = "\n".join(f"- {point}" for point in research.key_points)
        
        # Format sources (use ALL retrieved sources to ensure comprehensive list)
        sources_text = "\n".join(f"- {source}" for source in research.sources)

        # Get style
        styles = get_all_styles()
        style = styles.get(writing_style_key, styles.get("investor"))
        
        current_date_str = datetime.date.today().strftime("%Y-%m-%d")

        # Context construction (provide tail of previous content)
        context_str = ""
        if previous_content:
            last_chunk = previous_content[-1000:]
            context_str = f"""
PREVIOUS CONTENT (This leads into your section - Maintain Flow):
...{last_chunk}
"""
        
        prompt = f"""You are a top-tier magazine editor and writer for a trading card publication.
Current Date: {current_date_str}.
WRITING STYLE: {style.name}. 
OBJECTIVE: {style.objective}.

Your task is to write ONLY the following section of a Feature Article about: {topic}

SECTION: "{section['type'].upper()} - {section['title']}"
INSTRUCTION: {section['instruction']}

═══════════════════════════════════════════════════════════════
RESEARCH DATA (Synthesize this):
{detailed_summary}

Available Sources:
{sources_text}
═══════════════════════════════════════════════════════════════

{context_str}

RULES:
1. Write ONLY the content for this section. Do NOT write the main Title.
2. STRICTLY FOCUS ON THE TOPIC: "{topic}". DO NOT WRITE GENERAL HISTORY. Do not write about "how collecting started" or "history of the company" unless the topic is explicitly "History of X". Jump straight into specific details.
3. SYNTHESIS: Combine info from multiple sources IF POSSIBLE. If only one source is available, use it deeply. Do not just list facts.
4. HEADINGS: Use Sentence case (only first letter capitalized, unless proper noun) for any subheadings.
5. INTERESTING FACTS: Weave in "Zajímavosti" (fun facts) or insider trivia that adds unique value.
6. NO FLUFF: Every sentence must add value. If it's a filler sentence, delete it.
7. MAINTAIN FLOW: Ensure this section flows naturally from the previous content.
8. LANGUAGE: CZECH (Čeština). Professional, rich vocabulary, engaging tone.
9. LENGTH: Approximately 150-200 words per section. Keep it concise but informative.
10. SOURCES (CRITICAL): IF this section is about "Zdroje" (Sources), you MUST list the FULL URLs from the "Available Sources" provided above.
    Format exactly as:
    **Hlavní zdroje:**
    * https://example.com/article1
    * https://example.com/article2
    (Do not hide links behind text. Show the full URL).

Generate the section content now:"""

        return prompt

    def _generate_article_with_openai(self, prompt: str) -> str:
        """Generate article content using OpenAI API."""
        logger.info("Calling OpenAI API for section generation")

        for attempt in range(1, self.max_retries + 1):
            try:
                # Use unified LLM client
                content = self.llm_client.call(
                    system_prompt="You are a professional writer. Write in CZECH. Do not use Markdown headers unless explicitly asked.",
                    user_prompt=prompt
                )

                # Validate minimum length (check 500 chars ~ 80-100 words)
                if len(content) < 500:
                    raise ValueError(f"Content too short: {len(content)} chars. Needed 500+.")

                logger.info("Successfully generated content (%d chars)", len(content))
                return content

            except Exception as e:
                wait_time = 2 ** (attempt - 1)
                logger.warning(
                    "OpenAI API attempt %d/%d failed: %s. Retrying...",
                    attempt, self.max_retries, str(e)
                )

                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to generate content after retries")
                    raise

        raise RuntimeError("Generation failed after all retries")

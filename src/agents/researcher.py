"""Researcher Agent for gathering investment-focused information.

This module implements the Researcher Agent, responsible for gathering
detailed information from category-specific web sources using SEO tools
and Context7 MCP for technical documentation.
"""

import datetime
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from src.config.settings import Config

from src.tools.context7_client import Context7Client
from src.tools.seo_tools import SEOTools
from src.utils.context_manager import ContextManager
from src.utils.llm_client import get_llm_client


logger = logging.getLogger(__name__)


class ResearchResult(BaseModel):
    """Pydantic model for research output.

    Attributes:
        topic: The topic being researched
        category: Content category (pokemon, hockey, or soccer)
        sources: List of source URLs consulted
        key_points: List of key findings from research
        investment_insights: List of investment-focused insights
        seo_keywords: List of relevant SEO keywords
        detailed_summary: Detailed 500-word summary of the scraped content
    """

    topic: str = Field(..., min_length=10, max_length=200)
    category: str = Field(..., pattern="^(pokemon|hockey|soccer)$")
    sources: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    investment_insights: List[str] = Field(default_factory=list)
    seo_keywords: List[str] = Field(default_factory=list)
    detailed_summary: str = Field(default="")
    original_source_text: str = Field(default="", description="Full original text of the master source article")
    data_quality_warning: str = Field(default="None")
    verification_status: str = Field(default="VERIFIED")  # VERIFIED, REJECTED, UNCERTAIN


class ResearcherAgent:
    """Researcher Agent for gathering investment-focused information.

    This agent uses SEO tools (Serper.dev, ScrapeWebsiteTool) to gather
    information from category-specific sources and Context7 MCP for
    technical documentation. It focuses on investment insights and
    market trends.

    Attributes:
        context_manager: Context manager for storing research results
        context7_client: Context7 MCP client for library documentation
        seo_tools: SEO and web scraping tools
        config: System configuration
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        context_manager: ContextManager,
        context7_client: Context7Client,
        seo_tools: SEOTools,
        config: Config
    ):
        """Initialize researcher with context, Context7, and research tools.

        Args:
            context_manager: Context manager for storing outputs
            context7_client: Context7 MCP client for documentation
            seo_tools: SEO and web scraping tools
            config: System configuration
        """
        self.context_manager = context_manager
        self.context7_client = context7_client
        self.seo_tools = seo_tools
        self.config = config
        self.max_retries = config.max_retries
        self.llm_client = get_llm_client(config)

        logger.info("ResearcherAgent initialized")

    def research(
        self,
        topic: str,
        category: str,
        status_callback=None,
        active_url: str = None,
        source_content: str = None  # NEW: Pre-fetched content
    ) -> ResearchResult:
        """Gather information from category-specific sources.

        This method:
        1. Uses SEO tools to get SERP data and keywords (or uses provided active_url)
        2. Scrapes category-specific web sources
        3. Retrieves Context7 documentation for best practices
        4. Compiles research findings with investment focus
        5. Generates detailed summary

        Args:
            topic: Topic to research
            category: Content category
            status_callback: Optional callback for UI updates
            active_url: Optional direct URL to source (provided by Strategist)
            category: Content category (pokemon, hockey, or soccer)
            status_callback: Optional function(msg) to report progress

        Returns:
            ResearchResult with findings, sources, investment insights,
            and SEO keywords

        Raises:
            Exception: If research fails after all retries
        """
        logger.info("Starting research for topic: %s (category: %s)", topic, category)

        for attempt in range(1, self.max_retries + 1):
            try:
                # Step 1: Get SEO insights
                if status_callback:
                    status_callback(f"Step 1/4: Gathering SEO insights (Attempt {attempt})")
                logger.info("Gathering SEO insights for: %s", topic)
                seo_keywords = self._get_seo_keywords(topic, category)

                # Step 2: Scrape category-specific sources
                if status_callback:
                    status_callback("Step 2/4: Scraping & downloading verified sources...")
                logger.info("Scraping category-specific sources for: %s", category)
                scraped_data = self._scrape_sources(category, topic, active_url, source_content)

                # Step 3: Get Context7 documentation (optional)
                # if status_callback: status_callback("Step 3/4: Checking Context7 docs...") # fast, maybe skip UI update
                logger.info("Retrieving Context7 documentation")
                context7_docs = self._get_context7_docs(category)

                # Step 4: Compile research findings
                if status_callback:
                    status_callback("Step 4/4: Analyzing content with LLM (Synthesizing)...")
                logger.info("Compiling research findings")
                result = self._compile_research(
                    topic,
                    category,
                    seo_keywords,
                    scraped_data,
                    context7_docs
                )

                # Store in context manager
                self.context_manager.add_context(
                    "ResearcherAgent",
                    result.model_dump(),
                    metadata={"attempt": attempt}
                )

                logger.info(
                    "Research complete for topic: %s (%d sources, %d insights)",
                    topic, len(result.sources), len(result.investment_insights)
                )

                return result

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "Research attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )

                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Research failed after %d attempts for topic: %s",
                        self.max_retries, topic
                    )
                    raise

        # Should never reach here
        raise RuntimeError(f"Research failed after all retries for topic: {topic}")

    def _get_seo_keywords(self, topic: str, category: str) -> List[str]:
        """Get SEO keywords for the topic."""
        try:
            query = f"{topic} {category} trading cards investment"
            keywords = self.seo_tools.get_keywords(query, category)
            logger.info("Retrieved %d SEO keywords", len(keywords))
            return keywords
        except Exception as e:
            logger.warning("Failed to get SEO keywords: %s", str(e))
            return [category, "trading cards", "investment", "value", "market"]

    def _scrape_sources(self, category: str, topic: str, active_url: str = None, source_content: str = None) -> Dict:
        """Scrape category-specific web sources."""
        try:
            # STRATEGY 0: Use Pre-Fetched Content (Fastest & Most Reliable)
            if source_content and active_url:
                logger.info("🚀 using CACHED content from Strategist (%d chars). Skipping scrape.", len(source_content))
                return {
                    'sources': [{'url': active_url}], 
                    'content': {active_url: source_content}
                }

            # STRATEGY 1: DIRECT URL STRATEGY (High Priority)
            if active_url:
                logger.info("🔎 Using DIRECT source provided by Strategist: %s", active_url)
                content = ""
                
                # Attempt 1: Standard CrewAI Tool
                try:
                    content = self.seo_tools.scrape_tool.run(website_url=active_url)
                except Exception as e:
                    logger.warning("Standard scraping tool failed: %s", str(e))

                # Attempt 2: Browser Mask Fallback (requests + bs4)
                # If standard tool fails or returns garbage/cookie banners (< 600 chars)
                if not content or len(str(content)) < 600:
                    logger.info("Standard scrape insufficient. Activating BROWSER MASK fallback...")
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Referer': 'https://www.google.com/'
                        }
                        response = requests.get(active_url, headers=headers, timeout=20)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # Clean up DOM
                            for element in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
                                element.decompose()
                            
                            content = soup.get_text(separator='\n', strip=True)
                            logger.info("✅ Browser Mask scrape successful! Recovered %d chars.", len(content))
                        else:
                            logger.warning("Browser Mask failed with status: %d", response.status_code)
                    except Exception as ex:
                        logger.error("Browser Mask scraping failed: %s", str(ex))

                if content and len(str(content)) > 500:
                    logger.info("✅ Final scrape result valid (%d chars)", len(str(content)))
                    return {
                        'sources': [{'url': active_url}],
                        'content': {active_url: content}
                    }
                else:
                    logger.warning("All scraping attempts failed for active URL. Content too short.")
            
            # FALLBACK: Scrape category-specific sources...
            # This ensures we find articles about "hokejisté hockey cards", not just "hockey cards"
            scraped_data = self.seo_tools.scrape_category_sources(
                category=category,
                topic=topic,  # CRITICAL: Pass topic to find relevant articles
                max_sources=6
            )
            
            # Check if scraping actually worked
            if not scraped_data.get('content') and not scraped_data.get('sources'):
                 logger.warning("Web scraping failed (likely API limits). Switching to SYNTHETIC RESEARCH mode.")
                 return {
                     'sources': [],
                     'content': {'SYNTHETIC': 'NO_WEB_CONTENT_AVAILABLE'},
                     'is_synthetic': True
                 }

            logger.info("Scraped %d sources for topic '%s' in category: %s", 
                       len(scraped_data.get('sources', [])), topic, category)
            return scraped_data
        except Exception as e:
            logger.warning("Failed to scrape sources: %s. Using synthetic fallback.", str(e))
            return {
                'sources': [], 
                'content': {'SYNTHETIC': 'SCRAPING_ERROR'},
                'is_synthetic': True
            }

    def _get_context7_docs(self, category: str) -> str:
        """Get Context7 documentation for best practices."""
        try:
            crewai_lib_id = self.context7_client.resolve_library("crewai")
            if crewai_lib_id:
                docs = self.context7_client.get_docs(crewai_lib_id, topic="content generation best practices", mode="info")
                return docs
            return ""
        except Exception as e:
            logger.warning("Failed to get Context7 docs: %s", str(e))
            return ""

    def _compile_research(
        self,
        topic: str,
        category: str,
        seo_keywords: List[str],
        scraped_data: Dict,
        context7_docs: str  # pylint: disable=unused-argument
    ) -> ResearchResult:
        """Compile research findings into ResearchResult."""
        # Extract sources
        sources = []
        for source in scraped_data.get('sources', []):
            if isinstance(source, dict):
                sources.append(source.get('url', ''))
            elif isinstance(source, str):
                sources.append(source)
        
        # FALLBACK: If sources list is empty, extract URLs from content dict keys
        # This handles cases where content was cached/scraped directly
        if not sources:
            content_data = scraped_data.get('content', {})
            if isinstance(content_data, dict):
                for url in content_data.keys():
                    if isinstance(url, str) and url.startswith('http'):
                        sources.append(url)
                        logger.info("📎 Recovered source URL from content map: %s", url)

        # Prepare content for LLM analysis
        content_data = scraped_data.get('content', '')
        if isinstance(content_data, dict):
             # Format as explicit source blocks to help LLM verify sources
             raw_text = "\n\n".join(f"SOURCE URL: {k}\nCONTENT: {v}" for k, v in content_data.items() if v)
        else:
             raw_text = str(content_data)

        # Truncate if too long (approx 25k chars to fit context - increased from 15k)
        raw_text = raw_text[:25000]

        # Use LLM to analyze content and extract fresh data
        analysis = self._analyze_with_openai(raw_text, topic, category)

        if analysis.get('verification_status') == 'REJECTED':
            logger.error("Topic rejected by Researcher: %s (Reason: %s)", topic, analysis.get('data_quality_warning'))
            raise ValueError(f"Topic REJECTED due to lack of evidence or factual impossibility: {analysis.get('data_quality_warning')}")

        # CRITICAL: Prioritize the Master Source identified by LLM
        master_url = analysis.get('master_source_url')
        master_source_content = ""
        if master_url and isinstance(master_url, str) and master_url.startswith('http'):
            # Remove if exists to avoid duplicates, then insert at front
            if master_url in sources:
                sources.remove(master_url)
            sources.insert(0, master_url)
            logger.info("🎯 Identified Master Source URL: %s", master_url)
            
            # Extract the original content for this URL
            content_data = scraped_data.get('content', {})
            if isinstance(content_data, dict):
                master_source_content = content_data.get(master_url, "")
                if not master_source_content:
                    # Try fuzzy match
                    for url, text in content_data.items():
                        if master_url in url or url in master_url:
                            master_source_content = text
                            break
        
        # Fallback: Use first available source content if master not found
        if not master_source_content:
            content_data = scraped_data.get('content', {})
            if isinstance(content_data, dict) and content_data:
                first_url = next(iter(content_data))
                master_source_content = content_data.get(first_url, "")
                if sources and not sources[0].startswith('http'):
                    sources[0] = first_url
                logger.info("📄 Using fallback source content (%d chars)", len(master_source_content))

        # Create result
        result = ResearchResult(
            topic=topic,
            category=category,
            sources=sources[:10],
            key_points=analysis.get('key_points', []),
            investment_insights=analysis.get('investment_insights', []),
            seo_keywords=seo_keywords[:20],
            detailed_summary=analysis.get('detailed_summary', ''),
            original_source_text=master_source_content[:15000],  # Limit to ~15k chars
            data_quality_warning=analysis.get('data_quality_warning', 'None'),
            verification_status=analysis.get('verification_status', 'VERIFIED')
        )

        return result

    def _analyze_with_openai(self, content: str, topic: str, category: str) -> Dict[str, Any]:
        """Analyze scraped content using OpenAI to extract relevant, VERIFIED data.

        Args:
            content: Raw scraped text
            topic: Research topic
            category: Category name

        Returns:
            Dict with 'key_points', 'investment_insights', and 'detailed_summary'
        """
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # --- DEFAULT PROMPT (Web Analysis) ---
        prompt = f"""You are a strict data analyst for a TRADING CARD MAGAZINE. 
Current Date: {current_date}

⚠️ ONE-SOURCE STRATEGY:
Your goal is to IDENTIFY THE SINGLE BEST ARTICLE from the provided content and use it as the "Master Source" for translation/adaptation.
- Do NOT synthesize multiple sources unless the main source has gaps.
- We want to virtually "mirror" the structure and information of the BEST comprehensive article found.

TASK:
1. Scan the RAW CONTENT below.
2. Identify the **"Master Article"**: The longest, most detailed, and most relevant text.
3. Your "Detailed Summary" must be a COMPREHENSIVE SUMMARY of that ONE Master Article.

RAW CONTENT:
{content}

CRITICAL RULES:
1. **SELECTING THE MASTER SOURCE**:
   - Must be a real article/guide (not a product page or forum comment).
   - Must be > 300 words if possible.
   - Must be directly about: "{topic}".
   - PRIORITIZE: detailed guides, investment analysis, deep dives.

2. **SOURCE VERIFICATION**:
   - ❌ REJECT Video Games, Digital Cards/NFTs.
   - ❌ REJECT different categories (football vs hockey).
   - ✅ ONLY physical cards.

3. **SUMMARY INSTRUCTIONS**:
   - Capture the FULL flow of the Master Article.
   - Catch all the specific details (sets, prices, historical facts).
   - Don't just bullet point—preserve the *narrative arc* of the original.

OUTPUT FORMAT:
Return a JSON object:
{{
  "master_source_url": "URL_OF_THE_CHOSEN_ARTICLE (Must match one of the SOURCE URLs provided above)",
  "key_points": ["Fact 1 (From Master Source)", "Fact 2", ...],
  "investment_insights": ["Insight 1", ...],
  "detailed_summary": "FULL, DETAILED SUMMARY OF THE MASTER ARTICLE (approx 600-800 words)... [Start by stating]: 'The Master Source selected is [URL/Title]...'",
  "data_quality_warning": "None" or "No good master source found",
  "verification_status": "VERIFIED" or "REJECTED"
}}
"""
            
        # --- SYNTHETIC MODE CHECK ---
        # If content is empty or explicitly flagged as synthetic/missing
        is_synthetic = False
        if isinstance(content, str) and ("NO_WEB_CONTENT" in content or "SCRAPING_ERROR" in content or len(content) < 100):
             is_synthetic = True
             prompt = f"""You are a TRADING CARD EXPERT and HISTORIAN.
Current Date: {current_date}

TASK: Write a detailed, factual research brief about: "{topic}"
CONTEXT: {category} Trading Cards.

⚠️ DATA SOURCE UNAVAILABLE:
Web search failed. You must rely on your INITIAL EXPERT KNOWLEDGE.
Do NOT hallucinate fake URLs or specific recent news if you don't know it.
Focus on TIMELESS FACTS, HISTORY, MECHANICS, and ESTABLISHED MARKET TRENDS.

REQUIREMENTS:
1. **Explain the Topic**: What is it? Why does it matter to collectors?
2. **Key Details**: sets, years, rarities, mechanics.
3. **Investment Angle**: Why do people buy this? Risks vs Rewards.
4. **Conclusion**: Summary for a writer.

OUTPUT FORMAT (JSON):
{{
  "master_source_url": "",
  "key_points": ["Fact 1", "Fact 2", "Fact 3", ...],
  "investment_insights": ["Insight 1", ...],
  "detailed_summary": "Comprehensive 600-word explanation of the topic...",
  "data_quality_warning": "Synthetic/Expert Knowledge Only - No fresh web data",
  "verification_status": "VERIFIED"
}}
"""

        try:
            # Use unified LLM client
            response_text = self.llm_client.call(
                system_prompt="You are a precise data analyst. Return valid JSON only.",
                user_prompt=prompt,
                temperature=0.4 if is_synthetic else 0.3, # Slightly higher temp for creative synthetic generation
                max_tokens=2000,
                json_mode=True,
                force_model=self.config.research_model
            )
            
            import json
            # Handle potential markdown wrapping
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
            
        except Exception as e:
            logger.error("LLM Analysis failed: %s", str(e))
            # Fallback
            return {
                "key_points": [f"Analysis failed for {topic}"],
                "investment_insights": [],
                "detailed_summary": f"Could not analyze content due to error: {e}"
            }

    def _extract_key_points(self, scraped_data: Dict, topic: str) -> List[str]:
        """Extract key points from scraped data.

        Args:
            scraped_data: Scraped web content
            topic: Topic being researched

        Returns:
            List of key points
        """
        key_points = []

        # Extract from scraped content
        content_data = scraped_data.get('content', '')
        
        # Handle content being a dictionary (url -> content) or a string
        if isinstance(content_data, dict):
            # Join all content values into one large string
            content = " ".join(str(v) for v in content_data.values() if v)
        else:
            content = str(content_data)

        if content:
            # Simple extraction: split by sentences and take relevant ones
            sentences = content.split('.')
            for sentence in sentences[:20]:
                sentence = sentence.strip()
                if 20 < len(sentence) < 200:
                    key_points.append(sentence)

        # Add default points if not enough found
        if len(key_points) < 5:
            key_points.extend([
                "Market analysis for " + topic,
                "Investment potential and value trends",
                "Collector demand and rarity factors",
                "Historical price performance",
                "Future market outlook"
            ])

        return key_points

    def _generate_investment_insights(
        self,
        topic: str,
        category: str,
        scraped_data: Dict  # pylint: disable=unused-argument
    ) -> List[str]:
        """Generate investment-focused insights.

        Args:
            topic: Topic being researched
            category: Content category
            scraped_data: Scraped web content (unused but kept for future enhancement)

        Returns:
            List of investment insights
        """
        insights = []

        # Generate category-specific insights
        if category == "pokemon":
            insights.extend([
                "Pokémon card values driven by nostalgia and competitive play",
                "First edition and holographic cards command premium prices",
                "Graded cards (PSA 10) significantly increase investment value",
                "Modern sets show strong short-term appreciation potential"
            ])
        elif category == "hockey":
            insights.extend([
                "Rookie cards of Hall of Fame players offer long-term value",
                "Vintage hockey cards from 1970s-1980s remain strong investments",
                "Autographed cards and game-used memorabilia cards premium",
                "Canadian market shows consistent demand for hockey cards"
            ])
        elif category == "soccer":
            insights.extend([
                "International star player cards drive global market demand",
                "World Cup and Champions League cards show cyclical value",
                "Emerging markets in Asia increasing soccer card values",
                "Limited edition and numbered cards offer scarcity premium"
            ])

        # Add topic-specific insight
        insights.append("Investment opportunity analysis for " + topic)

        return insights

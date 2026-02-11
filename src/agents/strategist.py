"""Strategy Phase for topic generation with SEO and deduplication.

This module implements the Strategy Phase of the TCG Content Generator,
responsible for generating unique, SEO-optimized topics by consulting
category-specific web sources and checking against existing topics in
the Neon database.
"""

import json
import logging
import random
import time
import datetime
from typing import Any, Dict, List, Set

import openai
from pydantic import BaseModel, Field, field_validator

from src.config.settings import Config
from src.config.web_sources import get_sources_for_category
from src.config.writing_styles import get_all_styles, get_style_names
from src.tools.context7_client import Context7Client
from src.utils.topic_manager import get_topic_manager
from src.tools.seo_tools import SEOTools
from src.utils.documentation_manager import DocumentationManager
from src.utils.llm_client import get_llm_client


logger = logging.getLogger(__name__)


class SEOInsights(BaseModel):
    """Pydantic model for SEO insights.

    Attributes:
        keywords: List of relevant keywords
        trends: List of trending topics
        search_volume: Dictionary mapping keywords to search volumes
        serp_data: Raw SERP data from SerperDevTool
    """

    keywords: List[str] = Field(default_factory=list)
    trends: List[str] = Field(default_factory=list)
    search_volume: Dict[str, int] = Field(default_factory=dict)
    serp_data: Dict[str, Any] = Field(default_factory=dict)


class TopicCandidate(BaseModel):
    """Pydantic model for topic candidate.

    Attributes:
        title: Topic title (10-200 characters)
        category: Content category (pokemon, hockey, or soccer)
        sources: List of source URLs consulted
        seo_score: SEO score (0.0-100.0)
        keywords: List of relevant keywords
    """

    title: str = Field(..., min_length=10, max_length=200)
    category: str = Field(..., pattern="^(pokemon|hockey|soccer)$")
    sources: List[str] = Field(default_factory=list)
    seo_score: float = Field(default=0.0, ge=0.0, le=100.0)
    keywords: List[str] = Field(default_factory=list)
    writing_style: str = Field(default="investor")
    cached_content: str = Field(default="", description="Full text content of the source to avoid re-scraping")

    @field_validator('title')
    @classmethod
    def title_must_be_unique(cls, v: str) -> str:
        """Validate title format."""
        return v.strip()


class StrategyPhase:
    """Strategy Phase for topic generation with SEO optimization.

    This class implements the first phase of the TCG Content Generator,
    responsible for generating unique topics by:
    1. Querying Neon database for existing topics BEFORE generation
    2. Using SEO tools (Serper.dev) for SERP data and trends
    3. Scraping category-specific web sources
    4. Generating topic candidates using OpenAI API
    5. Deduplicating against existing topics
    6. Returning JSON-serializable list of topic strings

    Attributes:
        config: System configuration
        neon_client: Neon database client
        context7_client: Context7 MCP client
        seo_tools: SEO and web scraping tools
        doc_manager: Documentation manager
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        config: Config,
        context7_client: Context7Client,
        seo_tools: SEOTools,
        doc_manager: DocumentationManager
    ):
        """Initialize strategy phase with required clients.

        Args:
            config: System configuration
            context7_client: Context7 MCP client for library documentation
            seo_tools: SEO tools for SERP data and web scraping
            doc_manager: Documentation manager for logging
        """
        self.config = config
        self.topic_manager = get_topic_manager()
        self.context7_client = context7_client
        self.seo_tools = seo_tools
        self.doc_manager = doc_manager
        self.max_retries = config.max_retries
        self.llm_client = get_llm_client(config)

        logger.info("StrategyPhase initialized")
        self.doc_manager.log_event(
            "Strategy Phase Initialized",
            "Strategy Phase component initialized with SEO tools and database client"
        )

    def generate_topics(self, distribution: Dict[str, int]) -> List[TopicCandidate]:
        """Generate deduplicated topic list with SEO optimization.

        This is the main orchestration method that:
        1. Fetches existing topics from database
        2. Generates topic candidates for each category
        3. Deduplicates against existing topics
        4. Returns list of TopicCandidate objects with assigned styles

        Args:
            distribution: Dict with 'pokemon', 'hockey', 'soccer' counts

        Returns:
            List of TopicCandidate objects

        Raises:
            Exception: If generation fails after all retries
        """
        logger.info("Starting topic generation with distribution: %s", distribution)
        self.doc_manager.log_event(
            "Topic Generation Started",
            f"Distribution: {distribution}"
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                # Step 1: Fetch existing topics BEFORE generation
                existing_topics = self._fetch_existing_topics()
                logger.info("Found %d existing topics in database", len(existing_topics))

                # Step 2: Generate candidates for each category
                all_candidates: List[str] = []

                for category, count in distribution.items():
                    if count > 0:
                        logger.info(
                            "Generating %d topics for category: %s",
                            count, category
                        )

                        # Get SEO insights
                        seo_insights = self._get_seo_insights(category)

                        # Research web sources and generate candidates (with buffer for deduplication)
                        # Generate extra topics to ensure we meet the quota after deduplication
                        generation_count = count + 5
                        candidates = self._research_web_sources(
                            category, generation_count, seo_insights
                        )

                        # Add full candidate objects directly
                        all_candidates.extend(candidates)

                        logger.info(
                            "Generated %d candidates for %s (requested %d + buffer)",
                            len(candidates), category, count
                        )

                # Step 3: Deduplicate against existing topics
                unique_candidates = self._deduplicate(all_candidates, existing_topics)

                # Step 4: RETRY LOOP - If all topics are duplicates, find NEW sources
                source_retry_count = 0
                max_source_retries = 5
                
                while len(unique_candidates) == 0 and source_retry_count < max_source_retries:
                    source_retry_count += 1
                    logger.warning(
                        "All topics were duplicates! Searching for NEW sources (attempt %d/%d)...",
                        source_retry_count, max_source_retries
                    )
                    
                    # Category-specific search queries in multiple languages
                    category_queries = {
                        "pokemon": [
                            "Pokémon TCG news articles",
                            "Pokémon TCG blog",
                            "Pokémon karty novinky články",
                            "Pokémon Sammelkarten Neuigkeiten",
                            "Pokemon card collecting blog 2026",
                        ],
                        "hockey": [
                            "Hockey cards articles news",
                            "Hockey cards blog",
                            "Hokejové karty novinky články",
                            "Eishockey Sammelkarten Blog",
                            "NHL trading cards collecting news",
                        ],
                        "soccer": [
                            "Soccer cards articles news",
                            "Soccer cards blog",
                            "Fotbalové karty novinky články",
                            "Fußball Sammelkarten Neuigkeiten",
                            "Football trading cards Panini news",
                        ],
                    }
                    
                    for category, count in distribution.items():
                        if count > 0:
                            # Get category-specific queries
                            queries = category_queries.get(category, [f"{category} trading cards news"])
                            
                            # Use query based on retry count (cycle through available queries)
                            query_index = (source_retry_count - 1) % len(queries)
                            alt_query = queries[query_index]
                            
                            logger.info("Trying alternative search: '%s' for %s", alt_query, category)
                            
                            # Re-scrape with category-specific query
                            scraped_data = self.seo_tools.scrape_category_sources(
                                category, topic=alt_query, max_sources=10
                            )
                            
                            # Get SEO insights again
                            seo_insights = self._get_seo_insights(category)
                            
                            # Rebuild prompt and generate new candidates
                            prompt = self._build_topic_generation_prompt(
                                category, count + 3, seo_insights, scraped_data, 
                                [], existing_topics, False
                            )
                            
                            new_candidates = self._generate_topics_with_openai(
                                prompt, category, count + 3, seo_insights,
                                existing_topics=existing_topics,
                                scraped_data=scraped_data
                            )
                            
                            # Deduplicate the new candidates
                            new_unique = self._deduplicate(new_candidates, existing_topics)
                            unique_candidates.extend(new_unique)
                            
                            if len(unique_candidates) > 0:
                                logger.info("Found %d new unique topics from alternative sources!", len(unique_candidates))
                                break
                
                # Step 5: Return all unique candidates (including buffer)
                # The Orchestrator will choose which ones to use until the quota is met.
                final_topics = unique_candidates
                
                logger.info(
                    "Topic generation complete: %d unique candidates available for %d requested slots",
                    len(final_topics), sum(distribution.values())
                )
                
                # Log generated topics for documentation
                topic_titles = [t.title for t in final_topics]
                self.doc_manager.log_event(
                    "Topic Generation Complete",
                    f"Generated {len(final_topics)} unique topics: {topic_titles}"
                )

                return final_topics

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "Topic generation attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )
                self.doc_manager.log_problem(
                    f"Topic Generation Attempt {attempt} Failed",
                    "active",
                    f"Error: {str(e)}"
                )

                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error(
                        "Topic generation failed after %d attempts",
                        self.max_retries
                    )
                    self.doc_manager.log_problem(
                        "Topic Generation Failed",
                        "active",
                        f"Failed after {self.max_retries} attempts. Last error: {str(e)}"
                    )
                    raise

        # Should never reach here, but for type safety
        raise RuntimeError("Topic generation failed after all retries")

    def _fetch_existing_topics(self) -> Set[str]:
        """Query temporary database for ALL existing topics before generation.

        This method is called BEFORE generating new topics to ensure
        deduplication. It retrieves all topic titles from the temporary database.

        Returns:
            Set of existing topic title strings

        Raises:
            Exception: If database query fails after all retries
        """
        logger.info("Fetching existing topics from temporary database")

        try:
            # Query all topics from Neon database
            topics = self.topic_manager.get_existing_topics()
            topic_set = set(topics)

            logger.info(
                "Successfully fetched %d existing topics from Neon database",
                len(topic_set)
            )
            return topic_set

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to fetch existing topics: %s", str(e))
            # Return empty set if database fails - better than crashing
            return set()

    def _get_seo_insights(self, category: str) -> SEOInsights:
        """Get SERP data, Google Trends, and keywords using Serper.dev.

        This method uses the SEO tools to gather insights about trending
        topics and keywords for the specified category.

        Args:
            category: Content category (pokemon, hockey, or soccer)

        Returns:
            SEOInsights model with keywords, trends, and SERP data
        """
        logger.info("Gathering SEO insights for category: %s", category)

        # Build search query
        query = f"{category} trading cards investment 2026"

        # Get SERP data
        serp_data = self.seo_tools.get_serp_data(query, num_results=10)

        # Get trends
        trends_data = self.seo_tools.get_google_trends(query)

        # Extract keywords
        keywords = self.seo_tools.get_keywords(f"best {category} cards", category)

        # Build insights model
        insights = SEOInsights(
            keywords=keywords,
            trends=trends_data.get('related_queries', []),
            search_volume={},  # Would need additional API for volume data
            serp_data=serp_data
        )

        logger.info(
            "SEO insights gathered: %d keywords, %d trends",
            len(insights.keywords), len(insights.trends)
        )

        return insights

    def _research_web_sources(
        self,
        category: str,
        count: int,
        seo_insights: SEOInsights
    ) -> List[TopicCandidate]:
        """Research category-specific web sources and generate topic candidates.

        This method:
        1. Scrapes category-specific web sources
        2. Uses Context7 MCP for library documentation
        3. Generates topic candidates using OpenAI API with SEO insights

        Args:
            category: Content category (pokemon, hockey, or soccer)
            count: Number of topics to generate
            seo_insights: SEO insights for the category

        Returns:
            List of TopicCandidate models
        """
        logger.info(
            "Researching web sources for %s (generating %d topics)",
            category, count
        )

        # Define news-focused query to ensure we find "Articles" first
        news_topic = f"latest {category} trading card news blog"
        
        # Scrape category-specific sources using the news topic
        scraped_data = self.seo_tools.scrape_category_sources(
            category, topic=news_topic, max_sources=15
        )

        # Get Context7 documentation for CrewAI (if available)
        try:
            crewai_lib_id = self.context7_client.resolve_library("crewai")
            if crewai_lib_id:
                _ = self.context7_client.get_docs(
                    crewai_lib_id,
                    topic="content generation",
                    mode="info"
                )
                logger.info("Retrieved CrewAI documentation from Context7")
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Could not fetch CrewAI docs: %s", str(e))

        # Get category sources for context
        category_sources = get_sources_for_category(category)
        source_names = [s['name'] for s in category_sources]

        # Get recent topics to prevent repetition
        existing_topics_list = list(self.topic_manager.get_existing_topics())

        # Check if we have valid content
        content_map = scraped_data.get('content', {})
        fallback_mode = False
        if not content_map:
            logger.warning("No scraped content available (search failed?). Switching to EVERGREEN/FALLBACK mode.")
            fallback_mode = True

        # Build prompt for OpenAI
        prompt = self._build_topic_generation_prompt(
            category, count, seo_insights, scraped_data, source_names, existing_topics_list, fallback_mode
        )

        # Generate topics using OpenAI with Semantic Deduplication
        candidates = self._generate_topics_with_openai(
            prompt, category, count, seo_insights, 
            existing_topics=existing_topics_list,
            scraped_data=scraped_data  # Pass scraped data for caching
        )

        logger.info(
            "Generated %d topic candidates for %s",
            len(candidates), category
        )

        return candidates

    def _build_topic_generation_prompt(
        self,
        category: str,
        count: int,
        seo_insights: SEOInsights,
        scraped_data: Dict[str, Any],
        source_names: List[str],
        recent_topics: List[str] = None,
        fallback_mode: bool = False
    ) -> str:
        """Build prompt for OpenAI topic generation."""
        current_date_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # Extract key information from scraped data
        content_map = scraped_data.get('content', {})
        full_source_content = ""
        if isinstance(content_map, dict):
            # Take FULL TEXT (up to 10,000 chars - approx 1500-2000 words) from top 3 sources
            # Quality > Quantity. We need to be 100% sure about the topic.
            for url, text in list(content_map.items())[:3]:  
                clean_text = str(text)[:10000].replace('\n', ' ')
                full_source_content += f"=== SOURCE ===\nURL: {url}\nCONTENT: {clean_text}...\n================\n\n"
        
        scraped_summary = f"analyzed {len(content_map)} articles (deep read of top 3)."
        
        # Format recent topics context
        recent_context = ""
        if recent_topics:
            formatted_recent = "\n".join([f"- {t}" for t in recent_topics[:30]]) # Limit to last 30
            recent_context = f"\nRECENTLY COVERED TOPICS (DO NOT REPEAT THESE SUBJECTS):\n{formatted_recent}\n"

        # Get list of available styles
        styles = get_style_names()
        styles_list = ", ".join([f"'{s}'" for s in styles])

        # Define category-specific keywords for stricter validation
        keywords_pokemon = '"Pokemon TCG", "ETB", "Elite Trainer Box", "Booster Box", "Holo", "Reverse Holo", "Full Art", "Secret Rare", "Trainer Gallery", "VMAX", "Charizard", "Pikachu", "Scarlet & Violet", "Sword & Shield", "Energy", "Trainer Card", "Gym Leader", "Pull Rates", "Illustration Rare"'
        
        keywords_sports = '"Young Guns", "Future Watch", "RPA", "Patch Auto", "Jersey Card", "Upper Deck", "Panini", "Topps", "Chrome", "Refractor", "Prizm", "Select", "Series 1", "Series 2", "Stature", "The Cup", "SP Authentic", "Skybox", "Artifacts", "Rookie Card", "RC", "Logoman"'
        
        # Universal keywords (valid for all physical cards)
        keywords_universal = '"Hobby Box", "Blaster Box", "Checklist", "Parallel", "Autograph", "PSA", "BGS", "SGC", "Grading", "Case Hit", "Redemption", "Card Stock", "Serial Numbered", "On-card", "Sticker auto", "Toploader", "Penny sleeve", "Binder", "Memorabilia"'
        
        # International keywords for secondary validation
        keywords_intl = '"Sammelkarten", "Aufkleber", "Stickeralbum", "Booster", "Display", "Autogramm", "Cartes", "Figurine", "Cromos", "Pochette", "Bustine", "Sobres", "Album", "Colección"'

        # Select the right set based on category
        if "pokemon" in category.lower():
            target_keywords = f"   - POKEMON TCG SPECIFIC: {keywords_pokemon}\n   - UNIVERSAL: {keywords_universal}"
        elif "football" in category.lower() or "soccer" in category.lower() or "hockey" in category.lower():
            target_keywords = f"   - SPORTS CARD SPECIFIC: {keywords_sports}\n   - UNIVERSAL: {keywords_universal}"
        else:
             target_keywords = f"   - UNIVERSAL: {keywords_universal}"

        if fallback_mode:
            source_instruction = f"""
3. **GENERATE EVERGREEN {category.upper()} TOPICS**: Since no breaking news was found, generate interesting **Analysis**, **Strategic Guides**, or **Deep Dives** specific to **{category}**.
   - Do NOT try to link to current news.
   - Use your internal expert knowledge about {category}.
   - Topics should be timeless and practical (e.g., "How to Grade {category} Cards", "Investment Analysis: Modern vs. Vintage", "Complete Guide to {category} Sets").
            """
            requirements = f"""
- **EVERGREEN & ANALYTICAL CONTENT**: Focus on analysis, strategy, and detailed guides for {category} collectors.
- **AVOID GENERIC HISTORY**: Do not write generic "History of..." articles unless it's a specific deep dive into a set or era.
- **NO FAKE LINKS**: Do NOT include a source_url if you don't have a real news source. Leave it empty string "".
- **BE SPECIFIC**: Use precise set names and terminology related to {category}.
"""
        else:
            source_instruction = f"""
3. **GENERATE TOPICS**: Based on the news above, generate {count} interesting article topics.
   - Use the REAL URLs from the source text.
   - DO NOT invent "example.com" links.
   - Ideally focus on Physical Cards, but if you are unsure, include it. The Researcher will validate it later.
            """
            requirements = f"""
- **{category.upper()} TOPICS ONLY**: All topics must be strictly about **{category}**.
- **PHYSICAL CARDS ONLY (STRICT)**: 
   - ❌ NEVER generate topics about video games (NHL 24, FIFA 25).
- **SOURCE BASED**: Link every topic to its source URL.
- **BE SPECIFIC**: Use precise set names.
"""

        prompt = f"""You are a content strategist for a trading card platform. 
Current Date: {current_date_str}.
Your goal is to create high-quality article topics.

SOURCE MATERIAL (FULL TEXT):
{full_source_content if not fallback_mode else "No recent news available. Using EXPERT KNOWLEDGE mode."}

{source_instruction}

Generate {count} unique, engaging article topics.
The topics MUST be in CZECH language (Čeština).

Available Writing Styles: {styles_list}

TARGET AUDIENCE:
- Enthusiasts, collectors, and people curious about the hobby.
- People looking for **fresh news**, **comparisons**, and **interesting facts**.

CORE STRATEGY (WHAT TO FOCUS ON):
1. **NEWS & CURRENT EVENTS**: 
   - Look at the VALID sources. Is there a new set mentioned?
   - Create a topic about IT.
   
2. **PRODUCT REVIEWS**:
   - If a VALID source reviews a product, create a "Review" topic.

REQUIREMENTS:
{requirements}
- **SHORT & PUNCHY TITLES**: catchy and short (max 10-12 words).


SEO INSIGHTS (Use for context):
- Top Keywords: {', '.join(seo_insights.keywords[:10])}
- Trending Topics: {', '.join(seo_insights.trends[:5])}

{recent_context}

CRITICAL RULES:
1. **VALIDITY**: { 'Base topics on sources.' if not fallback_mode else 'Base topics on expert knowledge.' }
2. **SOURCE VERIFICATION**: { 'Include source_url.' if not fallback_mode else 'Leave source_url empty.' }
   - ❌ IF the topic is about a VIDEO GAME (digital), DO NOT USE IT.
   - ❌ IF the snippet is too short or vaguely unrelated, DO NOT USE IT.
3. **SEMANTIC UNIQUENESS**: Check the "RECENTLY COVERED TOPICS". Do NOT generate topics that are semantically similar.

OUTPUT FORMAT:
Return ONLY a valid JSON array of objects (Start with '[' and end with ']').
Do NOT return a single object.
You MUST generate EXACTLY {count} topics.

Example structure:
[
  {{
    "title": "Nový set Topps 2024 Series 1: Kompletní přehled",
    "category": "{category}",
    "style": "Expert Analyst",
    "source_url": "https://example.com/article/topps-2024-news"
  }}
]

{recent_context}

CRITICAL RULES FOR UNIQUENESS & VALIDITY:
1. **SEMANTIC UNIQUENESS**: Check the "RECENTLY COVERED TOPICS". Do NOT generate topics that are semantically similar (cover the same underlying event/question). Rephrasing the title is NOT enough.
   - Bad: "Investment tips for McDavid" vs "Should you buy McDavid?". (Too similar).
   - Good: "McDavid's Rookie Year" vs "McDavid's new 2026 inserts". (Different focus).
2. **SOURCE AVAILABILITY**: Propose ONLY topics for which you believe there are existing, substantial ARTICLES (guides, reviews, news) online. Do not invent hyper-specific niche topics if no one writes about them.
3. **TOPIC VARIETY**: If SEO says "Bedard" is trending, do NOT generate 10 topics about Bedard. Use the Web Research to find OTHER news.

OUTPUT FORMAT:
Return ONLY a valid JSON array of objects (Start with '[' and end with ']').
Do NOT return a single object.
You MUST generate EXACTLY {count} topics.

Example structure:
[
  {{"topic": "Velké srovnání: PSA vs. BGS v roce 2026", "style": "analyst"}},
  {{"topic": "Co nám napověděl únik checklistu nové série?", "style": "reporter"}},
  {{"topic": "Historie zakázaných karet: Proč zmizela [Karta]?", "style": "historian"}}
]

Generate EXACTLY {count} varied, specific, and interesting topics now:"""

        return prompt

    def _generate_topics_with_openai(
        self,
        prompt: str,
        category: str,
        count: int,
        seo_insights: SEOInsights,

        existing_topics: List[str] = None,  # Add existing_topics param
        scraped_data: Dict[str, Any] = None # Add scraped_data for caching
    ) -> List[TopicCandidate]:
        """Generate topics using OpenAI API.

        Args:
            prompt: Formatted prompt for OpenAI
            category: Content category
            count: Number of topics to generate
            seo_insights: SEO insights for scoring
            existing_topics: List of existing topics for deduplication

        Returns:
            List of TopicCandidate models

        Raises:
            Exception: If OpenAI API call fails after retries
        """
        existing_topics = existing_topics or []
        logger.info("Generating topics with OpenAI API (checking against %d existing)", len(existing_topics))

        for attempt in range(1, self.max_retries + 1):
            try:
                # Use unified LLM client
                content = self.llm_client.call(
                    system_prompt=f"You are a trading card expert. Generate exactly {count} topics in JSON format.",
                    user_prompt=prompt,
                    json_mode=True,
                    # force_model=self.config.research_model  # Revert to Sonnet (default) for intelligence
                )

                # Parse JSON response
                try:
                    # Clean potential markdown
                    cleaned_content = content
                    if "```json" in cleaned_content:
                        cleaned_content = cleaned_content.replace("```json", "").replace("```", "")
                    elif "```" in cleaned_content:
                        cleaned_content = cleaned_content.replace("```", "")
                    cleaned_content = cleaned_content.strip()

                    parsed_response = json.loads(cleaned_content)
                    
                    if isinstance(parsed_response, dict) and "error" in parsed_response:
                        raise ValueError(f"LLM returned error: {parsed_response['error']}")

                    # Handle dictionary wrapping (e.g. {"topics": [...]})
                    if isinstance(parsed_response, dict):
                        # Try to find a list value
                        found_list = False
                        for key, value in parsed_response.items():
                            if isinstance(value, list) and len(value) > 0:
                                parsed_response = value
                                found_list = True
                                break
                        
                        if not found_list:
                            # If no list found, maybe the dict itself is a single item topic?
                            if "topic" in parsed_response:
                                parsed_response = [parsed_response]
                            else:
                                raise ValueError(f"Response is a dictionary without a clear list: {parsed_response.keys()}")

                    if not isinstance(parsed_response, list):
                        raise ValueError(f"Response is not a list, got {type(parsed_response)}")
                    
                    logger.info("LLM returned %d items in JSON list", len(parsed_response))
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning("Failed to parse JSON response: %s. Content start: %s", str(e), content[:100])
                    # Fallback extraction (only topics, default style)
                    extracted_topics = self._extract_topics_from_text(content, count)
                    parsed_response = [{"topic": t, "style": "investor"} for t in extracted_topics]

                if not isinstance(parsed_response, list):
                    # Wrap in list if single object
                    parsed_response = [parsed_response]

                # Create TopicCandidate objects
                candidates = []
                for item in parsed_response:
                    if len(candidates) >= count:
                        break

                    if isinstance(item, str):
                        # Check if the string is actually a JSON object (common LLM behavior)
                        if item.strip().startswith('{'):
                            try:
                                item_dict = json.loads(item)
                                topic_title = item_dict.get("topic", "") or item_dict.get("title", "")
                                style = item_dict.get("style", "investor")
                            except json.JSONDecodeError:
                                # Not valid JSON, treat as plain string topic
                                topic_title = item
                                style = "investor"
                        else:
                            # Plain string topic
                            topic_title = item
                            style = "investor"
                        source_url = ""
                    else:
                        topic_title = item.get("topic", "") or item.get("title", "")
                        style = item.get("style", "investor")
                        source_url = item.get("source_url", "")

                    if not topic_title:
                        continue

                    # --- SANITIZATION: Reject Malformed JSON Fragments ---
                    # Sometimes the LLM returns broken JSON like `category": "pokemon",` as the topic
                    if isinstance(topic_title, str):
                        # Check for obvious JSON fragment patterns
                        malformed_patterns = ['":', '": "', '",']
                        if any(pattern in topic_title for pattern in malformed_patterns):
                            logger.warning("Skipping malformed topic title (JSON fragment): %s", topic_title)
                            continue
                        
                        # Also skip if it starts with lowercase 'category' or similar field names
                        if topic_title.strip().lower().startswith(('category":', 'style":', 'source_url":')):
                            logger.warning("Skipping malformed topic title (field name fragment): %s", topic_title)
                            continue
                    
                    # --- SANITIZATION: Check for Double-Encoded JSON ---
                    # Sometimes the 'topic' field itself contains a JSON string
                    if isinstance(topic_title, str) and topic_title.strip().startswith('{') and 'topic' in topic_title:
                        try:
                            inner_dict = json.loads(topic_title)
                            if isinstance(inner_dict, dict):
                                topic_title = inner_dict.get('topic', topic_title)
                                # Update style if present in inner dict
                                if 'style' in inner_dict:
                                    style = inner_dict.get('style', style)
                        except json.JSONDecodeError:
                            pass
                    # ---------------------------------------------------
                    
                    # --- RANDOM STYLE INJECTION ---
                    # 30% chance to override the LLM's choice with a random style
                    # This ensures diverse distribution and interesting/unexpected combinations
                    if random.random() < 0.30:
                        all_styles = get_style_names()
                        original_style = style
                        style = random.choice(all_styles)
                        logger.info(
                            "Randomly overrode style for '%s': %s -> %s", 
                            topic_title, original_style, style
                        )
                    # -----------------------------

                    # --- SEMANTIC DEDUPLICATION ---
                    if self._is_semantically_similar(topic_title, existing_topics):
                        logger.warning("Skipping topic '%s' - Semantically similar to existing content.", topic_title)
                        continue
                    # -----------------------------

                    # Calculate simple SEO score based on keyword presence
                    seo_score = self._calculate_seo_score(
                        topic_title, seo_insights.keywords
                    )

                    # LOOKUP CACHED CONTENT
                    source_content_cache = ""
                    if scraped_data and source_url:
                        content_map = scraped_data.get('content', {})
                        # Try exact match or fuzzy match (sometimes trailing slashes differ)
                        if source_url in content_map:
                            source_content_cache = content_map[source_url]
                        else:
                            # Try normalized lookup
                            for s_url, s_text in content_map.items():
                                if source_url in s_url or s_url in source_url:
                                    source_content_cache = s_text
                                    break
                    
                    if source_content_cache:
                        logger.info("Content HIT: Passing cached text for '%s' (%d chars)", topic_title, len(source_content_cache))

                    candidate = TopicCandidate(
                        title=topic_title,
                        category=category,
                        sources=[source_url] if source_url else [],
                        seo_score=seo_score,
                        keywords=seo_insights.keywords[:5],
                        writing_style=style,
                        cached_content=source_content_cache
                    )
                    candidates.append(candidate)

                logger.info("Successfully generated %d topics", len(candidates))
                return candidates

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
                        "Failed to generate topics with OpenAI after %d attempts",
                        self.max_retries
                    )
                    raise

        # Should never reach here
        return []

    def _extract_topics_from_text(self, text: str, count: int) -> List[str]:
        """Extract topics from non-JSON text response using robust strategies.

        This fallback method attempts to salvage topics when JSON parsing fails,
        using regex for JSON patterns and fallback to line-based extraction.

        Args:
            text: Text response from OpenAI
            count: Number of topics to extract

        Returns:
            List of topic strings
        """
        logger.info("Extracting topics from text response (Robust Fallback)")
        import re
        topics = []

        # Strategy 1: Regex for JSON patterns ("topic": "Title")
        # Matches "topic": "Any Text" ignoring whitespace
        matches = re.finditer(r'"topic":\s*"([^"]+)"', text)
        for m in matches:
            t = m.group(1).strip()
            if 10 <= len(t) <= 200:
                topics.append(t)

        if not topics:
             # Strategy 2: Single quotes ('topic': 'Title')
             matches = re.finditer(r"'topic':\s*'([^']+)'", text)
             for m in matches:
                 t = m.group(1).strip()
                 if 10 <= len(t) <= 200:
                    topics.append(t)
        
        # Strategy 3: Line-based extraction (Bullet points)
        if not topics:
            lines = text.split('\n')
            for line in lines:
                # Remove common prefixes
                line = line.strip()
                for prefix in ['- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()

                # Check if line looks like a topic
                # Remove quotes if present
                line = line.strip('"').strip("'")
                
                if 10 <= len(line) <= 200 and line:
                    topics.append(line)

        # Allow more than requested if found, or limit? 
        # Better to return all valid ones found, up to sensible limit
        unique_topics = list(dict.fromkeys(topics)) # Dedupe preserving order
        
        logger.info("Extracted %d topics from text using fallback", len(unique_topics))
        return unique_topics[:count]

    def _is_semantically_similar(self, new_topic: str, existing_topics: List[str]) -> bool:
        """Check if new topic is semantically similar to any existing topic using LLM."""
        if not existing_topics:
            return False
            
        # Optimization: check exact match first
        if any(t.lower().strip() == new_topic.lower().strip() for t in existing_topics):
            return True

        # REDUCED: Only check against last 50 topics (to allow more variety)
        recent_topics = existing_topics[:50]
        
        try:
            prompt = f"""DUPLICITY CHECK
TASK: Determine if the "New Topic" is an EXACT duplicate of any "Existing Topic".

New Topic: "{new_topic}"

Recent Existing Topics:
{json.dumps(recent_topics, ensure_ascii=False)}

RULES:
1. **Only flag EXACT DUPLICATES**: Same news event, same player, same card set discussed.
2. **Different angles are OK**: "Player X rookie cards" vs "Player X autograph cards" are DIFFERENT.
3. **Different time periods are OK**: "Best cards 2025" vs "Best cards 2026" are DIFFERENT.
4. **Be PERMISSIVE**: When in doubt, say NO.

VERDICT: Is the New Topic an EXACT duplicate?
Reply EXACTLY "YES" or "NO".
"""

            response = self.llm_client.call(
                system_prompt="You are a permissive duplication checker. Only flag exact duplicates.",
                user_prompt=prompt,
                max_tokens=5,
                temperature=0.0
            )
            
            is_dup = "YES" in response.upper()
            if is_dup:
                logger.warning("Detected semantic duplicate: '%s' is similar to existing topics.", new_topic)
            return is_dup
            
        except Exception as e:
            logger.warning("Semantic check failed: %s", str(e))
            return False

    def _calculate_seo_score(self, title: str, keywords: List[str]) -> float:
        """Calculate SEO score for a topic title.

        This is a simple scoring algorithm based on keyword presence.

        Args:
            title: Topic title
            keywords: List of relevant keywords

        Returns:
            SEO score (0.0-100.0)
        """
        if not keywords:
            return 50.0  # Default score

        title_lower = title.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in title_lower)

        # Score based on percentage of keywords present
        score = (matches / len(keywords)) * 100.0

        # Bonus for title length (prefer 50-150 chars)
        if 50 <= len(title) <= 150:
            score += 10.0

        # Cap at 100
        return min(score, 100.0)

    def _deduplicate(
        self,
        candidates: List[TopicCandidate],
        existing: Set[str]
    ) -> List[TopicCandidate]:
        """Remove duplicates from candidate list.

        This method filters out any topics that already exist in the database.

        Args:
            candidates: List of TopicCandidate objects
            existing: Set of existing topic strings from database

        Returns:
            List of unique TopicCandidate objects
        """
        logger.info(
            "Deduplicating %d candidates against %d existing topics",
            len(candidates), len(existing)
        )

        # Filter out existing topics (case-insensitive comparison)
        existing_lower = {topic.lower() for topic in existing}
        unique_topics = [
            cand for cand in candidates
            if cand.title.lower() not in existing_lower
        ]

        removed_count = len(candidates) - len(unique_topics)
        logger.info(
            "Deduplication complete: %d duplicates removed, %d unique topics remain",
            removed_count, len(unique_topics)
        )

        if removed_count > 0:
            self.doc_manager.log_event(
                "Topics Deduplicated",
                f"Removed {removed_count} duplicate topics"
            )

        return unique_topics

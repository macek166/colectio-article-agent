"""SEO and web scraping tools for content research.

This module provides tools for SEO research and web scraping using CrewAI tools.
It includes functionality for SERP data retrieval, Google Trends analysis,
keyword research, and category-specific web source scraping.
"""

import logging
import time
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup

from crewai_tools import SerperDevTool, ScrapeWebsiteTool

from src.models.config import Config
from src.config.web_sources import get_source_urls_for_category

logger = logging.getLogger(__name__)


class SEOTools:
    """Tools for SEO research and web scraping.

    This class provides methods for gathering SEO insights, scraping web sources,
    and conducting keyword research using CrewAI tools (SerperDevTool and
    ScrapeWebsiteTool).

    Attributes:
        config: System configuration
        serper_tool: SerperDevTool instance for SERP data and trends
        scrape_tool: ScrapeWebsiteTool instance for web scraping
        max_retries: Maximum number of retry attempts
    """

    def __init__(self, config: Config):
        """Initialize SEO tools with CrewAI tools.

        Args:
            config: System configuration with API keys and settings
        """
        self.config = config
        self.max_retries = config.max_retries

        # Initialize CrewAI tools
        try:
            self.serper_tool = SerperDevTool(api_key=config.serper_api_key)
            logger.info("SerperDevTool initialized successfully")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to initialize SerperDevTool: %s", str(e))
            self.serper_tool = None

        try:
            self.scrape_tool = ScrapeWebsiteTool()
            logger.info("ScrapeWebsiteTool initialized successfully")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to initialize ScrapeWebsiteTool: %s", str(e))
            self.scrape_tool = None

        logger.info("SEOTools initialized")

    def get_serp_data(
        self,
        query: str,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """Get SERP (Search Engine Results Page) data using SerperDevTool.

        This method retrieves search engine results for a given query,
        including organic results, related searches, and search metadata.

        Args:
            query: Search query string
            num_results: Number of results to retrieve (default: 10)

        Returns:
            Dictionary containing SERP data with keys:
                - organic_results: List of organic search results
                - related_searches: List of related search queries
                - search_metadata: Metadata about the search
                - error: Error message if request failed
        """
        if not self.serper_tool:
            logger.warning("SerperDevTool not available, returning empty results")
            return {
                'organic_results': [],
                'related_searches': [],
                'search_metadata': {},
                'error': 'SerperDevTool not initialized'
            }

        logger.info("Fetching SERP data for query: %s", query)

        for attempt in range(1, self.max_retries + 1):
            try:
                # Use SerperDevTool to get SERP data
                result = self.serper_tool.run(
                    search_query=query,
                    num_results=num_results
                )

                # Parse result
                if isinstance(result, dict):
                    logger.info(
                        "Successfully retrieved SERP data for: %s (%d results)",
                        query, len(result.get('organic_results', []))
                    )
                    return result
                elif isinstance(result, str):
                    # Try to parse as JSON if string
                    import json
                    try:
                        parsed = json.loads(result)
                        return parsed
                    except json.JSONDecodeError:
                        logger.warning("Could not parse SERP result as JSON")
                        return {
                            'organic_results': [],
                            'related_searches': [],
                            'search_metadata': {'raw_result': result}
                        }
                else:
                    logger.warning("Unexpected SERP result type: %s", type(result))
                    return {
                        'organic_results': [],
                        'related_searches': [],
                        'search_metadata': {}
                    }

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)  # Exponential backoff
                logger.warning(
                    "SERP data fetch attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to fetch SERP data after %d attempts", self.max_retries)
                    return {
                        'organic_results': [],
                        'related_searches': [],
                        'search_metadata': {},
                        'error': str(e)
                    }

        return {
            'organic_results': [],
            'related_searches': [],
            'search_metadata': {},
            'error': 'Max retries exceeded'
        }

    def get_google_trends(
        self,
        query: str,
        timeframe: str = "now 7-d"
    ) -> Dict[str, Any]:
        """Get Google Trends data using SerperDevTool.

        This method retrieves trending information for a given query,
        including interest over time and related queries.

        Args:
            query: Search query string
            timeframe: Time period for trends (e.g., "now 7-d", "today 3-m")

        Returns:
            Dictionary containing trends data with keys:
                - interest_over_time: Time series data
                - related_queries: Related trending queries
                - error: Error message if request failed
        """
        if not self.serper_tool:
            logger.warning("SerperDevTool not available, returning empty trends")
            return {
                'interest_over_time': [],
                'related_queries': [],
                'error': 'SerperDevTool not initialized'
            }

        logger.info("Fetching Google Trends for query: %s (timeframe: %s)", query, timeframe)

        for attempt in range(1, self.max_retries + 1):
            try:
                # Use SerperDevTool for trends
                # Note: SerperDevTool may not directly support trends,
                # so we'll use search data as a proxy
                result = self.serper_tool.run(
                    search_query=f"{query} trends",
                    num_results=5
                )

                logger.info("Successfully retrieved trends data for: %s", query)
                return {
                    'interest_over_time': [],
                    'related_queries': result.get('related_searches', []) if isinstance(result, dict) else [],
                    'search_results': result
                }

            except Exception as e:  # pylint: disable=broad-except
                wait_time = 2 ** (attempt - 1)
                logger.warning(
                    "Trends fetch attempt %d/%d failed: %s. Retrying in %d seconds...",
                    attempt, self.max_retries, str(e), wait_time
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to fetch trends after %d attempts", self.max_retries)
                    return {
                        'interest_over_time': [],
                        'related_queries': [],
                        'error': str(e)
                    }

        return {
            'interest_over_time': [],
            'related_queries': [],
            'error': 'Max retries exceeded'
        }

    def get_keywords(
        self,
        topic: str,
        category: str
    ) -> List[str]:
        """Get relevant keywords for a topic using SerperDevTool.

        This method extracts keywords from SERP data and related searches
        to identify relevant terms for content optimization.

        Args:
            topic: Topic to get keywords for
            category: Content category (pokemon, hockey, soccer)

        Returns:
            List of relevant keyword strings
        """
        if not self.serper_tool:
            logger.warning("SerperDevTool not available, returning empty keywords")
            return []

        logger.info("Extracting keywords for topic: %s (category: %s)", topic, category)

        # Build search query
        query = f"{topic} {category} trading cards investment"

        # Get SERP data
        serp_data = self.get_serp_data(query, num_results=10)

        # Extract keywords from related searches
        keywords = set()

        # Add related searches
        for related in serp_data.get('related_searches', []):
            if isinstance(related, str):
                keywords.add(related.lower())
            elif isinstance(related, dict):
                keywords.add(related.get('query', '').lower())

        # Extract keywords from organic results titles
        for result in serp_data.get('organic_results', []):
            if isinstance(result, dict):
                title = result.get('title', '')
                # Simple keyword extraction from title
                words = title.lower().split()
                for word in words:
                    if len(word) > 3:  # Filter short words
                        keywords.add(word)

        keyword_list = list(keywords)[:20]  # Limit to top 20
        logger.info("Extracted %d keywords for topic: %s", len(keyword_list), topic)

        return keyword_list

    def _validate_content_quality(self, content: str) -> bool:
        """Rate content quality. Returns True if good."""
        if not content:
            return False
            
        # 1. Length Check (Short content is usually trash/cookies/errors)
        if len(content) < 1000:
            return False
            
        # 2. Ban phrases (Scraper errors & Paywalls)
        bad_phrases = [
            "javascript is disabled", "enable javascript", 
            "access denied", "403 forbidden", "cloudflare",
            "verify you are human", "captcha",
            "login to view", "subscribe to read",
            "cookies to continue", "accept all cookies"
        ]
        content_lower = content.lower()
        if any(phrase in content_lower for phrase in bad_phrases):
             return False
             
        return True

    def _scrape_source(
        self,
        url: str,
        max_content_length: int = 25000  # Increased limit for better context
    ) -> Optional[str]:
        """Scrape content from a single web source with browser emulation fallback.

        Args:
            url: URL to scrape
            max_content_length: Maximum content length to return

        Returns:
            Scraped content as string, or None if scraping failed
        """
        content = ""
        
        # Attempt 1: Standard CrewAI ScrapeWebsiteTool
        if self.scrape_tool:
            try:
                import concurrent.futures
                def _do_scrape():
                    return self.scrape_tool.run(website_url=url)
                
                # Use timeout for standard tool
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_do_scrape)
                    content = future.result(timeout=15)
                    
            except Exception as e:
                logger.warning("Standard scraping failed for %s: %s", url, str(e))

        # Attempt 2: Browser Mask Fallback (requests + bs4)
        # Trigger if standard scrape failed OR returned likely garbage (< 600 chars)
        if not content or len(str(content)) < 600:
            logger.info("Standard scrape weak for %s. Activating BROWSER MASK...", url)
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.google.com/'
                }
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Clean up DOM
                    for element in soup(["script", "style", "nav", "footer", "iframe", "noscript", "svg"]):
                        element.decompose()
                    
                    content = soup.get_text(separator='\n', strip=True)
                    logger.info("✅ Browser Mask scrape successful for %s (%d chars)", url, len(content))
                else:
                    logger.warning("Browser Mask failed for %s with status: %d", url, response.status_code)
            except Exception as ex:
                logger.error("Browser Mask scraping failed for %s: %s", url, str(ex))

        # Final Validation (Quality Gate)
        if content and len(str(content)) > 200:
            # Check Quality
            if not self._validate_content_quality(content):
                logger.warning("❌ Content rejected by Quality Gate (%d chars): %s", len(content), url)
                return None

            if len(content) > max_content_length:
                content = content[:max_content_length]
            return content
        
        return None

    def _discover_urls(
        self,
        topic: str,
        category: str,
        num_results: int = 6  # Reduced from default 10
    ) -> List[str]:
        """Discover relevant URLs through Google Search.
        
        Args:
            topic: The specific topic to search for
            category: The category context
            num_results: Number of results to return (target)
            
        Returns:
            List of discovered URLs
        """
        if not self.serper_tool:
            return []
            
        logger.info("Discovering fresh URLs for topic: %s", topic)
        
        # CRITICAL: Multi-Region & Multi-Language Strategy
        # We want to find the BEST article globally, regardless of language.
        
        lang_contexts = {
             'pokemon': {
                 'en': ['Pokemon TCG news', 'Pokemon cards investment', 'Pokemon TCG meta analysis'],
                 'de': ['Pokemon Karten News', 'Pokemon Sammelkarten Investition'],
                 'es': ['Pokemon TCG noticias', 'Cartas Pokemon coleccionismo'],
                 'fr': ['Cartes Pokemon actualité', 'Pokemon JCC investissement'],
                 'it': ['Pokemon TCG notizie', 'Carte Pokemon valore'],
                 'pt': ['Cartas Pokemon novidades', 'Pokemon TCG investimento'],
                 'jp': ['Pokemon Card Game news', 'Pokemon TCG latest releases'] 
             },
             'hockey': {
                 'en': ['Hockey cards news', 'NHL trading cards release dates', 'Hockey card investment guide'],
                 'cz': ['Hokejové karty novinky', 'Hokejové karty investice', 'Hokejové karty checklist'],
                 'se': ['Ishockeysamlurbilder nyheter', 'Hockeykort värde'],
                 'fi': ['Jääkiekkokortit uutiset', 'Jääkiekkokortit sijoitus'],
                 'de': ['Eishockey Karten News', 'DEL trading cards'],
                 'fr': ['Cartes hockey sur glace', 'Cartes LNH actualité']
             },
             'soccer': {
                 'en': ['Soccer trading cards news', 'Football stickers investment', 'Soccer card market analysis'],
                 'es': ['Cromos La Liga noticias', 'Futbol cards coleccionismo'],
                 'it': ['Calciatori Panini notizie', 'Figurine calcio valore'],
                 'de': ['Fussball Sammelkarten News', 'Topps Chrome Bundesliga'],
                 'fr': ['Cartes foot actualité', 'Sorare news', 'Panini foot album'],
                 'pt': ['Figurinhas futebol noticias', 'Cartas futebol colecionismo']
             }
        }

        queries = []
        category_key = category.lower() if category else "generic"
        
        # Select context for this category
        target_languages = lang_contexts.get(category_key, {'en': [f'{category} trading cards news']})
        
        for lang, terms in target_languages.items():
            for term in terms:
                if topic:
                    # Specific topic search
                    queries.append(f"{topic} {term}")
                else:
                    # Broad news gathering
                    queries.append(f"latest {term}")
                    queries.append(f"best {term} 2026") # Forward looking
        
        # Add a specific "Blog" search for high quality content (English is still good for this, but we keep it mixed)
        queries.append(f"best {category} card collecting blog 2026")

        # Shuffle to ensure variety in the first few searches
        import random
        random.shuffle(queries)
        
        # Dynamic Limit: If looking for specific topic (deep research), check more.
        # If brainstorming (no topic), check fewer to save time.
        query_limit = 8 if topic else 5
        queries = queries[:query_limit]
        
        discovered_urls = []
        
        for q in queries:
            # Stop if we have enough sources (e.g. 5 is plenty for 2-3 strong ones)
            if len(discovered_urls) >= 5:
                break

            try:
                # Ask for fewer results per query to speed up
                results = self.serper_tool.run(search_query=q, num_results=3)
                
                # FIX: Serper returns 'organic' not 'organic_results'
                if isinstance(results, dict):
                    organic = results.get('organic') or results.get('organic_results', [])
                    for res in organic:
                        link = res.get('link')
                        if link and link not in discovered_urls:
                            discovered_urls.append(link)
                            logger.info("Discovered URL: %s", link)
                elif isinstance(results, str):
                    import json
                    try:
                        parsed = json.loads(results)
                        organic = parsed.get('organic') or parsed.get('organic_results', [])
                        for res in organic:
                            link = res.get('link')
                            if link and link not in discovered_urls:
                                discovered_urls.append(link)
                    except:
                        pass
                        
            except Exception as e:
                logger.warning("Search failed for query '%s': %s", q, e)
                
        logger.info("Discovered %d URLs total", len(discovered_urls))
        return discovered_urls[:num_results]

    def scrape_pokemon_sources(
        self,
        topic: Optional[str] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """Scrape Pokemon-specific sources.
        
        Args:
            topic: Optional specific topic to focus on
            max_sources: Maximum number of sources to scrape
            
        Returns:
            Dictionary with 'sources' (list of URLs) and 'content' (dict of URL -> text)
        """
        logger.info("Scraping Pokemon sources (max: %d)", max_sources)
        
        # Discover URLs
        urls = self._discover_urls("pokemon", topic, num_results=max_sources)
        
        # Scrape each URL
        content_dict = {}
        for url in urls:
            scraped_text = self._scrape_source(url)
            if scraped_text:
                content_dict[url] = scraped_text
        
        return {
            'sources': urls,
            'content': content_dict
        }

    def scrape_hockey_sources(
        self,
        topic: Optional[str] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """Scrape Hockey-specific sources.
        
        Args:
            topic: Optional specific topic to focus on
            max_sources: Maximum number of sources to scrape
            
        Returns:
            Dictionary with 'sources' (list of URLs) and 'content' (dict of URL -> text)
        """
        logger.info("Scraping Hockey sources (max: %d)", max_sources)
        
        # Discover URLs
        urls = self._discover_urls("hockey", topic, num_results=max_sources)
        
        # Scrape each URL
        content_dict = {}
        for url in urls:
            scraped_text = self._scrape_source(url)
            if scraped_text:
                content_dict[url] = scraped_text
        
        return {
            'sources': urls,
            'content': content_dict
        }

    def scrape_soccer_sources(
        self,
        topic: Optional[str] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """Scrape Soccer-specific sources.
        
        Args:
            topic: Optional specific topic to focus on
            max_sources: Maximum number of sources to scrape
            
        Returns:
            Dictionary with 'sources' (list of URLs) and 'content' (dict of URL -> text)
        """
        logger.info("Scraping Soccer sources (max: %d)", max_sources)
        
        # Discover URLs
        urls = self._discover_urls("soccer", topic, num_results=max_sources)
        
        # Scrape each URL
        content_dict = {}
        for url in urls:
            scraped_text = self._scrape_source(url)
            if scraped_text:
                content_dict[url] = scraped_text
        
        return {
            'sources': urls,
            'content': content_dict
        }

    def scrape_category_sources(
        self,
        category: str,
        topic: Optional[str] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """Scrape sources for a specific category.

        This is a convenience method that routes to the appropriate
        category-specific scraping method.

        Args:
            category: Category name (pokemon, hockey, soccer)
            topic: Optional specific topic to focus on
            max_sources: Maximum number of sources to scrape

        Returns:
            Dictionary containing scraped content and metadata

        Raises:
            ValueError: If category is invalid
        """
        if not category:
             raise ValueError("Category must be provided (cannot be None)")
             
        category_lower = category.lower()

        if category_lower == 'pokemon':
            return self.scrape_pokemon_sources(topic, max_sources)
        elif category_lower == 'hockey':
            return self.scrape_hockey_sources(topic, max_sources)
        elif category_lower == 'soccer':
            return self.scrape_soccer_sources(topic, max_sources)
        else:
            raise ValueError(
                f"Invalid category: {category}. Must be 'pokemon', 'hockey', or 'soccer'"
            )

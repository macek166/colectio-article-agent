"""
Property-based tests for SEO and web scraping tools.

Feature: tcg-content-generator
Tests category-specific source consultation properties.
"""

from unittest.mock import MagicMock, patch

from hypothesis import given, settings, strategies as st

from src.models.config import Config
from src.tools.seo_tools import (
    SEOTools,
    POKEMON_SOURCES,
    HOCKEY_SOURCES,
    SOCCER_SOURCES
)


# Hypothesis strategies for generating valid test data
@st.composite
def valid_category_strategy(draw):
    """Generate valid category values."""
    return draw(st.sampled_from(['pokemon', 'hockey', 'soccer']))


@st.composite
def valid_topic_strategy(draw):
    """Generate valid topic strings."""
    return draw(st.text(min_size=10, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc')  # Exclude surrogates and control chars
    )))


@st.composite
def max_sources_strategy(draw):
    """Generate valid max_sources values."""
    return draw(st.integers(min_value=1, max_value=10))


# Property 2: Category-specific source consultation
# For any topic generation request for a specific category (Pokémon, Hockey, or Soccer),
# the system should consult the web sources designated for that category


@given(
    category=valid_category_strategy(),
    topic=st.one_of(valid_topic_strategy(), st.none()),
    max_sources=max_sources_strategy()
)
@settings(max_examples=100)
def test_property_2_category_specific_source_consultation(
    category: str,
    topic: str,
    max_sources: int
) -> None:
    """
    Feature: tcg-content-generator, Property 2: Category-specific source consultation
    For any topic generation request for a specific category (Pokémon, Hockey, or Soccer),
    the system should consult the web sources designated for that category.
    Validates: Requirements 1.3, 1.4, 1.5
    """
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Mock the CrewAI tools to avoid actual network requests
    with patch('src.tools.seo_tools.SerperDevTool'), \
         patch('src.tools.seo_tools.ScrapeWebsiteTool') as mock_scrape:
        
        # Setup mock scrape tool
        mock_scrape_instance = MagicMock()
        mock_scrape.return_value = mock_scrape_instance
        
        # Track which URLs were scraped
        scraped_urls = []
        
        def mock_scrape_run(website_url: str) -> str:
            """Mock scraping that tracks URLs."""
            scraped_urls.append(website_url)
            return f"Mock content from {website_url}"
        
        mock_scrape_instance.run.side_effect = mock_scrape_run
        
        # Create SEOTools instance
        seo_tools = SEOTools(config)
        
        # Call the category-specific scraping method
        result = seo_tools.scrape_category_sources(
            category=category,
            topic=topic,
            max_sources=max_sources
        )
        
        # Property: The result should indicate the correct category
        assert result['category'] == category.lower(), \
            f"Result should indicate category '{category}'"
        
        # Property: The system should consult sources from the correct category
        if category.lower() == 'pokemon':
            expected_sources = POKEMON_SOURCES
        elif category.lower() == 'hockey':
            expected_sources = HOCKEY_SOURCES
        elif category.lower() == 'soccer':
            expected_sources = SOCCER_SOURCES
        else:
            raise ValueError(f"Invalid category: {category}")
        
        # Property: All scraped URLs should be from the category-specific source list
        for url in scraped_urls:
            assert url in expected_sources, \
                f"Scraped URL '{url}' should be from {category} sources"
        
        # Property: The system should attempt to scrape up to max_sources
        # (may be less if sources fail, but should not exceed max_sources)
        assert len(result['sources']) <= max_sources, \
            f"Should not scrape more than {max_sources} sources"
        
        # Property: All successfully scraped sources should be in the result
        assert all(url in result['content'] for url in result['sources']), \
            "All sources in result should have content"
        
        # Property: Failed sources should not have content
        for failed_url in result.get('failed_sources', []):
            assert failed_url not in result['content'], \
                f"Failed source '{failed_url}' should not have content"


@given(
    category=valid_category_strategy(),
    max_sources=max_sources_strategy()
)
@settings(max_examples=100)
def test_property_2_pokemon_sources_consultation(
    category: str,
    max_sources: int
) -> None:
    """
    Feature: tcg-content-generator, Property 2: Category-specific source consultation
    Verify that Pokémon category consults Pokémon-specific sources.
    Validates: Requirements 1.3
    """
    if category.lower() != 'pokemon':
        # Skip non-Pokemon categories for this test
        return
    
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Mock the CrewAI tools
    with patch('src.tools.seo_tools.SerperDevTool'), \
         patch('src.tools.seo_tools.ScrapeWebsiteTool') as mock_scrape:
        
        mock_scrape_instance = MagicMock()
        mock_scrape.return_value = mock_scrape_instance
        
        scraped_urls = []
        
        def mock_scrape_run(website_url: str) -> str:
            scraped_urls.append(website_url)
            return f"Pokemon content from {website_url}"
        
        mock_scrape_instance.run.side_effect = mock_scrape_run
        
        # Create SEOTools and scrape Pokemon sources
        seo_tools = SEOTools(config)
        _ = seo_tools.scrape_pokemon_sources(max_sources=max_sources)
        
        # Property: Should only consult Pokemon-specific sources
        pokemon_source_domains = [
            'ebay.com', 'cardmarket.com', 'tcgplayer.com', 'pokebeach.com',
            'pokeguardian.com', 'pokemon.com', 'ign.com', 'pkmcards.fr',
            'limitlesstcg.com'
        ]
        
        for url in scraped_urls:
            assert any(domain in url.lower() for domain in pokemon_source_domains), \
                f"Pokemon scraping should only access Pokemon sources, got: {url}"
        
        # Property: Should not consult Hockey or Soccer sources
        hockey_domains = ['puckjunk.com', 'uncuthockey.com', 'allvintagecards.com']
        soccer_domains = ['soccercardshq.com', '130point.com', 'usfcards.fr']
        
        for url in scraped_urls:
            assert not any(domain in url.lower() for domain in hockey_domains), \
                f"Pokemon scraping should not access Hockey sources: {url}"
            assert not any(domain in url.lower() for domain in soccer_domains), \
                f"Pokemon scraping should not access Soccer sources: {url}"


@given(
    category=valid_category_strategy(),
    max_sources=max_sources_strategy()
)
@settings(max_examples=100)
def test_property_2_hockey_sources_consultation(
    category: str,
    max_sources: int
) -> None:
    """
    Feature: tcg-content-generator, Property 2: Category-specific source consultation
    Verify that Hockey category consults Hockey-specific sources.
    Validates: Requirements 1.4
    """
    if category.lower() != 'hockey':
        # Skip non-Hockey categories for this test
        return
    
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Mock the CrewAI tools
    with patch('src.tools.seo_tools.SerperDevTool'), \
         patch('src.tools.seo_tools.ScrapeWebsiteTool') as mock_scrape:
        
        mock_scrape_instance = MagicMock()
        mock_scrape.return_value = mock_scrape_instance
        
        scraped_urls = []
        
        def mock_scrape_run(website_url: str) -> str:
            scraped_urls.append(website_url)
            return f"Hockey content from {website_url}"
        
        mock_scrape_instance.run.side_effect = mock_scrape_run
        
        # Create SEOTools and scrape Hockey sources
        seo_tools = SEOTools(config)
        _ = seo_tools.scrape_hockey_sources(max_sources=max_sources)
        
        # Property: Should only consult Hockey-specific sources
        hockey_source_domains = [
            'ebay.com', 'comc.com', 'beckett.com', 'puckjunk.com',
            'allvintagecards.com', 'uncuthockey.com', 'bsportscards.com',
            'cherrycollectables.com'
        ]
        
        for url in scraped_urls:
            assert any(domain in url.lower() for domain in hockey_source_domains), \
                f"Hockey scraping should only access Hockey sources, got: {url}"
        
        # Property: Should not consult Pokemon or Soccer sources
        pokemon_domains = ['pokemon.com', 'pokebeach.com', 'pokeguardian.com', 'pkmcards.fr']
        soccer_domains = ['soccercardshq.com', '130point.com', 'usfcards.fr']
        
        for url in scraped_urls:
            assert not any(domain in url.lower() for domain in pokemon_domains), \
                f"Hockey scraping should not access Pokemon sources: {url}"
            assert not any(domain in url.lower() for domain in soccer_domains), \
                f"Hockey scraping should not access Soccer sources: {url}"


@given(
    category=valid_category_strategy(),
    max_sources=max_sources_strategy()
)
@settings(max_examples=100)
def test_property_2_soccer_sources_consultation(
    category: str,
    max_sources: int
) -> None:
    """
    Feature: tcg-content-generator, Property 2: Category-specific source consultation
    Verify that Soccer category consults Soccer-specific sources.
    Validates: Requirements 1.5
    """
    if category.lower() != 'soccer':
        # Skip non-Soccer categories for this test
        return
    
    # Create a mock config
    config = Config(
        neon_connection_string="postgresql://user:pass@host:5432/db",
        openai_api_key="sk-" + "x" * 40,
        serper_api_key="serper_" + "x" * 30
    )
    
    # Mock the CrewAI tools
    with patch('src.tools.seo_tools.SerperDevTool'), \
         patch('src.tools.seo_tools.ScrapeWebsiteTool') as mock_scrape:
        
        mock_scrape_instance = MagicMock()
        mock_scrape.return_value = mock_scrape_instance
        
        scraped_urls = []
        
        def mock_scrape_run(website_url: str) -> str:
            scraped_urls.append(website_url)
            return f"Soccer content from {website_url}"
        
        mock_scrape_instance.run.side_effect = mock_scrape_run
        
        # Create SEOTools and scrape Soccer sources
        seo_tools = SEOTools(config)
        _ = seo_tools.scrape_soccer_sources(max_sources=max_sources)
        
        # Property: Should only consult Soccer-specific sources
        soccer_source_domains = [
            'ebay.com', 'comc.com', 'beckett.com', 'soccercardshq.com',
            '130point.com', 'usfcards.fr', 'sportcard.fr'
        ]
        
        for url in scraped_urls:
            assert any(domain in url.lower() for domain in soccer_source_domains), \
                f"Soccer scraping should only access Soccer sources, got: {url}"
        
        # Property: Should not consult Pokemon or Hockey sources
        pokemon_domains = ['pokemon.com', 'pokebeach.com', 'pokeguardian.com', 'pkmcards.fr']
        hockey_domains = ['puckjunk.com', 'uncuthockey.com', 'allvintagecards.com']
        
        for url in scraped_urls:
            assert not any(domain in url.lower() for domain in pokemon_domains), \
                f"Soccer scraping should not access Pokemon sources: {url}"
            assert not any(domain in url.lower() for domain in hockey_domains), \
                f"Soccer scraping should not access Hockey sources: {url}"


def test_property_2_category_source_lists_are_distinct() -> None:
    """
    Feature: tcg-content-generator, Property 2: Category-specific source consultation
    Verify that each category has distinct source lists with no overlap
    in category-specific domains.
    Validates: Requirements 1.3, 1.4, 1.5
    """
    # Property: Pokemon sources should be distinct from Hockey and Soccer
    pokemon_specific = ['pokemon.com', 'pokebeach.com', 'pokeguardian.com', 
                       'pkmcards.fr', 'limitlesstcg.com', 'cardmarket.com/en/Pokemon']
    hockey_specific = ['puckjunk.com', 'uncuthockey.com', 'allvintagecards.com',
                      'bsportscards.com', 'cherrycollectables.com']
    soccer_specific = ['soccercardshq.com', '130point.com', 'usfcards.fr', 'sportcard.fr']
    
    # Check Pokemon sources
    for source in POKEMON_SOURCES:
        has_pokemon_domain = any(domain in source.lower() for domain in pokemon_specific)
        has_hockey_domain = any(domain in source.lower() for domain in hockey_specific)
        has_soccer_domain = any(domain in source.lower() for domain in soccer_specific)
        
        if has_pokemon_domain:
            assert not has_hockey_domain and not has_soccer_domain, \
                f"Pokemon source should not contain Hockey/Soccer domains: {source}"
    
    # Check Hockey sources
    for source in HOCKEY_SOURCES:
        has_pokemon_domain = any(domain in source.lower() for domain in pokemon_specific)
        has_hockey_domain = any(domain in source.lower() for domain in hockey_specific)
        has_soccer_domain = any(domain in source.lower() for domain in soccer_specific)
        
        if has_hockey_domain:
            assert not has_pokemon_domain and not has_soccer_domain, \
                f"Hockey source should not contain Pokemon/Soccer domains: {source}"
    
    # Check Soccer sources
    for source in SOCCER_SOURCES:
        has_pokemon_domain = any(domain in source.lower() for domain in pokemon_specific)
        has_hockey_domain = any(domain in source.lower() for domain in hockey_specific)
        has_soccer_domain = any(domain in source.lower() for domain in soccer_specific)
        
        if has_soccer_domain:
            assert not has_pokemon_domain and not has_hockey_domain, \
                f"Soccer source should not contain Pokemon/Hockey domains: {source}"

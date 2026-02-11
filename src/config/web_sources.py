"""
Category-specific web source mappings for the TCG Content Generator.

This module defines the authoritative web sources for each trading card category
(Pokémon, Hockey, Soccer) that agents should consult for research and topic generation.
"""

from typing import Dict, List


# Pokémon Cards Web Sources
POKEMON_SOURCES: List[Dict[str, str]] = [
    {
        "name": "eBay",
        "url": "https://www.ebay.com/b/Pokemon-Trading-Card-Games/2536/bn_1852",
        "type": "marketplace",
        "description": "Primary marketplace for Pokémon card sales and pricing data"
    },
    {
        "name": "Cardmarket",
        "url": "https://www.cardmarket.com/en/Pokemon",
        "type": "marketplace",
        "description": "European marketplace with comprehensive pricing and trends"
    },
    {
        "name": "TCGplayer",
        "url": "https://www.tcgplayer.com/search/pokemon/product",
        "type": "marketplace",
        "description": "Major US marketplace for TCG pricing and availability"
    },
    {
        "name": "Pokebeach",
        "url": "https://www.pokebeach.com",
        "type": "news",
        "description": "Leading Pokémon TCG news and set information"
    },
    {
        "name": "Pokeguardian",
        "url": "https://www.pokeguardian.com",
        "type": "news",
        "description": "Pokémon TCG news, reviews, and investment insights"
    },
    {
        "name": "Pokemon Official News",
        "url": "https://www.pokemon.com/us/pokemon-news",
        "type": "official",
        "description": "Official Pokémon news and announcements"
    },
    {
        "name": "IGN Pokémon TCG",
        "url": "https://www.ign.com/games/pokemon-trading-card-game",
        "type": "media",
        "description": "Gaming media coverage of Pokémon TCG"
    },
    {
        "name": "Pkmcards",
        "url": "https://www.pkmcards.fr",
        "type": "database",
        "description": "Comprehensive Pokémon card database and pricing"
    },
    {
        "name": "Limitless TCG",
        "type": "competitive",
        "description": "Competitive Pokémon TCG tournament data and meta analysis"
    },
    {
        "name": "Cardboard Connection",
        "url": "https://www.cardboardconnection.com/pokemon-cards",
        "type": "database",
        "description": "The most authoritative card set database and checklists"
    }
]


# Hockey Cards Web Sources
HOCKEY_SOURCES: List[Dict[str, str]] = [
    {
        "name": "eBay",
        "url": "https://www.ebay.com/b/Hockey-Trading-Cards/261328/bn_1852",
        "type": "marketplace",
        "description": "Primary marketplace for hockey card sales and pricing"
    },
    {
        "name": "COMC",
        "url": "https://www.comc.com/Hockey",
        "type": "marketplace",
        "description": "Check Out My Cards - major hockey card marketplace"
    },
    {
        "name": "Beckett Hockey",
        "url": "https://www.beckett.com/hockey",
        "type": "pricing",
        "description": "Industry-standard pricing guide and grading authority"
    },
    {
        "name": "Puckjunk",
        "url": "https://www.puckjunk.com",
        "type": "blog",
        "description": "Hockey card investment strategies and market analysis"
    },
    {
        "name": "All Vintage Cards Hockey Blog",
        "url": "https://www.allvintagecards.com/blog/hockey",
        "type": "blog",
        "description": "Vintage hockey card insights and collecting tips"
    },
    {
        "name": "Uncut Hockey",
        "url": "https://www.uncuthockey.com",
        "type": "news",
        "description": "Hockey card news and release information"
    },
    {
        "name": "BSportscards",
        "url": "https://www.bsportscards.com",
        "type": "marketplace",
        "description": "Hockey card marketplace and investment insights"
    },
    {
        "name": "Cherry Collectables",
        "type": "marketplace",
        "description": "Canadian hockey card marketplace and news"
    },
    {
        "name": "Cardboard Connection",
        "url": "https://www.cardboardconnection.com/sports-cards-sets/hockey-card-sets",
        "type": "database",
        "description": "The most authoritative card set database and checklists"
    }
]


# Soccer Cards Web Sources
SOCCER_SOURCES: List[Dict[str, str]] = [
    {
        "name": "eBay",
        "url": "https://www.ebay.com/b/Soccer-Trading-Cards/261329/bn_1852",
        "type": "marketplace",
        "description": "Primary marketplace for soccer card sales and pricing"
    },
    {
        "name": "COMC",
        "url": "https://www.comc.com/Soccer",
        "type": "marketplace",
        "description": "Check Out My Cards - soccer card marketplace"
    },
    {
        "name": "Beckett Soccer",
        "url": "https://www.beckett.com/soccer",
        "type": "pricing",
        "type": "pricing",
        "description": "Soccer card pricing guide and market data"
    },
    {
        "name": "Cardboard Connection",
        "url": "https://www.cardboardconnection.com/sports-cards-sets/soccer-card-sets",
        "type": "database",
        "description": "The most authoritative card set database and checklists"
    },
    {
        "name": "Soccer Cards HQ",
        "url": "https://www.soccercardshq.com",
        "type": "news",
        "description": "Soccer card news, reviews, and investment analysis"
    },
    {
        "name": "130point",
        "url": "https://www.130point.com",
        "type": "marketplace",
        "description": "European soccer card marketplace and pricing"
    },
    {
        "name": "USF Cards",
        "url": "https://www.usfcards.fr",
        "type": "marketplace",
        "description": "French soccer card marketplace and trends"
    },
    {
        "name": "Sportcard",
        "url": "https://www.sportcard.fr",
        "type": "marketplace",
        "description": "European sports card marketplace with soccer focus"
    },
    {
        "name": "Cartophilic Info Exchange",
        "url": "https://cartophilic-info-exch.blogspot.com",
        "type": "blog",
        "description": "Comprehensive reference for historical card releases"
    },
    {
        "name": "Cartes et Stickers",
        "url": "https://cartesetstickers.fr",
        "type": "marketplace",
        "description": "French marketplace for stickers and cards"
    },
    {
        "name": "Draken Davids",
        "url": "https://www.drakendavids.se/en/blogs/om-samlarkort",
        "type": "blog",
        "description": "Swedish blog with detailed collecting guides"
    },
    {
        "name": "Soccer Stickers FC",
        "url": "https://soccerstickersfc.net",
        "type": "news",
        "description": "News and checklists for soccer stickers and cards"
    },
    {
        "name": "Blowout Cards Soccer Forums",
        "url": "https://www.blowoutcards.com/sports-cards/football-cards/2026.html",
        "type": "community",
        "description": "Major community forum for new release discussions"
    },
    {
        "name": "The Card Collective",
        "url": "https://thecardcollective.dk/blogs/guides/guide-to-collecting-soccer-cards",
        "type": "blog",
        "description": "Danish card shop with excellent collecting guides"
    },
    {
        "name": "Buy Soccer Cards Online",
        "url": "https://buysoccercardsonline.com/blogs/blog-news",
        "type": "news",
        "description": "News on Adrenalyn XL and other gaming sets"
    },
    {
        "name": "Card Chasers MTL",
        "url": "https://www.cardchasersmtl.com/blogs/blog",
        "type": "blog",
        "description": "Investment guides and value unlocking tips"
    },
    {
        "name": "RL Sports Cards",
        "url": "https://rlsportscards.com/blogs/news",
        "type": "blog",
        "description": "Guides for new collectors and best buys"
    },
    {
        "name": "Sports Cards Pro",
        "url": "https://www.sportscardspro.com/category/soccer-cards",
        "type": "pricing",
        "description": "Price tracking and historical value data"
    }
]


# Category to Sources Mapping
CATEGORY_SOURCES: Dict[str, List[Dict[str, str]]] = {
    "pokemon": POKEMON_SOURCES,
    "hockey": HOCKEY_SOURCES,
    "soccer": SOCCER_SOURCES
}


def get_sources_for_category(category: str) -> List[Dict[str, str]]:
    """
    Get web sources for a specific category.
    
    Args:
        category: Category name (pokemon, hockey, or soccer)
        
    Returns:
        List of source dictionaries with name, url, type, and description
        
    Raises:
        ValueError: If category is not recognized
    """
    category_lower = category.lower()
    if category_lower not in CATEGORY_SOURCES:
        raise ValueError(
            f"Unknown category: {category}. "
            f"Valid options: {list(CATEGORY_SOURCES.keys())}"
        )
    return CATEGORY_SOURCES[category_lower]


def get_source_urls_for_category(category: str) -> List[str]:
    """
    Get just the URLs for a specific category.
    
    Args:
        category: Category name (pokemon, hockey, or soccer)
        
    Returns:
        List of source URLs
        
    Raises:
        ValueError: If category is not recognized
    """
    sources = get_sources_for_category(category)
    return [source["url"] for source in sources]


def get_sources_by_type(category: str, source_type: str) -> List[Dict[str, str]]:
    """
    Get sources for a category filtered by type.
    
    Args:
        category: Category name (pokemon, hockey, or soccer)
        source_type: Type of source (marketplace, news, blog, pricing, etc.)
        
    Returns:
        List of source dictionaries matching the type
        
    Raises:
        ValueError: If category is not recognized
    """
    sources = get_sources_for_category(category)
    return [source for source in sources if source["type"] == source_type]


def get_all_categories() -> List[str]:
    """
    Get list of all valid categories.
    
    Returns:
        List of category names
    """
    return list(CATEGORY_SOURCES.keys())


def get_marketplace_sources(category: str) -> List[Dict[str, str]]:
    """
    Get marketplace sources for a category (for pricing data).
    
    Args:
        category: Category name (pokemon, hockey, or soccer)
        
    Returns:
        List of marketplace source dictionaries
    """
    return get_sources_by_type(category, "marketplace")


def get_news_sources(category: str) -> List[Dict[str, str]]:
    """
    Get news sources for a category (for trending topics).
    
    Args:
        category: Category name (pokemon, hockey, or soccer)
        
    Returns:
        List of news source dictionaries
    """
    return get_sources_by_type(category, "news")

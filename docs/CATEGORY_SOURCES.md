# Trading Card Content Generator - Category Source Mappings

## Overview

This document provides comprehensive documentation of all web sources consulted by the Trading Card Content Generator for each trading card category. These sources are used during the Strategy Phase for topic generation and during the Execution Phase for research.

**Last Updated:** December 2025  
**Version:** 1.0

---

## Table of Contents
1. [Pokémon Cards Sources](#pokémon-cards-sources)
2. [Hockey Cards Sources](#hockey-cards-sources)
3. [Soccer Cards Sources](#soccer-cards-sources)
4. [Source Configuration](#source-configuration)
5. [Adding New Sources](#adding-new-sources)
6. [Source Health Monitoring](#source-health-monitoring)

---

## Pokémon Cards Sources

### Overview
Pokémon trading cards represent one of the most popular and valuable segments of the trading card market. Sources focus on market prices, investment trends, tournament data, and official news.

### Marketplace Sources

#### eBay
- **URL**: https://www.ebay.com/b/Pokemon-Cards/183454/bn_2311392
- **Purpose**: Real-time market prices, sold listings, trending cards
- **Data Extracted**: 
  - Current listings and prices
  - Recently sold items and final prices
  - Popular search terms
  - Price trends over time
- **Update Frequency**: Real-time
- **Reliability**: High (primary marketplace)
- **Notes**: Use sold listings for accurate market data

#### Cardmarket
- **URL**: https://www.cardmarket.com/en/Pokemon
- **Purpose**: European market prices and trends
- **Data Extracted**:
  - European market prices
  - Card availability
  - Price trends
  - Popular cards in EU market
- **Update Frequency**: Daily
- **Reliability**: High (primary EU marketplace)
- **Notes**: Prices in EUR, convert to USD for consistency

#### TCGplayer
- **URL**: https://www.tcgplayer.com/search/pokemon/product
- **Purpose**: North American market prices and inventory
- **Data Extracted**:
  - Market prices (low, mid, high)
  - Card availability
  - Price history
  - Set information
- **Update Frequency**: Real-time
- **Reliability**: High (primary US marketplace)
- **Notes**: Industry-standard pricing reference

### News and Information Sources

#### Pokebeach.com
- **URL**: https://www.pokebeach.com
- **Purpose**: Pokémon TCG news, spoilers, and analysis
- **Data Extracted**:
  - New set announcements
  - Card spoilers and reveals
  - Tournament results
  - Meta analysis
- **Update Frequency**: Daily
- **Reliability**: High (established community site)
- **Notes**: Excellent for upcoming releases and meta trends

#### Pokeguardian.com
- **URL**: https://www.pokeguardian.com
- **Purpose**: Investment analysis and market insights
- **Data Extracted**:
  - Investment recommendations
  - Market analysis
  - Price predictions
  - Grading information
- **Update Frequency**: Weekly
- **Reliability**: Medium-High (investment focused)
- **Notes**: Focus on investment-grade cards

#### Pokemon.com Official News
- **URL**: https://www.pokemon.com/us/pokemon-news
- **Purpose**: Official Pokémon Company announcements
- **Data Extracted**:
  - Official set releases
  - Tournament announcements
  - Product information
  - Official events
- **Update Frequency**: Weekly
- **Reliability**: High (official source)
- **Notes**: Authoritative source for official information

#### IGN Pokémon TCG Coverage
- **URL**: https://www.ign.com/games/pokemon-trading-card-game
- **Purpose**: Gaming news and reviews
- **Data Extracted**:
  - Set reviews
  - Product announcements
  - Industry news
  - Competitive scene coverage
- **Update Frequency**: Weekly
- **Reliability**: High (major gaming outlet)
- **Notes**: Good for mainstream coverage

### Community and Data Sources

#### Pkmcards.fr
- **URL**: https://www.pkmcards.fr
- **Purpose**: French Pokémon card database and community
- **Data Extracted**:
  - Card database information
  - French market trends
  - Community discussions
  - Set information
- **Update Frequency**: Daily
- **Reliability**: Medium (regional focus)
- **Notes**: Useful for European market insights

#### Limitlesstcg.com
- **URL**: https://www.limitlesstcg.com
- **Purpose**: Tournament results and meta analysis
- **Data Extracted**:
  - Tournament decklists
  - Meta game analysis
  - Card usage statistics
  - Player rankings
- **Update Frequency**: Daily (during tournament season)
- **Reliability**: High (competitive focus)
- **Notes**: Essential for competitive meta insights

---

## Hockey Cards Sources

### Overview
Hockey cards have a rich history and strong collector base, particularly in North America. Sources focus on vintage cards, player performance, and investment opportunities.

### Marketplace Sources

#### eBay
- **URL**: https://www.ebay.com/b/Hockey-Trading-Cards/261328/bn_1853415
- **Purpose**: Real-time market prices and sold listings
- **Data Extracted**:
  - Current listings and prices
  - Recently sold items
  - Vintage card prices
  - Rookie card trends
- **Update Frequency**: Real-time
- **Reliability**: High (primary marketplace)
- **Notes**: Strong vintage card market

#### COMC (Check Out My Cards)
- **URL**: https://www.comc.com/Hockey
- **Purpose**: Consignment marketplace and price data
- **Data Extracted**:
  - Market prices
  - Card availability
  - Historical sales data
  - Popular players
- **Update Frequency**: Real-time
- **Reliability**: High (established marketplace)
- **Notes**: Good for bulk purchases and consignment

#### Beckett.com
- **URL**: https://www.beckett.com/hockey
- **Purpose**: Pricing guides and grading services
- **Data Extracted**:
  - Price guide values
  - Grading information
  - Market reports
  - Industry news
- **Update Frequency**: Monthly (price guides)
- **Reliability**: High (industry standard)
- **Notes**: Authoritative pricing reference

### Investment and Analysis Sources

#### Puckjunk.com
- **URL**: https://www.puckjunk.com
- **Purpose**: Hockey card investment strategies and analysis
- **Data Extracted**:
  - Investment recommendations
  - Market analysis
  - Player performance correlation
  - Vintage card insights
- **Update Frequency**: Weekly
- **Reliability**: Medium-High (investment focused)
- **Notes**: Excellent for investment strategy content

#### All Vintage Cards Hockey Blog
- **URL**: https://www.allvintagecards.com/hockey
- **Purpose**: Vintage hockey card information and history
- **Data Extracted**:
  - Vintage card values
  - Historical context
  - Set information
  - Collecting guides
- **Update Frequency**: Weekly
- **Reliability**: High (vintage focus)
- **Notes**: Best source for vintage card content

#### Uncut Hockey
- **URL**: https://www.uncuthockey.com
- **Purpose**: Industry news and market insights
- **Data Extracted**:
  - Industry news
  - Product releases
  - Market trends
  - Interviews
- **Update Frequency**: Daily
- **Reliability**: Medium-High
- **Notes**: Good for industry perspective

### Retailer Sources

#### Bsportscards.com
- **URL**: https://www.bsportscards.com
- **Purpose**: Retailer inventory and pricing
- **Data Extracted**:
  - Product availability
  - Retail prices
  - New releases
  - Popular products
- **Update Frequency**: Daily
- **Reliability**: Medium (retailer perspective)
- **Notes**: Useful for retail market insights

#### Cherrycollectables.com
- **URL**: https://www.cherrycollectables.com
- **Purpose**: Canadian market and collectibles
- **Data Extracted**:
  - Canadian market prices
  - Product availability
  - Regional trends
  - Hockey memorabilia
- **Update Frequency**: Daily
- **Reliability**: Medium (regional focus)
- **Notes**: Important for Canadian market coverage

---

## Soccer Cards Sources

### Overview
Soccer (football) cards represent a growing international market with strong European presence. Sources focus on international players, emerging markets, and investment opportunities.

### Marketplace Sources

#### eBay
- **URL**: https://www.ebay.com/b/Soccer-Trading-Cards/261329/bn_1853416
- **Purpose**: International market prices and availability
- **Data Extracted**:
  - Current listings and prices
  - International sales
  - Player card trends
  - Regional variations
- **Update Frequency**: Real-time
- **Reliability**: High (primary marketplace)
- **Notes**: Strong international presence

#### COMC (Check Out My Cards)
- **URL**: https://www.comc.com/Soccer
- **Purpose**: Consignment marketplace for soccer cards
- **Data Extracted**:
  - Market prices
  - Player popularity
  - Set information
  - Historical data
- **Update Frequency**: Real-time
- **Reliability**: High (established marketplace)
- **Notes**: Growing soccer card inventory

### News and Information Sources

#### Beckett.com Soccer News
- **URL**: https://www.beckett.com/news/category/soccer
- **Purpose**: Soccer card news and market updates
- **Data Extracted**:
  - Product releases
  - Market news
  - Player spotlights
  - Investment insights
- **Update Frequency**: Weekly
- **Reliability**: High (industry authority)
- **Notes**: Authoritative soccer card coverage

#### Soccercardshq.com
- **URL**: https://www.soccercardshq.com
- **Purpose**: Soccer card community and information hub
- **Data Extracted**:
  - Market analysis
  - Player information
  - Set reviews
  - Collecting guides
- **Update Frequency**: Weekly
- **Reliability**: Medium-High (community focused)
- **Notes**: Good for community insights

#### 130point.com
- **URL**: https://www.130point.com
- **Purpose**: Soccer card community and marketplace
- **Data Extracted**:
  - Community discussions
  - Market trends
  - Player analysis
  - Set information
- **Update Frequency**: Daily
- **Reliability**: Medium (community driven)
- **Notes**: Active community engagement

### International Sources

#### Usfcards.fr
- **URL**: https://www.usfcards.fr
- **Purpose**: French soccer card market
- **Data Extracted**:
  - French market prices
  - European players
  - Regional trends
  - Set availability
- **Update Frequency**: Daily
- **Reliability**: Medium (regional focus)
- **Notes**: Important for European market

#### Sportcard.fr
- **URL**: https://www.sportcard.fr
- **Purpose**: French sports card marketplace
- **Data Extracted**:
  - European market prices
  - Soccer card availability
  - Regional trends
  - International players
- **Update Frequency**: Daily
- **Reliability**: Medium (regional focus)
- **Notes**: Covers broader European market

---

## Source Configuration

### Configuration File Location
Category-specific sources are configured in:
```
src/config/web_sources.py
```

### Configuration Format

```python
# Pokémon Cards Sources
POKEMON_SOURCES = [
    {
        "name": "eBay Pokémon",
        "url": "https://www.ebay.com/b/Pokemon-Cards/183454/bn_2311392",
        "type": "marketplace",
        "priority": "high",
        "rate_limit": 60,  # requests per minute
        "timeout": 30,  # seconds
        "retry_attempts": 3
    },
    {
        "name": "Cardmarket",
        "url": "https://www.cardmarket.com/en/Pokemon",
        "type": "marketplace",
        "priority": "high",
        "rate_limit": 30,
        "timeout": 30,
        "retry_attempts": 3
    },
    # ... more sources
]

# Hockey Cards Sources
HOCKEY_SOURCES = [
    {
        "name": "eBay Hockey",
        "url": "https://www.ebay.com/b/Hockey-Trading-Cards/261328/bn_1853415",
        "type": "marketplace",
        "priority": "high",
        "rate_limit": 60,
        "timeout": 30,
        "retry_attempts": 3
    },
    # ... more sources
]

# Soccer Cards Sources
SOCCER_SOURCES = [
    {
        "name": "eBay Soccer",
        "url": "https://www.ebay.com/b/Soccer-Trading-Cards/261329/bn_1853416",
        "type": "marketplace",
        "priority": "high",
        "rate_limit": 60,
        "timeout": 30,
        "retry_attempts": 3
    },
    # ... more sources
]
```

### Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| name | string | Human-readable source name | Required |
| url | string | Source URL | Required |
| type | string | Source type (marketplace, news, community) | Required |
| priority | string | Priority level (high, medium, low) | medium |
| rate_limit | integer | Max requests per minute | 60 |
| timeout | integer | Request timeout in seconds | 30 |
| retry_attempts | integer | Max retry attempts | 3 |

---

## Adding New Sources

### Step 1: Identify Source

1. Verify source is reliable and regularly updated
2. Check robots.txt for scraping permissions
3. Identify data extraction points
4. Test source accessibility

### Step 2: Add to Configuration

Edit `src/config/web_sources.py`:

```python
# Add to appropriate category list
POKEMON_SOURCES.append({
    "name": "New Pokémon Source",
    "url": "https://www.example.com/pokemon",
    "type": "marketplace",
    "priority": "medium",
    "rate_limit": 30,
    "timeout": 30,
    "retry_attempts": 3
})
```

### Step 3: Test Source

```python
# Test source accessibility
from src.tools.seo_tools import SEOTools

seo_tools = SEOTools(config)
result = seo_tools.scrape_pokemon_sources()
print(f"Successfully scraped: {result}")
```

### Step 4: Update Documentation

1. Add source to this document
2. Update AGENT_STRUCTURE.md if needed
3. Document any special considerations

### Step 5: Monitor Performance

- Check logs for scraping errors
- Monitor rate limit compliance
- Verify data quality
- Track source availability

---

## Source Health Monitoring

### Monitoring Metrics

**Per Source:**
- Success rate (successful scrapes / total attempts)
- Average response time
- Error rate
- Data quality score

**System-Wide:**
- Total sources available
- Sources currently failing
- Average scraping time
- Rate limit violations

### Health Check Script

```python
# Check source health
from src.tools.seo_tools import SEOTools
from src.config.settings import Config

config = Config()
seo_tools = SEOTools(config)

# Test all sources
health_report = seo_tools.check_source_health()
print(health_report)
```

### Troubleshooting Failed Sources

**Common Issues:**

1. **Rate Limiting**
   - Reduce scraping frequency
   - Implement exponential backoff
   - Use multiple IP addresses

2. **Website Structure Changes**
   - Update scraping selectors
   - Implement robust parsing
   - Add fallback strategies

3. **Access Restrictions**
   - Check robots.txt compliance
   - Use appropriate User-Agent
   - Implement CAPTCHA handling

4. **Network Issues**
   - Increase timeout values
   - Implement retry logic
   - Use alternative DNS

### Source Rotation Strategy

**Priority Levels:**

- **High Priority**: Primary sources, always attempted first
- **Medium Priority**: Secondary sources, used if primary fails
- **Low Priority**: Tertiary sources, used as last resort

**Rotation Logic:**
1. Attempt all high-priority sources
2. If insufficient data, attempt medium-priority sources
3. If still insufficient, attempt low-priority sources
4. Log any sources that failed
5. Update source health metrics

---

## Best Practices

### Scraping Ethics

1. **Respect robots.txt**: Always check and follow robots.txt rules
2. **Rate Limiting**: Don't overwhelm servers with requests
3. **User-Agent**: Use descriptive User-Agent header
4. **Caching**: Cache results to minimize redundant requests
5. **Attribution**: Credit sources in generated content

### Data Quality

1. **Validation**: Validate extracted data before use
2. **Freshness**: Prefer recent data over stale data
3. **Consistency**: Cross-reference data across multiple sources
4. **Accuracy**: Verify prices and facts when possible
5. **Completeness**: Ensure all required fields are extracted

### Performance Optimization

1. **Parallel Requests**: Scrape multiple sources concurrently (within rate limits)
2. **Caching**: Cache frequently accessed data
3. **Compression**: Use gzip compression for responses
4. **Connection Pooling**: Reuse HTTP connections
5. **Timeout Management**: Set appropriate timeouts

---

## Maintenance Schedule

### Daily
- Monitor source availability
- Check error logs
- Verify data quality

### Weekly
- Review source performance metrics
- Update source priorities based on reliability
- Test new sources

### Monthly
- Audit all sources for continued relevance
- Update source configurations
- Review and update documentation

### Quarterly
- Comprehensive source evaluation
- Add new sources as needed
- Remove unreliable sources
- Update scraping strategies

---

## Support

For questions or issues related to category sources:

1. Check PROBLEMS.md for known source issues
2. Review logs/tcg_generator.log for scraping errors
3. Test source accessibility manually
4. Contact support with source name and error details

---

## Appendix

### Source Type Definitions

- **Marketplace**: Sites where cards are bought and sold (eBay, COMC, etc.)
- **News**: Sites providing news and announcements (Pokebeach, IGN, etc.)
- **Community**: Community-driven sites and forums (130point, etc.)
- **Data**: Card databases and reference sites (Pkmcards.fr, etc.)
- **Investment**: Investment analysis and recommendations (Puckjunk, etc.)

### Priority Level Guidelines

- **High**: Essential sources, always consulted
- **Medium**: Important sources, consulted if high-priority sources insufficient
- **Low**: Supplementary sources, consulted as needed

### Rate Limit Guidelines

- **60 req/min**: Major marketplaces (eBay, COMC)
- **30 req/min**: News sites and communities
- **10 req/min**: Smaller sites and blogs

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Maintained By:** TCG Content Generator Team

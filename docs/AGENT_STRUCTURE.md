# Trading Card Content Generator - Agent Structure

**Generated**: 2025-12-14 02:56:50

## Overview

The Trading Card Content Generator is a sophisticated multi-agent AI system that automates the creation of investment-focused articles about trading cards across three categories: Pokémon, Hockey, and Soccer. The system employs a two-phase orchestration approach with five specialized AI agents working in concert.

**Key Features:**
- Two-phase workflow: Strategy (topic generation) → Execution (article creation)
- Five specialized agents: Strategist, Researcher, Writer, Editor, Archivist
- Sequential processing: One topic at a time for predictable resource usage
- Neon PostgreSQL database via Kiro Power as single source of truth
- Context7 MCP integration for up-to-date library documentation
- Category-specific web source consultation for market insights
- SEO optimization using SerperDevTool for SERP data and Google Trends
- Comprehensive error handling with retry logic (max 3 attempts)
- Automatic documentation generation and problem tracking

## System Architecture

```mermaid
graph TB
    %% User Interface Layer
    UI[Streamlit UI<br/>User Interface]
    
    %% Orchestration Layer
    Orchestrator[Orchestrator<br/>Two-Phase Coordinator]
    
    %% Phase 1: Strategy
    StrategyPhase[Strategy Phase<br/>Topic Generation & Deduplication]
    Strategist[Strategist Agent<br/>Topic Generation, SEO Research,<br/>Web Scraping, Deduplication]
    
    %% Phase 2: Execution
    ExecutionPhase[Execution Phase<br/>Sequential Article Creation]
    ContentCrew[ContentCrew<br/>Per-Topic Pipeline]
    
    %% Five Specialized Agents
    Researcher[Researcher Agent<br/>Information Gathering<br/>from Category Sources]
    Writer[Writer Agent<br/>Investment-Focused<br/>Article Drafting]
    Editor[Editor Agent<br/>Content Refinement<br/>& Optimization]
    Archivist[Archivist Agent<br/>Database Persistence]
    
    %% Context Management
    ContextMgr[Context Manager<br/>Agent Memory &<br/>Conversation History]
    
    %% External Integrations
    NeonDB[Neon DB Client<br/>PostgreSQL Interface]
    KiroPower[Kiro Power<br/>Database Integration Layer]
    Neon[(Neon PostgreSQL<br/>Single Source of Truth)]
    
    Context7[Context7 MCP<br/>Library Documentation]
    
    %% SEO and Web Tools
    SEOTools[SEO Tools<br/>SerperDevTool]
    ScrapeTools[Web Scraping<br/>ScrapeWebsiteTool]
    
    %% Category-Specific Sources
    WebSources[Category-Specific<br/>Web Sources]
    Pokemon[Pokémon Sources<br/>eBay, Cardmarket, TCGplayer<br/>Pokebeach, Pokeguardian<br/>Pokemon.com, IGN TCG<br/>Pkmcards.fr, Limitlesstcg]
    Hockey[Hockey Sources<br/>eBay, COMC, Beckett<br/>Puckjunk, All Vintage Cards<br/>Uncut Hockey, Bsportscards<br/>Cherrycollectables]
    Soccer[Soccer Sources<br/>eBay, COMC, Beckett Soccer<br/>Soccercardshq, 130point<br/>Usfcards.fr, Sportcard.fr]
    
    %% Documentation
    Docs[Documentation Manager]
    DocFiles[Documentation Files<br/>DOCUMENTATION.md<br/>PROBLEMS.md<br/>HOWTO.md]
    
    %% Main Flow Connections
    UI --> Orchestrator
    Orchestrator --> StrategyPhase
    Orchestrator --> ExecutionPhase
    
    %% Strategy Phase Flow
    StrategyPhase --> Strategist
    Strategist --> NeonDB
    Strategist --> SEOTools
    Strategist --> ScrapeTools
    Strategist --> Context7
    Strategist --> WebSources
    
    %% Execution Phase Flow
    ExecutionPhase --> ContentCrew
    ContentCrew --> Researcher
    ContentCrew --> Writer
    ContentCrew --> Editor
    ContentCrew --> Archivist
    
    %% Agent Interactions
    Researcher --> SEOTools
    Researcher --> ScrapeTools
    Researcher --> Context7
    Researcher --> WebSources
    Researcher --> ContextMgr
    
    Writer --> ContextMgr
    Writer --> Context7
    
    Editor --> ContextMgr
    Editor --> Context7
    
    Archivist --> NeonDB
    Archivist --> ContextMgr
    
    %% Web Sources Breakdown
    WebSources --> Pokemon
    WebSources --> Hockey
    WebSources --> Soccer
    
    %% Database Integration
    NeonDB --> KiroPower
    KiroPower --> Neon
    
    %% Documentation Flow
    Orchestrator --> Docs
    StrategyPhase --> Docs
    ContentCrew --> Docs
    Docs --> DocFiles
    
    %% Styling
    classDef phaseClass fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
    classDef agentClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef dbClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef toolClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef sourceClass fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    
    class StrategyPhase,ExecutionPhase phaseClass
    class Strategist,Researcher,Writer,Editor,Archivist agentClass
    class NeonDB,KiroPower,Neon dbClass
    class SEOTools,ScrapeTools,Context7,ContextMgr toolClass
    class WebSources,Pokemon,Hockey,Soccer sourceClass
```


## Two-Phase Workflow Sequence

```mermaid
sequenceDiagram
    participant UI as Streamlit UI
    participant Orch as Orchestrator
    participant SP as Strategy Phase
    participant Strat as Strategist Agent
    participant DB as Neon DB (via Kiro Power)
    participant SEO as SEO Tools (Serper)
    participant Scrape as Web Scraping
    participant C7 as Context7 MCP
    participant EP as Execution Phase
    participant CC as ContentCrew
    participant R as Researcher
    participant W as Writer
    participant E as Editor
    participant A as Archivist
    participant CM as Context Manager
    
    Note over UI,CM: PHASE 1: STRATEGY (Topic Generation)
    
    UI->>Orch: Start Generation<br/>(5 Pokémon, 3 Hockey, 2 Soccer)
    Orch->>SP: Execute Strategy Phase
    SP->>Strat: Initialize Strategist
    
    Strat->>DB: Query ALL Existing Topics
    DB-->>Strat: Return Existing Topics List
    
    Strat->>SEO: Get SERP Data & Google Trends
    SEO-->>Strat: Return SEO Insights
    
    Strat->>Scrape: Scrape Category Sources
    Scrape-->>Strat: Return Trending Topics
    
    Strat->>C7: Get Library Documentation
    C7-->>Strat: Return Documentation
    
    Strat->>Strat: Generate Topic Candidates<br/>with SEO Scores
    Strat->>Strat: Deduplicate Against<br/>Existing Topics
    
    Strat-->>SP: Return 10 Unique Topics<br/>(JSON List)
    SP-->>Orch: Topics Ready
    
    Note over UI,CM: PHASE 2: EXECUTION (Sequential Article Creation)
    
    Orch->>EP: Execute with Topic List
    
    loop For Each Topic (Sequential, One at a Time)
        EP->>CC: Instantiate ContentCrew<br/>for Topic
        CC->>CM: Initialize Context
        
        Note over CC,CM: Research Phase
        CC->>R: Execute Research
        R->>SEO: Get SEO Keywords
        R->>Scrape: Scrape Category Sources
        R->>C7: Get Technical Docs
        R->>CM: Store Research Results
        
        Note over CC,CM: Writing Phase
        CC->>W: Execute Writing
        W->>CM: Retrieve Research
        W->>C7: Get Best Practices
        W->>CM: Store Draft Article
        
        Note over CC,CM: Editing Phase
        CC->>E: Execute Editing
        E->>CM: Retrieve Draft
        E->>C7: Get Style Guidelines
        E->>CM: Store Final Article
        
        Note over CC,CM: Archiving Phase
        CC->>A: Execute Archiving
        A->>CM: Retrieve Final Article
        A->>DB: Store Article in Neon
        DB-->>A: Confirm Storage
        
        CC->>CM: Clear Context
        CC-->>EP: Topic Complete
    end
    
    EP-->>Orch: All Topics Complete
    Orch-->>UI: Display Results
```


## Data Flow

```mermaid
graph LR
    %% Data Sources
    ExistingTopics[(Existing Topics<br/>in Neon DB)]
    WebData[Web Sources<br/>Category-Specific]
    SEOData[SEO Data<br/>SERP & Trends]
    LibDocs[Library Docs<br/>Context7 MCP]
    
    %% Strategy Phase Data Flow
    ExistingTopics -->|Query| Strategist
    WebData -->|Scrape| Strategist
    SEOData -->|Fetch| Strategist
    LibDocs -->|Retrieve| Strategist
    Strategist -->|Generate & Deduplicate| TopicList[Topic List<br/>JSON Format]
    
    %% Execution Phase Data Flow
    TopicList -->|Sequential| ContentCrew
    
    %% Research Data Flow
    ContentCrew -->|Topic| Researcher
    WebData -->|Scrape| Researcher
    SEOData -->|Keywords| Researcher
    LibDocs -->|Technical| Researcher
    Researcher -->|Research Results| Context[Context Manager]
    
    %% Writing Data Flow
    Context -->|Research| Writer
    LibDocs -->|Best Practices| Writer
    Writer -->|Draft Article| Context
    
    %% Editing Data Flow
    Context -->|Draft| Editor
    LibDocs -->|Style Guide| Editor
    Editor -->|Final Article| Context
    
    %% Archiving Data Flow
    Context -->|Final Article| Archivist
    Archivist -->|Store| NeonDB[(Neon Database<br/>via Kiro Power)]
    
    %% Documentation Flow
    Strategist -.->|Log Events| DocMgr[Documentation<br/>Manager]
    ContentCrew -.->|Log Events| DocMgr
    DocMgr -.->|Write| DocFiles[DOCUMENTATION.md<br/>PROBLEMS.md]
    
    %% Styling
    classDef dataSource fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef storage fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class ExistingTopics,WebData,SEOData,LibDocs dataSource
    class Strategist,Researcher,Writer,Editor,Archivist process
    class Context,NeonDB,DocFiles storage
```



## Two-Phase Orchestration Workflow

### Phase 1: Strategy Phase (Topic Generation)

**Objective**: Generate unique, SEO-optimized topics by researching web sources and deduplicating against existing database records.

**Process:**
1. **Pre-Query Database**: Query Neon database for ALL existing topics
2. **SEO Research**: Use SerperDevTool to get SERP data, Google Trends, and keywords
3. **Web Scraping**: Scrape category-specific sources for trending topics
4. **Topic Generation**: Generate topic candidates with SEO scores
5. **Deduplication**: Filter out topics that exist in database
6. **Output**: Return JSON-serializable Python list of 10 unique topics

**Default Distribution:**
- 5 Pokémon topics
- 3 Hockey topics
- 2 Soccer topics
- Total: 10 articles

**Error Handling:**
- Maximum 3 retry attempts
- Log failures to PROBLEMS.md
- Continue with partial results if some categories fail

### Phase 2: Execution Phase (Sequential Article Creation)

**Objective**: Create high-quality investment-focused articles for each topic, one at a time.

**Process:**
1. **Sequential Loop**: Process topics one at a time (not parallel)
2. **ContentCrew Instantiation**: Create fresh ContentCrew for each topic
3. **Agent Pipeline**: Execute Research → Write → Edit → Archive
4. **Context Management**: Maintain context within each ContentCrew
5. **Database Persistence**: Store completed article in Neon
6. **Context Cleanup**: Clear context between topics

**Per-Topic Pipeline:**
1. **Research**: Gather information from category sources
2. **Write**: Generate investment-focused draft article
3. **Edit**: Refine and optimize content
4. **Archive**: Store in Neon database via Kiro Power

**Error Handling:**
- Maximum 3 retry attempts per topic
- Log failures to PROBLEMS.md
- Mark failed topics and continue to next
- Maintain progress for resumability

**Why Sequential?**
- Predictable resource usage
- Easier debugging and monitoring
- Respects API rate limits
- Prevents overwhelming external services
- Clear progress tracking



## Agent Details

### Five Specialized Agents

#### 1. Strategist Agent
**Role**: Topic generation, SEO research, web scraping, and deduplication

**Responsibilities:**
- Query Neon database for ALL existing topics BEFORE generation
- Use SerperDevTool for SERP data, Google Trends, and keywords
- Scrape category-specific web sources using ScrapeWebsiteTool
- Generate topic candidates with SEO scores
- Deduplicate against existing topics in database
- Return JSON-serializable Python list of unique topics

**Tools:**
- SerperDevTool (SEO research)
- ScrapeWebsiteTool (web scraping)
- Context7Client (library documentation)
- NeonDBClient (database queries)

**Output**: List of 10 unique topics (default: 5 Pokémon, 3 Hockey, 2 Soccer)

#### 2. Researcher Agent
**Role**: Information gathering from category-specific sources

**Responsibilities:**
- Gather detailed information about the topic
- Consult category-specific web sources
- Extract investment insights and market data
- Identify SEO keywords for content optimization
- Use Context7 MCP for technical documentation

**Tools:**
- SerperDevTool (SEO keywords)
- ScrapeWebsiteTool (category sources)
- Context7Client (technical docs)
- ContextManager (store results)

**Output**: ResearchResult with sources, key points, investment insights, SEO keywords

#### 3. Writer Agent
**Role**: Investment-focused article drafting

**Responsibilities:**
- Generate draft article based on research findings
- Incorporate SEO keywords naturally
- Focus on investment insights and market analysis
- Follow best practices from Context7 documentation
- Maintain consistent tone and style

**Tools:**
- ContextManager (retrieve research)
- Context7Client (best practices)
- OpenAI API (content generation)

**Output**: DraftArticle with content (minimum 500 words)

#### 4. Editor Agent
**Role**: Content refinement and optimization

**Responsibilities:**
- Review and refine draft article
- Enhance clarity and readability
- Optimize for SEO without keyword stuffing
- Ensure investment insights are prominent
- Apply style guidelines from Context7

**Tools:**
- ContextManager (retrieve draft)
- Context7Client (style guidelines)
- OpenAI API (content refinement)

**Output**: EditedArticle with refined content and improvement notes

#### 5. Archivist Agent
**Role**: Database persistence and context storage

**Responsibilities:**
- Store completed article in Neon database
- Save research sources and metadata
- Persist conversation context
- Update topic status to 'completed'
- Handle database errors with retry logic

**Tools:**
- NeonDBClient (database operations)
- ContextManager (retrieve final article)

**Output**: ArchivedContent with database record ID



## Integration Details

### Neon Database via Kiro Power

The system uses Neon PostgreSQL as the single source of truth for all data:

**Connection Flow:**
1. Application connects to Neon DB through Kiro Power integration layer
2. Kiro Power manages connection pooling and authentication
3. All queries use parameterized statements for security
4. Automatic retry logic with exponential backoff (max 3 retries)

**Data Storage:**
- **Topics Table**: Stores all generated topics with UNIQUE constraint on title
- **Content Table**: Stores completed articles with JSONB metadata
- **Context Table**: Stores agent conversation history

**Key Operations:**
- `query_all_topics()`: Retrieves ALL existing topics for deduplication
- `create_topic()`: Inserts new topic with validation
- `create_content()`: Stores completed article with metadata
- `update_status()`: Updates processing status

### Context7 MCP Integration

Context7 MCP provides up-to-date library documentation to all agents:

**Usage Pattern:**
1. Agent requests documentation for a specific library
2. Context7Client resolves library name to Context7-compatible ID
3. Client fetches documentation in appropriate mode (code/info)
4. Documentation is cached for subsequent requests
5. If Context7 fails, agent continues without documentation (logged as warning)

**Modes:**
- **Code Mode**: API references, code examples, function signatures
- **Info Mode**: Conceptual guides, architecture, best practices

**Agents Using Context7:**
- **Strategist**: Library documentation for topic generation
- **Researcher**: Technical documentation for research
- **Writer**: Best practices for article structure
- **Editor**: Style guidelines for content refinement

### SEO Tools Integration

**SerperDevTool** provides:
- SERP (Search Engine Results Page) data
- Google Trends information
- Keyword research and search volume
- Related queries and topics

**ScrapeWebsiteTool** provides:
- Content extraction from category-specific sources
- Trending topics and market data
- Investment insights and analysis
- Real-time market information

**Error Handling:**
- Rate limiting with exponential backoff
- Fallback to alternative sources on failure
- Request caching to minimize redundant calls
- Maximum 3 retry attempts per source



## Category-Specific Web Sources

The system consults different web sources based on the trading card category:

### Pokémon Cards Sources

| Source | Purpose | URL Pattern |
|--------|---------|-------------|
| eBay | Market prices, trending cards | ebay.com |
| Cardmarket | European market data | cardmarket.com |
| TCGplayer | US market prices | tcgplayer.com |
| Pokebeach | News and releases | pokebeach.com |
| Pokeguardian | Investment insights | pokeguardian.com |
| Pokemon.com | Official news | pokemon.com/us/pokemon-news |
| IGN Pokémon TCG | Reviews and analysis | ign.com |
| Pkmcards.fr | French market data | pkmcards.fr |
| Limitlesstcg | Tournament data | limitlesstcg.com |

### Hockey Cards Sources

| Source | Purpose | URL Pattern |
|--------|---------|-------------|
| eBay | Market prices, trending cards | ebay.com |
| COMC | Market data and sales | comc.com |
| Beckett | Pricing and grading | beckett.com |
| Puckjunk | Investment strategies | puckjunk.com |
| All Vintage Cards | Historical data | allvintagecards.com |
| Uncut Hockey | News and analysis | uncuthockey.com |
| Bsportscards | Market insights | bsportscards.com |
| Cherrycollectables | Canadian market | cherrycollectables.com |

### Soccer Cards Sources

| Source | Purpose | URL Pattern |
|--------|---------|-------------|
| eBay | Market prices, trending cards | ebay.com |
| COMC | Market data and sales | comc.com |
| Beckett Soccer | Pricing and news | beckett.com |
| Soccercardshq | Investment insights | soccercardshq.com |
| 130point | Market analysis | 130point.com |
| Usfcards.fr | French market data | usfcards.fr |
| Sportcard.fr | European market | sportcard.fr |


## Error Handling and Retry Logic

### Retry Strategy

All operations implement retry logic with exponential backoff:

**Retry Schedule:**
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- After 3 attempts: Mark as failed and continue

**Retry Scope:**
- Strategy Phase: Max 3 retries for entire phase
- Execution Phase: Max 3 retries per topic
- Database Operations: Max 3 retries per operation
- Web Scraping: Max 3 retries per source
- Agent Execution: Max 3 retries per agent

### Error Categories

1. **External Service Failures**: Neon DB, OpenAI API, web sources, Context7 MCP
2. **Agent Execution Failures**: Invalid output, timeouts, exceptions
3. **Data Validation Failures**: Pydantic validation errors
4. **Resource Exhaustion**: Memory limits, disk space, rate limits

### Logging

All errors and significant events are logged to:
- **DOCUMENTATION.md**: Timestamped log of significant events
- **PROBLEMS.md**: Active issues with status (active, resolved, blocked)
- **Console**: Real-time log output for monitoring

## Configuration

### Environment Variables

```bash
# Database
NEON_CONNECTION_STRING=postgresql://user:password@host/database
KIRO_POWER_NEON=neon

# AI APIs
OPENAI_API_KEY=your_openai_key

# SEO and Web Scraping
SERPER_API_KEY=your_serper_dev_api_key

# Configuration
LOG_LEVEL=INFO
MAX_RETRIES=3
PYLINT_MIN_SCORE=8.0

# Topic Distribution (optional)
POKEMON_TOPICS=5
HOCKEY_TOPICS=3
SOCCER_TOPICS=2
```

### Default Topic Distribution

The system generates 10 articles by default:
- **5 Pokémon topics**: Focus on TCG market and investment
- **3 Hockey topics**: Focus on vintage and modern cards
- **2 Soccer topics**: Focus on emerging market opportunities

This distribution can be customized via the Streamlit UI or environment variables.

## Technology Stack

### Core Technologies
- **CrewAI**: Multi-agent orchestration framework
- **Streamlit**: Interactive user interface
- **Neon PostgreSQL**: Serverless database (via Kiro Power)
- **Context7 MCP**: Library documentation integration
- **Pydantic**: Data validation and type safety
- **Pylint**: Code quality assurance (minimum 8.0/10)
- **Hypothesis**: Property-based testing

### External Services
- **OpenAI API**: LLM for content generation
- **Serper.dev**: SEO research (SERP data, Google Trends)
- **Web Sources**: Category-specific market data

## Data Models

All data structures use Pydantic for validation:

### Topic Model
```python
class Topic(BaseModel):
    id: uuid.UUID
    title: str  # 10-200 characters
    category: str  # pokemon|hockey|soccer
    created_at: datetime
    status: str  # pending|in_progress|completed|failed
```

### Content Model
```python
class Content(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    topic_title: str
    category: str
    final_content: str  # minimum 500 characters
    research_sources: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    status: str
```

## Database Schema

### Topics Table
- Stores all generated topics
- UNIQUE constraint on title for deduplication
- Indexed on title, category, and status

### Content Table
- Stores completed articles
- JSONB columns for flexible metadata
- Foreign key to topics table

### Context Table
- Stores agent conversation history
- JSONB for agent outputs
- Indexed on topic_id and agent_name

## Performance Considerations

### Sequential Processing
- **Current**: One topic at a time
- **Benefit**: Predictable resource usage, easier debugging
- **Trade-off**: Slower than parallel processing
- **Future**: Worker pool for parallel processing (if needed)

### Caching Strategy
- Web scraping results cached to avoid redundant requests
- Context7 documentation cached for frequently accessed libraries
- Database queries use prepared statements for performance

### Resource Management
- In-memory context cleared between topics
- Connection pooling managed by Neon
- Rate limiting for external API calls

## Monitoring and Observability

### Metrics to Track
- Topics processed per hour
- Average processing time per topic per category
- Agent success/failure rates
- API call counts and latencies
- Database query performance
- Web scraping success rates
- Retry attempt counts
- Error rates by category

### Health Checks
- Neon database connectivity (startup)
- Kiro Power availability (startup)
- Context7 MCP connectivity (startup)
- Periodic health check endpoint
- Memory and CPU usage monitoring

## Documentation Files

The system maintains four key documentation files:

1. **AGENT_STRUCTURE.md** (this file): System architecture and agent details
2. **DOCUMENTATION.md**: Timestamped log of significant events
3. **PROBLEMS.md**: Active issues and error logs
4. **HOWTO.md**: Setup and usage instructions

All documentation is automatically generated and maintained by the DocumentationManager component.

## Development Workflow

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Code Quality
```bash
# Run Pylint (minimum 8.0/10)
pylint src/ --min-score=8.0

# Run tests
pytest tests/

# Run property tests
pytest tests/property/
```

### Running the System
```bash
# Start Streamlit UI
streamlit run app.py

# Access at http://localhost:8501
```

## Future Enhancements

### Scalability
- Worker pool for parallel topic processing
- Redis for distributed context management
- Message queue (Celery) for async processing
- Caching layer for web scraping results

### Features
- Custom topic distribution per run
- Multi-language support
- Advanced SEO analytics
- A/B testing for content variations
- Automated content scheduling

---

*This documentation is automatically generated. Last updated: 2025-12-14 02:56:50*

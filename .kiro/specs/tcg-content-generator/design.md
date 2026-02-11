# Design Document

## Overview

The Trading Card Content Generator is a sophisticated multi-agent system built on CrewAI that orchestrates investment-focused article creation for three trading card categories: Pokémon cards, Hockey cards, and Soccer cards. The system architecture separates strategic planning (topic generation with web research and deduplication) from tactical execution (sequential article creation), enabling efficient resource utilization and high-quality content production.

The system employs five specialized AI agents working in concert: a Strategist for topic generation and validation, a Researcher for information gathering from category-specific sources, a Writer for investment-focused article drafting, an Editor for refinement, and an Archivist for persistence. All agents integrate with Context7 MCP for library documentation, operate within a managed context environment, and interact with Neon PostgreSQL database as the authoritative data store through Kiro Power integration. The system uses Pydantic for data validation and Pylint for code quality assurance.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    UI[Streamlit UI] --> Orchestrator[Orchestrator]
    Orchestrator --> StrategyPhase[Strategy Phase]
    Orchestrator --> ExecutionPhase[Execution Phase]
    
    StrategyPhase --> Strategist[Strategist Agent]
    Strategist --> WebSources[Category Web Sources]
    Strategist --> NeonDB[Neon DB Client]
    Strategist --> Context7[Context7 MCP]
    
    ExecutionPhase --> ContentCrew[ContentCrew Sequential Loop]
    ContentCrew --> Researcher[Researcher Agent]
    ContentCrew --> Writer[Writer Agent]
    ContentCrew --> Editor[Editor Agent]
    ContentCrew --> Archivist[Archivist Agent]
    
    Researcher --> WebSources
    Researcher --> Context7
    Writer --> ContextMgr[Context Manager]
    Writer --> Context7
    Editor --> ContextMgr
    Editor --> Context7
    Archivist --> NeonDB
    
    WebSources --> Pokemon[Pokémon Sources]
    WebSources --> Hockey[Hockey Sources]
    WebSources --> Soccer[Soccer Sources]
    
    NeonDB --> KiroPower[Kiro Power: Neon]
    KiroPower --> Neon[(Neon PostgreSQL)]
    
    Docs[Documentation Files] --> HOWTO[HOWTO.md]
    Docs --> Documentation[DOCUMENTATION.md]
    Docs --> Problems[PROBLEMS.md]
```

### Category-Specific Web Sources

**Pokémon Cards Sources:**
- eBay, Cardmarket, TCGplayer
- Pokebeach.com, Pokeguardian.com
- Pokemon.com/us/pokemon-news
- IGN.com Pokémon TCG
- Pkmcards.fr, Limitlesstcg.com

**Hockey Cards Sources:**
- eBay, COMC, Beckett.com
- Puckjunk.com (investment strategies)
- All Vintage Cards Hockey Blog
- Uncut Hockey
- Bsportscards.com, Cherrycollectables.com

**Soccer Cards Sources:**
- eBay, COMC
- Beckett.com Soccer News
- Soccercardshq.com, 130point.com
- Usfcards.fr, Sportcard.fr

### Two-Phase Orchestration

**Phase 1: Strategy Phase**
- Single execution per run
- Strategist agent queries Neon database for ALL existing topics BEFORE generating new ones
- Generates topic candidates by researching category-specific web sources
- Default distribution: 5 Pokémon + 3 Hockey + 2 Soccer = 10 total topics
- Performs deduplication by comparing candidates against existing Neon records
- Returns topics as JSON-serializable Python list of strings
- Maximum 3 retry attempts if errors occur

**Phase 2: Execution Phase**
- Sequential processing: ONE topic at a time (not parallel)
- For each topic, instantiates a fresh ContentCrew
- Each ContentCrew executes pipeline: Research → Write → Edit → Archive
- Context is maintained within each ContentCrew instance
- Completed articles are persisted to Neon database via Kiro Power
- Loop continues until all topics are processed
- Maximum 3 retry attempts per topic if errors occur
- Failed topics are logged to PROBLEMS.md and skipped

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant UI as Streamlit UI
    participant Orch as Orchestrator
    participant Strat as Strategy Phase
    participant DB as Neon DB Client
    participant Web as Web Sources
    participant C7 as Context7 MCP
    participant Exec as Execution Phase
    participant CC as ContentCrew
    
    UI->>Orch: Start Generation (5 Pokémon, 3 Hockey, 2 Soccer)
    Orch->>Strat: Execute Strategy Phase
    Strat->>DB: Query ALL Existing Topics
    DB-->>Strat: Return Existing Topics List
    Strat->>Web: Research Category Sources
    Web-->>Strat: Return Trending Topics
    Strat->>C7: Get Library Documentation
    C7-->>Strat: Return Documentation
    Strat->>Strat: Generate & Deduplicate Topics
    Strat-->>Orch: Return 10 Unique Topics (JSON list)
    
    Orch->>Exec: Execute with Topic List
    loop For Each Topic (Sequential)
        Exec->>CC: Instantiate ContentCrew for Topic
        CC->>CC: Research → Write → Edit
        CC->>DB: Archive Article
        DB-->>CC: Confirm Storage
        CC-->>Exec: Complete
    end
    Exec-->>Orch: All Topics Complete
    Orch-->>UI: Display Results
```

## Components and Interfaces

### 1. Orchestrator (`orchestrator.py`)

**Responsibilities:**
- Coordinate the two-phase workflow
- Manage phase transitions
- Handle error recovery with max 3 retries
- Report progress to UI
- Update DOCUMENTATION.md and PROBLEMS.md

**Interface:**
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Orchestrator:
    def __init__(self, config: Config, neon_client: NeonDBClient):
        """Initialize orchestrator with configuration and Neon database client."""
        
    def run(self, topic_distribution: Dict[str, int] = None) -> Dict[str, Any]:
        """Execute the complete two-phase workflow.
        
        Args:
            topic_distribution: Dict with keys 'pokemon', 'hockey', 'soccer' and int values
                               Default: {'pokemon': 5, 'hockey': 3, 'soccer': 2}
            
        Returns:
            Dictionary containing execution summary and results
        """
        
    def _execute_strategy_phase(self, distribution: Dict[str, int]) -> List[str]:
        """Execute Phase 1: Topic generation with web research and deduplication."""
        
    def _execute_execution_phase(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Execute Phase 2: Sequential article creation for each topic."""
        
    def _log_to_documentation(self, event: str, details: str) -> None:
        """Append event to DOCUMENTATION.md with timestamp."""
        
    def _log_to_problems(self, issue: str, status: str) -> None:
        """Log issue to PROBLEMS.md with status."""
```

### 2. Strategy Phase (`agents/strategist.py`)

**Responsibilities:**
- Query Neon database for existing topics BEFORE generation
- Use SEO tools (Serper.dev) to get SERP data, Google Trends, and keywords
- Research category-specific web sources for trending topics using CrewAI ScrapeWebsiteTool
- Generate topic candidates based on distribution and SEO insights
- Perform deduplication against Neon database
- Return JSON-serializable Python list of strings
- Use Context7 MCP for library documentation

**Tools:**
- SerperDevTool: For SERP data, Google Trends, and keyword research
- ScrapeWebsiteTool: For scraping category-specific sources
- Context7Client: For library documentation

**Interface:**
```python
from pydantic import BaseModel, validator
from typing import List, Set, Dict
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

class SEOInsights(BaseModel):
    """Pydantic model for SEO insights."""
    keywords: List[str]
    trends: List[str]
    search_volume: Dict[str, int]
    serp_data: Dict[str, Any]

class TopicCandidate(BaseModel):
    """Pydantic model for topic candidate."""
    title: str = Field(..., min_length=10, max_length=200)
    category: str = Field(..., regex="^(pokemon|hockey|soccer)$")
    sources: List[str]
    seo_score: float = Field(default=0.0, ge=0.0, le=100.0)
    keywords: List[str] = []
    
    @validator('title')
    def title_must_be_unique(cls, v):
        """Validate title format."""
        return v.strip()

class StrategyPhase:
    def __init__(self, neon_client: NeonDBClient, context7_client: Context7Client, 
                 serper_tool: SerperDevTool, scrape_tool: ScrapeWebsiteTool, config: Config):
        """Initialize strategy phase with Neon database, Context7, and SEO tools."""
        
    def generate_topics(self, distribution: Dict[str, int]) -> List[str]:
        """Generate deduplicated topic list with SEO optimization.
        
        Args:
            distribution: Dict with 'pokemon', 'hockey', 'soccer' counts
            
        Returns:
            JSON-serializable Python list of topic strings
        """
        
    def _fetch_existing_topics(self) -> Set[str]:
        """Query Neon database for ALL existing topics before generation."""
        
    def _get_seo_insights(self, category: str) -> SEOInsights:
        """Get SERP data, Google Trends, and keywords using Serper.dev."""
        
    def _research_web_sources(self, category: str, count: int, seo_insights: SEOInsights) -> List[TopicCandidate]:
        """Research category-specific web sources using ScrapeWebsiteTool and SEO insights."""
        
    def _deduplicate(self, candidates: List[str], existing: Set[str]) -> List[str]:
        """Remove duplicates from candidate list."""
```

### 3. ContentCrew (`agents/content_crew.py`)

**Responsibilities:**
- Instantiate and coordinate all five agents for ONE topic
- Manage agent execution pipeline sequentially
- Maintain context throughout the workflow
- Handle agent failures with max 3 retries
- Integrate Context7 MCP for all agents

**Interface:**
```python
from pydantic import BaseModel
from typing import Dict, Any

class ContentCrewResult(BaseModel):
    """Pydantic model for ContentCrew result."""
    topic: str
    article: str
    metadata: Dict[str, Any]
    success: bool
    retry_count: int = 0

class ContentCrew:
    def __init__(self, topic: str, category: str, context_manager: ContextManager, 
                 neon_client: NeonDBClient, context7_client: Context7Client, config: Config):
        """Initialize ContentCrew for a specific topic."""
        
    def execute(self, max_retries: int = 3) -> ContentCrewResult:
        """Execute the complete article creation pipeline with retry logic.
        
        Returns:
            ContentCrewResult with article and metadata
        """
        
    def _setup_agents(self) -> None:
        """Initialize all five agents with proper configuration."""
        
    def _run_pipeline(self) -> Dict[str, Any]:
        """Execute Research → Write → Edit → Archive pipeline."""
```

### 4. Individual Agents

**Researcher Agent (`agents/researcher.py`):**
```python
from pydantic import BaseModel
from typing import List, Dict, Any
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

class ResearchResult(BaseModel):
    """Pydantic model for research output."""
    topic: str
    category: str
    sources: List[str]
    key_points: List[str]
    investment_insights: List[str]
    seo_keywords: List[str]

class ResearcherAgent:
    def __init__(self, context_manager: ContextManager, context7_client: Context7Client,
                 serper_tool: SerperDevTool, scrape_tool: ScrapeWebsiteTool):
        """Initialize researcher with context, Context7, and research tools."""
        
    def research(self, topic: str, category: str) -> ResearchResult:
        """Gather information from category-specific sources using SEO and scraping tools.
        
        Returns:
            ResearchResult with findings, sources, investment insights, and SEO keywords
        """
```

**Writer Agent (`agents/writer.py`):**
```python
from pydantic import BaseModel

class DraftArticle(BaseModel):
    """Pydantic model for draft article."""
    topic: str
    content: str = Field(..., min_length=500)
    word_count: int

class WriterAgent:
    def __init__(self, context_manager: ContextManager, context7_client: Context7Client, config: Config):
        """Initialize writer with context and Context7."""
        
    def write(self, topic: str, research: ResearchResult) -> DraftArticle:
        """Generate investment-focused draft article based on research.
        
        Returns:
            DraftArticle with content
        """
```

**Editor Agent (`agents/editor.py`):**
```python
from pydantic import BaseModel

class EditedArticle(BaseModel):
    """Pydantic model for edited article."""
    topic: str
    content: str = Field(..., min_length=500)
    improvements: List[str]

class EditorAgent:
    def __init__(self, context_manager: ContextManager, context7_client: Context7Client, config: Config):
        """Initialize editor with context and Context7."""
        
    def edit(self, draft: DraftArticle, topic: str) -> EditedArticle:
        """Refine and optimize the draft article.
        
        Returns:
            EditedArticle with refined content
        """
```

**Archivist Agent (`agents/archivist.py`):**
```python
from pydantic import BaseModel
import uuid

class ArchivedContent(BaseModel):
    """Pydantic model for archived content."""
    id: uuid.UUID
    topic: str
    category: str
    content: str
    created_at: str

class ArchivistAgent:
    def __init__(self, neon_client: NeonDBClient, context_manager: ContextManager):
        """Initialize archivist with Neon database client."""
        
    def archive(self, article: EditedArticle, topic: str, category: str, metadata: Dict[str, Any]) -> ArchivedContent:
        """Store completed article in Neon database.
        
        Returns:
            ArchivedContent with database record ID
        """
```

### 5. Context Manager (`utils/context_manager.py`)

**Responsibilities:**
- Store and retrieve agent outputs
- Maintain conversation history
- Provide context isolation between ContentCrew instances
- Support context persistence

**Interface:**
```python
from pydantic import BaseModel
from typing import Any, List, Dict, Optional
from datetime import datetime

class AgentOutput(BaseModel):
    """Pydantic model for agent output."""
    agent_name: str
    output: Any
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class ContextManager:
    def __init__(self):
        """Initialize empty context storage."""
        
    def add_context(self, agent_name: str, output: Any, metadata: Dict[str, Any] = None) -> None:
        """Store output from an agent."""
        
    def get_context(self, agent_name: str = None) -> Any:
        """Retrieve context from specific agent or all agents."""
        
    def get_full_history(self) -> List[AgentOutput]:
        """Get complete conversation history."""
        
    def clear(self) -> None:
        """Clear all context (used between ContentCrew instances)."""
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for persistence."""
```

### 6. Neon Database Client (`tools/neon_db_client.py`)

**Responsibilities:**
- Provide abstraction over Neon PostgreSQL database via Kiro Power
- Handle connection management and retries
- Execute SQL queries through Kiro Power interface
- Validate data before persistence using Pydantic
- Store topics as JSONB for efficient querying

**Interface:**
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid

class TopicRecord(BaseModel):
    """Pydantic model for topic record."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    category: str
    created_at: str
    status: str = "pending"

class ContentRecord(BaseModel):
    """Pydantic model for content record."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    topic_id: uuid.UUID
    topic_title: str
    category: str
    final_content: str
    research_sources: List[str]
    metadata: Dict[str, Any]
    created_at: str
    status: str = "completed"

class NeonDBClient:
    def __init__(self, config: Config):
        """Initialize Neon database client using Kiro Power."""
        
    def query_all_topics(self) -> List[str]:
        """Retrieve ALL existing topic titles from Neon database.
        
        Returns:
            List of topic title strings
        """
        
    def create_topic(self, record: TopicRecord) -> uuid.UUID:
        """Create a new topic record in Neon database."""
        
    def create_content(self, record: ContentRecord) -> uuid.UUID:
        """Create a new content record in Neon database."""
        
    def update_status(self, record_id: uuid.UUID, status: str) -> None:
        """Update the status of a content record."""
        
    def verify_connection(self) -> bool:
        """Test connectivity to Neon database via Kiro Power."""
        
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query through Kiro Power with parameterization."""
```

### 7. Context7 MCP Client (`tools/context7_client.py`)

**Responsibilities:**
- Provide access to library documentation via Context7 MCP
- Resolve library IDs
- Fetch documentation for code and info modes
- Cache frequently accessed documentation

**Interface:**
```python
from pydantic import BaseModel
from typing import Optional

class Context7Client:
    def __init__(self, config: Config):
        """Initialize Context7 MCP client."""
        
    def resolve_library(self, library_name: str) -> Optional[str]:
        """Resolve library name to Context7-compatible ID."""
        
    def get_docs(self, library_id: str, topic: str = None, mode: str = "code") -> str:
        """Fetch documentation for a library."""
```

### 8. Configuration Model (`config/settings.py`)

**Interface:**
```python
from pydantic import BaseModel, Field, validator
from typing import Dict

class Config(BaseModel):
    """System configuration with Pydantic validation."""
    neon_connection_string: str = Field(..., min_length=10)
    openai_api_key: str = Field(..., min_length=20)
    serper_api_key: str = Field(..., min_length=20)
    kiro_power_name: str = "neon"
    max_retries: int = Field(default=3, ge=1, le=5)
    default_topic_distribution: Dict[str, int] = Field(
        default={'pokemon': 5, 'hockey': 3, 'soccer': 2}
    )
    agent_personas: Dict[str, str]
    logging_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    pylint_min_score: float = Field(default=8.0, ge=0.0, le=10.0)
    
    @validator('default_topic_distribution')
    def validate_distribution(cls, v):
        """Validate topic distribution sums to reasonable number."""
        total = sum(v.values())
        if total < 1 or total > 50:
            raise ValueError("Total topics must be between 1 and 50")
        return v
    
    class Config:
        """Pydantic config."""
        validate_assignment = True
```

### 9. Documentation Manager (`utils/documentation_manager.py`)

**Responsibilities:**
- Manage DOCUMENTATION.md file
- Manage PROBLEMS.md file
- Append timestamped entries
- Update issue statuses

**Interface:**
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class DocumentationEntry(BaseModel):
    """Pydantic model for documentation entry."""
    timestamp: datetime
    event: str
    details: str

class ProblemEntry(BaseModel):
    """Pydantic model for problem entry."""
    timestamp: datetime
    issue: str
    status: Literal["active", "resolved", "blocked"]
    details: str

class DocumentationManager:
    def __init__(self, docs_dir: str = "docs"):
        """Initialize documentation manager."""
        
    def log_event(self, event: str, details: str) -> None:
        """Append event to DOCUMENTATION.md."""
        
    def log_problem(self, issue: str, status: str, details: str) -> None:
        """Log problem to PROBLEMS.md."""
        
    def update_problem_status(self, issue: str, new_status: str) -> None:
        """Update problem status in PROBLEMS.md."""
```

### 10. Streamlit UI (`app.py`)

**Responsibilities:**
- Provide user interface for system interaction
- Display real-time progress updates
- Show generated article summaries
- Handle user input for topic distribution
- Display DOCUMENTATION.md and PROBLEMS.md content

**Interface:**
```python
def main():
    """Main Streamlit application entry point."""
    
def render_strategy_phase_ui() -> Dict[str, int]:
    """Render UI for topic distribution configuration.
    
    Returns:
        Dict with 'pokemon', 'hockey', 'soccer' counts
    """
    
def render_execution_progress(current_topic: str, completed: int, total: int, category: str) -> None:
    """Display execution phase progress."""
    
def render_results(results: List[ContentCrewResult]) -> None:
    """Display final results and article summaries."""
    
def render_documentation_viewer() -> None:
    """Display DOCUMENTATION.md and PROBLEMS.md content."""
```

## Data Models

All data models use Pydantic for validation and type safety.

### Topic Model
```python
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class Topic(BaseModel):
    """Represents a content topic."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str = Field(..., min_length=10, max_length=200)
    category: str = Field(..., regex="^(pokemon|hockey|soccer)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", regex="^(pending|in_progress|completed|failed)$")
    
    class Config:
        validate_assignment = True
```

### Content Model
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime

class Content(BaseModel):
    """Represents generated article content."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    topic_id: uuid.UUID
    topic_title: str
    category: str
    draft: str = Field(..., min_length=100)
    final_content: str = Field(..., min_length=500)
    research_sources: List[str]
    metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="completed")
    
    class Config:
        validate_assignment = True
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Pre-generation database query
*For any* Strategy Phase execution, the system should query Neon database for ALL existing topics BEFORE generating new topic candidates.
**Validates: Requirements 1.1**

### Property 2: Category-specific source consultation
*For any* topic generation request for a specific category (Pokémon, Hockey, or Soccer), the system should consult the web sources designated for that category.
**Validates: Requirements 1.2, 1.3, 1.4**

### Property 3: Topic deduplication completeness
*For any* set of proposed topics and existing topics in Neon database, the final topic list should contain no topics that exist in the database.
**Validates: Requirements 1.5**

### Property 4: JSON-serializable topic format
*For any* Strategy Phase output, topics should be structured as a JSON-serializable Python list of strings.
**Validates: Requirements 1.6**

### Property 5: Sequential topic processing
*For any* topic list, the Execution Phase should process topics one at a time in the exact order they appear in the list.
**Validates: Requirements 2.1, 2.3**

### Property 6: ContentCrew agent completeness
*For any* ContentCrew instantiation, exactly five agents (Strategist, Researcher, Writer, Editor, Archivist) should be initialized.
**Validates: Requirements 2.2, 3.1**

### Property 7: Retry limit enforcement
*For any* topic that fails processing, the system should retry up to 3 times, and if still failing, mark it as failed and continue to the next topic.
**Validates: Requirements 2.5, 2.6**

### Property 8: Context7 MCP integration
*For any* agent request for library documentation, the system should use Context7 MCP to retrieve the information.
**Validates: Requirements 3.2**

### Property 9: Category-specific research
*For any* Researcher Agent execution, the system should gather information from the web sources specific to the topic's category and use Context7 MCP for technical documentation.
**Validates: Requirements 3.3**

### Property 10: Agent pipeline execution
*For any* topic processed by a ContentCrew, all five agents should execute in sequence (Strategist → Researcher → Writer → Editor → Archivist), with each agent producing output.
**Validates: Requirements 3.4, 3.5, 3.6**

### Property 11: Pydantic model usage
*For any* data structure (Topic, Content, AgentContext, Config), the system should use Pydantic models with validation.
**Validates: Requirements 11.1, 11.4, 11.5**

### Property 12: Type hint completeness
*For any* function definition, the system should include type hints for all parameters and return values.
**Validates: Requirements 11.2**

### Property 13: Pylint code quality
*For any* Python module, running Pylint should produce a score of at least 8.0/10.
**Validates: Requirements 11.3**

### Property 14: Documentation file updates
*For any* significant event, the system should append a timestamped entry to DOCUMENTATION.md.
**Validates: Requirements 12.2**

### Property 15: Problem logging
*For any* error or issue encountered, the system should log it to PROBLEMS.md with status information.
**Validates: Requirements 12.4, 12.5**

### Property 16: Topic serialization format
*For any* topic serialization operation, the system should use JSON format and maintain Python list of strings structure.
**Validates: Requirements 13.1, 13.2, 13.4, 13.5**

## Error Handling

### Error Categories

**1. External Service Failures**
- Neon database unavailable or connection timeout
- OpenAI API failures or quota exceeded
- Web scraping failures (category sources unreachable)
- Context7 MCP connectivity issues
- Kiro Power connectivity issues

**Strategy:**
- Implement exponential backoff with retry logic (max 3 retries per operation)
- Log all external service errors to PROBLEMS.md with full context
- For Neon database failures during startup, halt execution immediately
- For Neon database failures during execution, attempt to cache locally and retry
- For AI API failures, log error and skip to next topic after 3 retries
- For web scraping failures, use fallback sources or skip that source
- For Context7 MCP failures, continue without documentation (log warning)
- For Kiro Power failures, verify power is activated and retry

**2. Agent Execution Failures**
- Agent produces invalid output
- Agent times out
- Agent raises unexpected exception
- Agent exceeds retry limit (3 attempts)

**Strategy:**
- Wrap all agent executions in try-catch blocks
- Log agent failures with full stack trace to PROBLEMS.md
- Retry failed agent up to 3 times with exponential backoff
- After 3 failures, mark topic as failed in Neon database
- Continue to next topic without halting entire pipeline
- Store partial results if any agents completed successfully

**3. Data Validation Failures**
- Invalid topic format (Pydantic validation fails)
- Missing required fields in content
- Malformed database records
- JSON serialization errors

**Strategy:**
- Validate all data at system boundaries using Pydantic models
- Log validation errors with specific field information to PROBLEMS.md
- Reject invalid data and continue processing
- Provide clear error messages for debugging
- Use Pydantic's built-in error messages for consistency

**4. Resource Exhaustion**
- Memory limits exceeded
- Disk space full
- API rate limits hit
- Database connection pool exhausted

**Strategy:**
- Monitor resource usage throughout execution
- Implement graceful degradation (reduce batch sizes)
- Pause execution when rate limits are hit (exponential backoff)
- Log resource exhaustion events to PROBLEMS.md
- Provide recovery mechanisms (resume from last successful topic)

**5. Loop Limit Exceeded**
- Retry attempts exceed 3 iterations
- Infinite loop detection

**Strategy:**
- Enforce maximum 3 retry attempts per operation
- Log loop limit exceeded to PROBLEMS.md
- Mark operation as failed and continue
- Implement circuit breaker pattern for repeated failures

### Error Recovery Patterns

**Checkpoint Pattern:**
- After each topic completes, save progress to Neon database
- Store list of completed topics
- On restart, skip already-completed topics
- Resume from last incomplete topic

**Circuit Breaker Pattern:**
- Track failure rates for external services
- If failure rate exceeds threshold (e.g., 50% over 10 requests), open circuit
- Stop making requests for cooldown period (e.g., 60 seconds)
- Attempt single test request after cooldown
- Close circuit if test succeeds

**Retry with Exponential Backoff:**
- First retry: wait 1 second
- Second retry: wait 2 seconds
- Third retry: wait 4 seconds
- After 3 retries, mark as failed

**Fallback Pattern:**
- For non-critical operations, provide fallback behavior
- Example: If primary web source fails, use alternative source
- Example: If Context7 MCP fails, continue without documentation
- Log all fallback activations to DOCUMENTATION.md

## Testing Strategy

### Unit Testing Approach

The system will use **pytest** as the primary testing framework. Unit tests will focus on:

**Component-Level Tests:**
- Individual agent logic (Strategist, Researcher, Writer, Editor, Archivist)
- Context Manager operations (add, retrieve, clear, serialize)
- Neon database client methods (query, create, update)
- Context7 MCP client methods (resolve, get_docs)
- Orchestrator phase transitions
- Configuration loading and Pydantic validation
- Documentation Manager file operations
- Kiro Power integration

**Integration Points:**
- Agent-to-Context Manager interactions
- ContentCrew pipeline execution
- Neon database connectivity via Kiro Power
- Context7 MCP integration
- Error handling and recovery mechanisms with retry logic
- Documentation file updates

**Edge Cases:**
- Empty topic lists
- Neon database connection failures
- Kiro Power unavailability
- Context7 MCP failures
- Invalid agent outputs
- Malformed configuration
- Resource exhaustion scenarios
- Retry limit exceeded scenarios
- Invalid Pydantic model data

**Code Quality Tests:**
- Pylint score verification (minimum 8.0/10)
- Type hint coverage verification
- Pydantic model validation tests

**Example Unit Test Structure:**
```python
from pydantic import ValidationError
import pytest

def test_topic_model_validation():
    """Test that Topic model validates data correctly."""
    # Valid topic
    topic = Topic(title="Best Pokémon Cards 2024", category="pokemon")
    assert topic.category == "pokemon"
    
    # Invalid category
    with pytest.raises(ValidationError):
        Topic(title="Invalid", category="invalid_category")

def test_deduplication_removes_existing_topics():
    """Test that deduplication correctly filters existing topics."""
    existing = {"Topic A", "Topic B"}
    candidates = ["Topic A", "Topic C", "Topic B", "Topic D"]
    result = deduplicate(candidates, existing)
    assert result == ["Topic C", "Topic D"]
    
def test_retry_limit_enforcement():
    """Test that retry limit is enforced after 3 attempts."""
    crew = ContentCrew(topic="Test", category="pokemon", ...)
    result = crew.execute(max_retries=3)
    assert result.retry_count <= 3
```

### Property-Based Testing Approach

The system will use **Hypothesis** for property-based testing in Python. Property tests will verify universal correctness properties across many randomly generated inputs.

**Configuration:**
- Each property test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate valid test data
- Each property test will be tagged with a comment referencing the design document property

**Property Test Coverage:**

Each correctness property from the design document will be implemented as a single property-based test. The tests will use Hypothesis to generate random but valid inputs and verify the property holds across all generated cases.

**Example Property Test Structure:**
```python
from hypothesis import given, strategies as st
from hypothesis.strategies import composite

@composite
def topic_list_strategy(draw):
    """Generate valid topic lists."""
    categories = ["pokemon", "hockey", "soccer"]
    return draw(st.lists(
        st.tuples(
            st.text(min_size=10, max_size=200),
            st.sampled_from(categories)
        ),
        min_size=1,
        max_size=20
    ))

@given(
    candidates=st.lists(st.text(min_size=10, max_size=200)),
    existing=st.sets(st.text(min_size=10, max_size=200))
)
def test_property_3_deduplication_completeness(candidates, existing):
    """
    Feature: tcg-content-generator, Property 3: Topic deduplication completeness
    For any set of proposed topics and existing topics, the output should contain
    no topics that exist in the existing set.
    """
    result = deduplicate(candidates, existing)
    assert not any(topic in existing for topic in result)

@given(topics=topic_list_strategy())
def test_property_5_sequential_processing(topics):
    """
    Feature: tcg-content-generator, Property 5: Sequential topic processing
    For any topic list, topics should be processed in the order they appear.
    """
    processed_order = []
    for topic in topics:
        processed_order.append(topic)
    assert processed_order == topics
```

### Test Organization

```
tests/
├── unit/
│   ├── test_context_manager.py
│   ├── test_orchestrator.py
│   ├── test_strategy_phase.py
│   ├── test_content_crew.py
│   ├── test_agents.py
│   ├── test_neon_db_client.py
│   ├── test_context7_client.py
│   ├── test_documentation_manager.py
│   └── test_pydantic_models.py
├── property/
│   ├── test_deduplication_properties.py
│   ├── test_execution_properties.py
│   ├── test_retry_properties.py
│   ├── test_serialization_properties.py
│   └── test_validation_properties.py
├── integration/
│   ├── test_end_to_end_flow.py
│   ├── test_neon_integration.py
│   ├── test_context7_integration.py
│   └── test_kiro_power_integration.py
├── code_quality/
│   ├── test_pylint_scores.py
│   ├── test_type_hints.py
│   └── test_pydantic_coverage.py
├── fixtures/
│   ├── sample_topics.json
│   ├── sample_content.json
│   ├── mock_web_responses.json
│   └── mock_neon_data.json
└── conftest.py  # Shared fixtures and configuration
```

### Testing Best Practices

1. **Isolation:** Each test should be independent and not rely on external state
2. **Mocking:** Use mocks for external services (Neon, OpenAI, web sources, Context7) in unit tests
3. **Real Integration:** Integration tests should use real Neon test database and Context7 MCP
4. **Fast Feedback:** Unit tests should run in < 5 seconds total
5. **Property Coverage:** Every correctness property must have a corresponding property test
6. **Tag Compliance:** All property tests must include the feature name and property number in comments
7. **Deterministic:** Tests should produce consistent results across runs
8. **Clear Failures:** Test failures should provide clear diagnostic information
9. **Pydantic Validation:** Test both valid and invalid data with Pydantic models
10. **Retry Logic:** Test retry mechanisms with controlled failures

## Implementation Notes

### Technology Stack Decisions

**CrewAI Framework:**
- Chosen for its built-in agent orchestration capabilities
- Provides task management and agent coordination out of the box
- Supports custom tools and memory management
- Active community and good documentation
- Supports sequential task execution (critical for our one-at-a-time processing)

**Streamlit for UI:**
- Rapid development of interactive interfaces
- Built-in support for real-time updates
- Easy integration with Python backend
- No frontend framework knowledge required
- Good for displaying documentation files

**Neon PostgreSQL via Kiro Power:**
- Serverless PostgreSQL with excellent performance
- Accessible through Kiro Power for seamless integration
- SQL-based queries for complex data operations
- JSONB support for flexible topic storage
- Automatic scaling and connection pooling
- Strong data consistency guarantees

**Context7 MCP:**
- Provides up-to-date library documentation
- Reduces hallucination by grounding in real documentation
- Supports both code and info modes
- Good for technical accuracy in articles

**Pydantic:**
- Industry-standard data validation for Python
- Type-safe data structures
- Automatic validation on assignment
- Clear error messages
- JSON serialization support

**Pylint:**
- Comprehensive Python code quality checker
- Enforces PEP 8 style guidelines
- Detects code smells and potential bugs
- Configurable scoring system

**Hypothesis for Property Testing:**
- Industry-standard property-based testing for Python
- Powerful strategy system for generating test data
- Automatic shrinking of failing examples
- Good integration with pytest

### Performance Considerations

**Sequential Processing Trade-offs:**
- Sequential processing ensures predictable resource usage
- Easier to debug and monitor progress
- Prevents overwhelming external APIs with parallel requests
- Future optimization: Implement parallel processing with worker pool (if needed)
- Consider rate limits when implementing parallelization

**Context Management:**
- In-memory context is fast but limited by RAM
- For large-scale deployments, consider Redis for context storage
- Implement context size limits to prevent memory issues
- Clear context between ContentCrew instances to prevent memory leaks

**Database Connection Management:**
- Neon provides connection pooling automatically
- Use prepared statements for better performance
- Implement connection retry logic for transient failures
- Cache frequently accessed data to reduce database load
- Use database indexes on topic titles for fast deduplication queries
- Use JSONB indexes for efficient topic querying

**Web Scraping Optimization:**
- Implement request caching to avoid redundant web requests
- Use connection pooling for HTTP requests
- Implement rate limiting to respect website policies
- Consider using async requests for parallel source consultation (within retry limits)

### Security Considerations

**API Key Management:**
- Store all API keys in environment variables
- Never commit keys to version control
- Use .env files for local development
- Use secrets management service in production
- Validate API keys on startup

**Data Validation:**
- Validate all external inputs using Pydantic models
- Sanitize content before storage
- Implement input size limits to prevent DoS
- Use parameterized SQL queries to prevent injection

**Error Information:**
- Don't expose sensitive information in error messages
- Log full details internally to PROBLEMS.md
- Return sanitized errors to users
- Implement proper error codes

**Web Scraping:**
- Respect robots.txt files
- Implement rate limiting
- Use appropriate User-Agent headers
- Handle CAPTCHA and anti-scraping measures gracefully

### Scalability Path

**Current Design (MVP):**
- Single-threaded sequential processing
- In-memory context management
- Direct Neon database calls via Kiro Power
- Suitable for 10-50 topics per run

**Future Enhancements:**
- Worker pool for parallel topic processing (respecting retry limits)
- Redis for distributed context management
- Message queue (Celery) for async processing
- Caching layer for web scraping results
- Caching layer for Context7 MCP responses
- Suitable for 100+ topics per run

## Deployment Considerations

### Environment Setup

**Required Environment Variables:**
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

# Topic Distribution (optional, defaults provided)
POKEMON_TOPICS=5
HOCKEY_TOPICS=3
SOCCER_TOPICS=2
```

**Python Version:**
- Python 3.10 or higher required
- Use virtual environment for dependency isolation

**Dependencies:**
```
crewai>=0.1.0
crewai-tools>=0.1.0
streamlit>=1.28.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
pylint>=3.0.0
hypothesis>=6.0.0
pytest>=7.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

### Running the System

**Development Mode:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run Pylint check
pylint src/ --min-score=8.0

# Run tests
pytest tests/

# Start Streamlit app
streamlit run app.py
```

**Production Mode:**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Monitoring and Observability

**Logging:**
- Structured JSON logging for production
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Separate log files for different components
- Rotate logs daily to prevent disk fill
- Log to DOCUMENTATION.md for significant events
- Log to PROBLEMS.md for errors and issues

**Metrics to Track:**
- Topics processed per hour
- Average processing time per topic per category
- Agent success/failure rates
- API call counts and latencies
- Database query performance
- Web scraping success rates
- Retry attempt counts
- Error rates by category
- Pylint scores over time

**Health Checks:**
- Neon database connectivity check on startup
- Kiro Power availability verification
- Context7 MCP connectivity check
- Periodic health check endpoint
- Monitor memory and CPU usage
- Alert on high error rates
- Database connection pool status
- Verify DOCUMENTATION.md and PROBLEMS.md are writable

## Documentation Structure

The system will maintain four key documentation files in the `docs/` directory:

**1. AGENT_STRUCTURE.md**
- Mermaid diagram of agent architecture
- Visual representation of data flow
- Component relationships
- Category-specific source mappings
- Updated automatically on system changes

**2. DOCUMENTATION.md**
- Timestamped log of significant events
- Architectural decisions and rationale
- System evolution history
- Integration patterns
- Performance optimization notes
- Configuration changes

**3. PROBLEMS.md**
- Active issues and bugs with status (active, resolved, blocked)
- Error logs with timestamps
- Known limitations
- Workarounds and temporary fixes
- Issue priority and resolution notes

**4. HOWTO.md**
- Setup instructions
- Dependency installation guide
- Configuration guide (environment variables)
- Running the application
- Troubleshooting common issues
- Development workflow
- Pylint and testing instructions
- Category source configuration

These documents will be generated and maintained automatically by the DocumentationManager component.

## Database Schema

### Topics Table
```sql
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(20) NOT NULL CHECK (category IN ('pokemon', 'hockey', 'soccer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'))
);

CREATE INDEX idx_topics_title ON topics(title);
CREATE INDEX idx_topics_category ON topics(category);
CREATE INDEX idx_topics_status ON topics(status);
```

### Content Table
```sql
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES topics(id),
    topic_title VARCHAR(200) NOT NULL,
    category VARCHAR(20) NOT NULL,
    draft TEXT,
    final_content TEXT NOT NULL,
    research_sources JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed'
);

CREATE INDEX idx_content_topic_id ON content(topic_id);
CREATE INDEX idx_content_category ON content(category);
```

### Context Table
```sql
CREATE TABLE context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES topics(id),
    agent_name VARCHAR(50) NOT NULL,
    output JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_context_topic_id ON context(topic_id);
CREATE INDEX idx_context_agent_name ON context(agent_name);
```

# Requirements Document

## Introduction

The Trading Card Content Generator is a multi-agent AI system designed to automate the creation of investment-focused articles about trading cards across three categories: Pokémon cards, Hockey cards, and Soccer cards. The system leverages CrewAI for agent coordination, Streamlit for user interface, Neon PostgreSQL database (accessed via Kiro Power) as the single source of truth, and Context7 MCP for accessing up-to-date library documentation. The system generates unique, deduplicated topics in a strategy phase by consulting category-specific web sources, then executes content creation for each topic sequentially through specialized AI agents (Strategist, Researcher, Writer, Editor, and Archivist).

## Glossary

- **Trading Card Content Generator**: The complete multi-agent system for automated trading card article creation
- **Strategy Phase**: Phase 1 of orchestration where unique topics are generated, validated against Neon database, and deduplicated
- **Execution Phase**: Phase 2 of orchestration where articles are created sequentially for each topic
- **ContentCrew**: A CrewAI crew instance containing specialized agents for content generation for a single topic
- **Context Manager**: Local component managing conversation context and agent memory
- **Neon Database**: PostgreSQL database accessed via Kiro Power storing all topics and generated content
- **Kiro Power**: Integration layer providing access to Neon database
- **Context7 MCP**: Model Context Protocol integration for accessing library documentation
- **Strategist Agent**: AI agent responsible for topic generation, web research, and deduplication checking
- **Researcher Agent**: AI agent responsible for gathering detailed information from category-specific sources
- **Writer Agent**: AI agent responsible for drafting investment-focused articles
- **Editor Agent**: AI agent responsible for refining and optimizing content
- **Archivist Agent**: AI agent responsible for storing completed articles in Neon database
- **Orchestrator**: Main control loop managing the two-phase workflow with sequential topic processing
- **Deduplication**: Process of ensuring topics are unique by checking against Neon database before generation
- **Category**: One of three content categories: Pokémon Cards, Hockey Cards, or Soccer Cards
- **Topic Distribution**: Default configuration of 5 Pokémon + 3 Hockey + 2 Soccer = 10 total articles
- **Loop Limit**: Maximum of 3 retry iterations for error recovery
- **Pylint**: Python code quality and style checker
- **Pydantic**: Data validation library using Python type annotations

## Requirements

### Requirement 1

**User Story:** As a content manager, I want the system to generate SEO-optimized unique topic lists for Pokémon, Hockey, and Soccer cards by using Serper.dev for SERP data and Google Trends, consulting category-specific web sources with ScrapeWebsiteTool, and checking against existing topics in Neon database, so that I can ensure no duplicate content is created and topics are search-engine friendly.

#### Acceptance Criteria

1. WHEN the Strategy Phase executes, THE Trading Card Content Generator SHALL query Neon database via Kiro Power to retrieve all existing topics before generating new ones
2. WHEN generating topics, THE Trading Card Content Generator SHALL use Serper.dev (SerperDevTool) to obtain SERP data, Google Trends, and keyword research for each category
3. WHEN generating topics for Pokémon cards, THE Trading Card Content Generator SHALL use ScrapeWebsiteTool to scrape sources including eBay, Cardmarket, TCGplayer, Pokebeach.com, Pokeguardian.com, Pokemon.com/us/pokemon-news, IGN.com Pokémon TCG, Pkmcards.fr, Limitlesstcg.com
4. WHEN generating topics for Hockey cards, THE Trading Card Content Generator SHALL use ScrapeWebsiteTool to scrape sources including eBay, COMC, Beckett.com, Puckjunk.com, All Vintage Cards Hockey Blog, Uncut Hockey, Bsportscards.com, Cherrycollectables.com
5. WHEN generating topics for Soccer cards, THE Trading Card Content Generator SHALL use ScrapeWebsiteTool to scrape sources including eBay, COMC, Beckett.com Soccer News, Soccercardshq.com, 130point.com, Usfcards.fr, Sportcard.fr
6. WHEN a proposed topic matches an existing topic in Neon database, THE Trading Card Content Generator SHALL exclude it from the final topic list
7. WHEN the Strategy Phase completes, THE Trading Card Content Generator SHALL return topics as a Python list of strings in JSON-serializable format
8. WHEN the default configuration is used, THE Trading Card Content Generator SHALL generate 5 Pokémon topics, 3 Hockey topics, and 2 Soccer topics for a total of 10 articles
9. WHEN topics are generated, THE Trading Card Content Generator SHALL include SEO score and relevant keywords for each topic candidate

### Requirement 2

**User Story:** As a content manager, I want the system to create articles for each topic sequentially (one at a time), so that I can manage resource usage, monitor progress, and ensure each article is completed before starting the next.

#### Acceptance Criteria

1. WHEN the Execution Phase begins, THE Trading Card Content Generator SHALL process topics one at a time in sequential order
2. WHEN processing each topic, THE Trading Card Content Generator SHALL instantiate a new ContentCrew with all five required agents
3. WHEN a ContentCrew completes processing a topic, THE Trading Card Content Generator SHALL proceed to the next topic in the list
4. WHEN all topics are processed, THE Trading Card Content Generator SHALL signal completion of the Execution Phase
5. IF a ContentCrew fails during processing, THEN THE Trading Card Content Generator SHALL log the error, retry up to 3 times, and if still failing continue with the next topic
6. WHEN retry attempts exceed 3 iterations for a single topic, THE Trading Card Content Generator SHALL mark the topic as failed and move to the next topic

### Requirement 3

**User Story:** As a content creator, I want specialized AI agents with appropriate tools (SerperDevTool, ScrapeWebsiteTool) to handle different aspects of article creation with Context7 MCP integration for library documentation, so that the output is comprehensive, high-quality, SEO-optimized, and uses current best practices.

#### Acceptance Criteria

1. WHEN a ContentCrew is instantiated, THE Trading Card Content Generator SHALL initialize five distinct agents: Strategist, Researcher, Writer, Editor, and Archivist
2. WHEN any agent needs library documentation, THE Trading Card Content Generator SHALL use Context7 MCP to retrieve up-to-date information
3. WHEN the Strategist Agent executes, THE Trading Card Content Generator SHALL use SerperDevTool for SEO insights and ScrapeWebsiteTool for web research
4. WHEN the Researcher Agent executes, THE Trading Card Content Generator SHALL use SerperDevTool and ScrapeWebsiteTool to gather information from category-specific web sources and use Context7 MCP for technical documentation
5. WHEN the Writer Agent executes, THE Trading Card Content Generator SHALL generate investment-focused draft articles based on research findings and SEO keywords
6. WHEN the Editor Agent executes, THE Trading Card Content Generator SHALL refine and optimize the drafted content for clarity, investment insights, and SEO optimization
7. WHEN the Archivist Agent executes, THE Trading Card Content Generator SHALL store the completed article in Neon database via Kiro Power

### Requirement 4

**User Story:** As a system administrator, I want Neon database to serve as the single source of truth for all content data, so that data consistency is maintained across the system.

#### Acceptance Criteria

1. WHEN querying existing topics, THE TCG Content Generator SHALL retrieve data exclusively from Neon database via Kiro Power
2. WHEN storing completed content, THE TCG Content Generator SHALL write data exclusively to Neon database via Kiro Power
3. WHEN updating content status, THE TCG Content Generator SHALL modify records in Neon database via Kiro Power
4. WHEN the system starts, THE TCG Content Generator SHALL verify connectivity to Neon database before proceeding
5. IF Neon database connectivity fails, THEN THE TCG Content Generator SHALL halt execution and report the error

### Requirement 5

**User Story:** As a content manager, I want a visual interface to monitor and control the content generation process, so that I can interact with the system easily.

#### Acceptance Criteria

1. WHEN the application starts, THE TCG Content Generator SHALL display a Streamlit interface
2. WHEN the Strategy Phase executes, THE TCG Content Generator SHALL display progress updates in the Streamlit interface
3. WHEN the Execution Phase executes, THE TCG Content Generator SHALL display the current topic being processed
4. WHEN content is completed, THE TCG Content Generator SHALL display a summary of generated content in the interface
5. WHERE user input is required, THE TCG Content Generator SHALL provide interactive controls in the Streamlit interface

### Requirement 6

**User Story:** As a developer, I want the system architecture documented with visual diagrams, so that I can understand the agent structure and workflow.

#### Acceptance Criteria

1. WHEN the system is initialized, THE TCG Content Generator SHALL generate a Mermaid diagram in docs/AGENT_STRUCTURE.md
2. WHEN the diagram is generated, THE TCG Content Generator SHALL represent all five agents and their relationships
3. WHEN the diagram is generated, THE TCG Content Generator SHALL illustrate the two-phase orchestration flow
4. WHEN the diagram is generated, THE TCG Content Generator SHALL show the integration points with Neon database via Kiro Power
5. WHEN the diagram is updated, THE TCG Content Generator SHALL reflect the current system architecture accurately

### Requirement 7

**User Story:** As a developer, I want a local Context Manager to handle agent memory and conversation context, so that agents can maintain coherent interactions throughout the workflow.

#### Acceptance Criteria

1. WHEN a ContentCrew is instantiated, THE TCG Content Generator SHALL initialize the Context Manager for that crew
2. WHEN an agent executes a task, THE TCG Content Generator SHALL store the task output in the Context Manager
3. WHEN a subsequent agent executes, THE TCG Content Generator SHALL provide access to previous agent outputs via the Context Manager
4. WHEN a ContentCrew completes, THE TCG Content Generator SHALL persist the final context to Neon database
5. WHILE a ContentCrew is active, THE TCG Content Generator SHALL maintain context isolation between different topic processing sessions

### Requirement 8

**User Story:** As a developer, I want the implementation broken down into numbered specification files, so that I can implement the system incrementally and systematically.

#### Acceptance Criteria

1. WHEN the requirements are finalized, THE TCG Content Generator SHALL organize implementation tasks into numbered spec files
2. WHEN spec files are created, THE TCG Content Generator SHALL store them in the .specs directory
3. WHEN each spec file is created, THE TCG Content Generator SHALL contain clear implementation instructions for a specific component
4. WHEN spec files are numbered, THE TCG Content Generator SHALL order them to support incremental development
5. WHEN all spec files are implemented, THE TCG Content Generator SHALL result in a complete, functional system

### Requirement 9

**User Story:** As a system administrator, I want comprehensive logging and error tracking, so that I can diagnose issues and monitor system health.

#### Acceptance Criteria

1. WHEN any component executes, THE TCG Content Generator SHALL log execution details with timestamps
2. WHEN errors occur, THE TCG Content Generator SHALL log error messages with stack traces
3. WHEN the system runs, THE TCG Content Generator SHALL maintain a PROBLEMS.md file tracking active issues
4. WHEN significant events occur, THE TCG Content Generator SHALL update DOCUMENTATION.md with architectural decisions
5. WHILE the system operates, THE TCG Content Generator SHALL provide real-time log output to the console

### Requirement 10

**User Story:** As a developer, I want clear setup and execution instructions in HOWTO.md, so that I can quickly get the system running in any environment.

#### Acceptance Criteria

1. WHEN the system is delivered, THE Trading Card Content Generator SHALL include a docs/HOWTO.md file with complete setup instructions
2. WHEN HOWTO.md is created, THE Trading Card Content Generator SHALL document all required dependencies including CrewAI, Streamlit, psycopg2, Hypothesis, Pylint, and Pydantic
3. WHEN HOWTO.md is created, THE Trading Card Content Generator SHALL provide step-by-step installation commands for all dependencies
4. WHEN HOWTO.md is created, THE Trading Card Content Generator SHALL include configuration instructions for environment variables including Neon connection, API keys, and Kiro Power settings
5. WHEN HOWTO.md is created, THE Trading Card Content Generator SHALL document how to run the application with Streamlit

### Requirement 11

**User Story:** As a developer, I want all Python code to be validated with Pylint and Pydantic, so that code quality is maintained and data structures are type-safe.

#### Acceptance Criteria

1. WHEN Python code is written, THE Trading Card Content Generator SHALL use Pydantic models for all data structures including Topic, Content, AgentContext, and Config
2. WHEN Python code is written, THE Trading Card Content Generator SHALL include type hints for all function parameters and return values
3. WHEN code quality is checked, THE Trading Card Content Generator SHALL run Pylint with a minimum score of 8.0/10
4. WHEN data validation occurs, THE Trading Card Content Generator SHALL use Pydantic validators to ensure data integrity
5. WHEN configuration is loaded, THE Trading Card Content Generator SHALL validate all required fields using Pydantic

### Requirement 12

**User Story:** As a developer, I want the system to maintain DOCUMENTATION.md and PROBLEMS.md files, so that I can track system evolution and active issues.

#### Acceptance Criteria

1. WHEN the system initializes, THE Trading Card Content Generator SHALL create docs/DOCUMENTATION.md if it does not exist
2. WHEN significant events occur, THE Trading Card Content Generator SHALL append entries to DOCUMENTATION.md with timestamps and descriptions
3. WHEN the system initializes, THE Trading Card Content Generator SHALL create docs/PROBLEMS.md if it does not exist
4. WHEN errors or issues are encountered, THE Trading Card Content Generator SHALL log them to PROBLEMS.md with status (active, resolved, blocked)
5. WHEN issues are resolved, THE Trading Card Content Generator SHALL update their status in PROBLEMS.md

### Requirement 13

**User Story:** As a content manager, I want topics to be structured as JSON-serializable Python lists, so that they can be easily processed, stored, and transferred between system components.

#### Acceptance Criteria

1. WHEN topics are generated, THE Trading Card Content Generator SHALL structure them as Python list of strings
2. WHEN topics are serialized, THE Trading Card Content Generator SHALL use JSON format for storage and transmission
3. WHEN topics are stored in Neon database, THE Trading Card Content Generator SHALL use JSONB column type for efficient querying
4. WHEN topics are passed between agents, THE Trading Card Content Generator SHALL maintain JSON-serializable format
5. WHEN topics are retrieved from Neon database, THE Trading Card Content Generator SHALL deserialize them into Python list of strings

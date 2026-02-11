# Implementation Plan

- [x] 1. Set up project structure, dependencies, and code quality tools





  - Create directory structure: src/agents, src/tasks, src/tools, src/config, src/utils, docs, tests
  - Create requirements.txt with dependencies: crewai, crewai-tools, streamlit, psycopg2-binary, pydantic>=2.0, pylint>=3.0, hypothesis, pytest, python-dotenv, requests
  - Create .env.example with all required environment variables (Neon, OpenAI, Serper API key, Kiro Power, topic distribution)
  - Set up Pylint configuration file (.pylintrc) with minimum score 8.0/10
  - Create pytest configuration (pytest.ini)
  - Set up basic logging configuration
  - _Requirements: 10.1, 10.2, 10.3, 11.3_


- [x] 2. Implement Pydantic data models




  - Create src/models/topic.py with Topic Pydantic model (id, title, category validation, created_at, status)
  - Create src/models/content.py with Content Pydantic model (id, topic_id, category, draft, final_content, research_sources, metadata)
  - Create src/models/agent_output.py with AgentOutput Pydantic model
  - Create src/models/config.py with Config Pydantic model including validators for topic distribution
  - Add Pydantic validators for category (pokemon|hockey|soccer)
  - Add Pydantic validators for status fields
  - Add type hints to all model fields
  - _Requirements: 11.1, 11.2, 11.4, 11.5, 13.1_

- [x] 2.1 Write property test for Pydantic model validation


  - **Property 11: Pydantic model usage**
  - **Validates: Requirements 11.1, 11.4, 11.5**


- [x] 3. Implement configuration management with Pydantic validation




  - Create src/config/settings.py with Config dataclass using Pydantic
  - Implement environment variable loading using python-dotenv
  - Add Pydantic validation for required configuration values
  - Create src/config/personas.py for agent persona definitions
  - Create src/config/web_sources.py with category-specific source mappings (Pokémon, Hockey, Soccer)
  - Add default topic distribution: {'pokemon': 5, 'hockey': 3, 'soccer': 2}
  - Add max_retries configuration (default: 3)
  - _Requirements: 10.4, 11.5, 1.7_


- [x] 4. Create database schema and Neon client with Kiro Power




  - Write SQL migration script for topics table with UNIQUE constraint on title
  - Write SQL migration script for content table with JSONB columns
  - Write SQL migration script for context table
  - Add indexes on topic titles, categories, and status
  - Create src/tools/neon_db_client.py with NeonDBClient class
  - Implement connection management through Kiro Power
  - Implement verify_connection() method
  - Implement execute_query() method with parameterized queries
  - Implement query_all_topics() method returning List[str]
  - Implement create_topic() method accepting TopicRecord Pydantic model
  - Implement create_content() method accepting ContentRecord Pydantic model
  - Implement update_status() method
  - Add connection retry logic with exponential backoff (max 3 retries)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 13.3_

- [x] 4.1 Write property test for pre-generation database query


  - **Property 1: Pre-generation database query**
  - **Validates: Requirements 1.1**

- [x] 4.2 Write property test for topic deduplication


  - **Property 3: Topic deduplication completeness**
  - **Validates: Requirements 1.5**

- [x] 5. Implement Context7 MCP client





  - Create src/tools/context7_client.py with Context7Client class
  - Implement resolve_library() method for library ID resolution
  - Implement get_docs() method with mode parameter (code/info)
  - Add caching for frequently accessed documentation
  - Add error handling for Context7 MCP failures (continue without docs)
  - _Requirements: 3.2_

- [x] 5.1 Write property test for Context7 MCP integration



  - **Property 8: Context7 MCP integration**
  - **Validates: Requirements 3.2**



- [x] 6. Implement Context Manager with Pydantic models






  - Create src/utils/context_manager.py with ContextManager class
  - Use AgentOutput Pydantic model for all context entries
  - Implement add_context() method with Pydantic validation
  - Implement get_context() method with optional agent filtering
  - Implement get_full_history() method returning List[AgentOutput]
  - Implement clear() method
  - Implement to_dict() serialization method
  - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [x] 7. Implement Documentation Manager





  - Create src/utils/documentation_manager.py with DocumentationManager class
  - Use DocumentationEntry and ProblemEntry Pydantic models
  - Implement log_event() method to append to docs/DOCUMENTATION.md with timestamps
  - Implement log_problem() method to append to docs/PROBLEMS.md with status
  - Implement update_problem_status() method
  - Create docs/DOCUMENTATION.md if it doesn't exist on initialization
  - Create docs/PROBLEMS.md if it doesn't exist on initialization
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 7.1 Write property test for documentation file updates


  - **Property 14: Documentation file updates**
  - **Validates: Requirements 12.2**

- [x] 7.2 Write property test for problem logging


  - **Property 15: Problem logging**
  - **Validates: Requirements 12.4, 12.5**


- [x] 8. Implement SEO and web scraping tools




  - Create src/tools/seo_tools.py with SEOTools class
  - Initialize SerperDevTool from crewai_tools for SERP data and Google Trends
  - Initialize ScrapeWebsiteTool from crewai_tools for web scraping
  - Implement get_serp_data() method using SerperDevTool
  - Implement get_google_trends() method using SerperDevTool
  - Implement get_keywords() method using SerperDevTool
  - Implement scrape_pokemon_sources() using ScrapeWebsiteTool (eBay, Cardmarket, TCGplayer, Pokebeach, etc.)
  - Implement scrape_hockey_sources() using ScrapeWebsiteTool (eBay, COMC, Beckett, Puckjunk, etc.)
  - Implement scrape_soccer_sources() using ScrapeWebsiteTool (eBay, COMC, Beckett Soccer, Soccercardshq, etc.)
  - Add request caching to avoid redundant requests
  - Add rate limiting and retry logic (max 3 retries)
  - Add error handling for unreachable sources (use fallback sources)
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.9_

- [x] 8.1 Write property test for category-specific source consultation


  - **Property 2: Category-specific source consultation**
  - **Validates: Requirements 1.3, 1.4, 1.5**

- [x] 9. Implement Strategy Phase with SEO and pre-query deduplication





  - Create src/agents/strategist.py with StrategyPhase class
  - Implement _fetch_existing_topics() to query Neon database BEFORE generation
  - Integrate SerperDevTool for SERP data, Google Trends, and keyword research
  - Integrate ScrapeWebsiteTool for category-specific source research
  - Integrate Context7Client for library documentation
  - Implement _get_seo_insights() method using SerperDevTool
  - Implement topic generation logic using OpenAI API with SEO insights
  - Implement _deduplicate() method to filter existing topics
  - Implement category filtering logic
  - Implement generate_topics() orchestration method
  - Return topics as JSON-serializable Python list of strings with SEO scores
  - Add retry logic with max 3 attempts
  - Log all operations to DocumentationManager
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [x] 9.1 Write property test for JSON-serializable topic format


  - **Property 4: JSON-serializable topic format**
  - **Validates: Requirements 1.6**

- [x] 9.2 Write property test for topic serialization format

  - **Property 16: Topic serialization format**
  - **Validates: Requirements 13.1, 13.2, 13.4, 13.5**

- [x] 10. Implement individual agents with SEO tools and Context7 integration


- [x] 10.1 Implement Researcher Agent


  - Create src/agents/researcher.py with ResearcherAgent class
  - Use ResearchResult Pydantic model for output (include seo_keywords field)
  - Integrate SerperDevTool for SEO research
  - Integrate ScrapeWebsiteTool for category-specific sources
  - Integrate Context7Client for technical documentation
  - Implement research() method to gather investment-focused information with SEO keywords
  - Format research output with sources, key investment insights, and SEO keywords
  - Add retry logic (max 3 attempts)
  - _Requirements: 3.4_

- [x] 10.2 Implement Writer Agent


  - Create src/agents/writer.py with WriterAgent class
  - Use DraftArticle Pydantic model for output
  - Implement write() method to generate investment-focused draft articles
  - Integrate with Context Manager to access research
  - Integrate Context7Client for best practices
  - Use OpenAI API for content generation
  - Add retry logic (max 3 attempts)
  - _Requirements: 3.4_

- [x] 10.3 Implement Editor Agent


  - Create src/agents/editor.py with EditorAgent class
  - Use EditedArticle Pydantic model for output
  - Implement edit() method to refine content for clarity and investment insights
  - Integrate with Context Manager to access draft
  - Integrate Context7Client for style guidelines
  - Use OpenAI API for content refinement
  - Add retry logic (max 3 attempts)
  - _Requirements: 3.5_

- [x] 10.4 Implement Archivist Agent


  - Create src/agents/archivist.py with ArchivistAgent class
  - Use ArchivedContent Pydantic model for output
  - Implement archive() method to store articles in Neon database
  - Integrate with NeonDBClient
  - Store context along with content
  - Add retry logic (max 3 attempts)
  - _Requirements: 3.6, 7.4_

- [x] 10.5 Write property test for category-specific research


  - **Property 9: Category-specific research**
  - **Validates: Requirements 3.3**

- [x] 10.6 Write property test for agent pipeline execution


  - **Property 10: Agent pipeline execution**
  - **Validates: Requirements 3.4, 3.5, 3.6**
  - **PBT Status: passed** - Test verifies that all four agents (Researcher, Writer, Editor, Archivist) execute in sequence and produce valid output for any topic processed by ContentCrew


- [x] 11. Implement ContentCrew with retry logic




  - Create src/agents/content_crew.py with ContentCrew class
  - Use ContentCrewResult Pydantic model for output
  - Implement _setup_agents() to initialize all five agents
  - Implement _run_pipeline() to execute agents in sequence: Research → Write → Edit → Archive
  - Integrate Context Manager for agent communication
  - Add error handling for individual agent failures
  - Implement retry logic with max 3 attempts per topic
  - Mark topic as failed after 3 retries and log to PROBLEMS.md
  - Implement execute() orchestration method
  - Clear context after each topic completion
  - _Requirements: 2.2, 2.5, 2.6, 3.1, 7.1_

- [x] 11.1 Write property test for ContentCrew agent completeness


  - **Property 6: ContentCrew agent completeness**
  - **Validates: Requirements 2.2, 3.1**

- [x] 11.2 Write property test for retry limit enforcement


  - **Property 7: Retry limit enforcement**
  - **Validates: Requirements 2.5, 2.6**

- [x] 12. Implement Orchestrator with sequential processing





  - Create src/orchestrator.py with Orchestrator class
  - Implement _execute_strategy_phase() to generate topics with pre-query deduplication
  - Implement _execute_execution_phase() with SEQUENTIAL loop (one topic at a time)
  - Add progress tracking and logging to DocumentationManager
  - Implement checkpoint pattern for resumability
  - Add error recovery logic to continue on failures (max 3 retries per topic)
  - Implement run() main orchestration method
  - Accept topic_distribution parameter (default: {'pokemon': 5, 'hockey': 3, 'soccer': 2})
  - Log all significant events to DOCUMENTATION.md
  - Log all errors to PROBLEMS.md
  - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.6_

- [x] 12.1 Write property test for sequential topic processing


  - **Property 5: Sequential topic processing**
  - **Validates: Requirements 2.1, 2.3**


- [x] 13. Implement logging system




  - Create src/utils/logger.py with structured logging setup
  - Implement timestamp logging for all component executions
  - Implement error logging with stack traces
  - Add console output handler
  - Add file output handlers with rotation
  - Integrate with DocumentationManager for DOCUMENTATION.md and PROBLEMS.md
  - _Requirements: 9.1, 9.2, 9.5_

- [x] 14. Implement documentation generation






  - Create script to generate docs/AGENT_STRUCTURE.md with Mermaid diagram
  - Implement diagram generation showing all five agents
  - Include two-phase orchestration flow in diagram
  - Show Neon database integration via Kiro Power
  - Show Context7 MCP integration
  - Show category-specific web sources
  - Update diagram automatically on system changes
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 9.3, 9.4_

- [x] 15. Implement Streamlit UI with documentation viewer





  - Create app.py as Streamlit entry point
  - Implement render_strategy_phase_ui() for topic distribution configuration
  - Default to 5 Pokémon + 3 Hockey + 2 Soccer
  - Implement render_execution_progress() for real-time progress display (show current topic and category)
  - Implement render_results() for final article summaries
  - Implement render_documentation_viewer() to display DOCUMENTATION.md and PROBLEMS.md
  - Add interactive controls for user input
  - Integrate with Orchestrator
  - Add error display and handling
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_


- [x] 16. Create comprehensive HOWTO.md documentation




  - Document all required dependencies (CrewAI, Streamlit, Pydantic, Pylint, etc.)
  - Provide step-by-step installation commands
  - Document environment variable configuration (Neon, OpenAI, Serper, Kiro Power, topic distribution)
  - Include instructions for running the application with Streamlit
  - Add Pylint usage instructions (minimum score 8.0/10)
  - Add pytest usage instructions
  - Add troubleshooting section for common issues
  - Add development workflow guide
  - Document category-specific source configuration
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_


- [x] 17. Code quality verification



  - Run Pylint on all Python modules and verify minimum score 8.0/10
  - Verify all functions have type hints
  - Verify all data structures use Pydantic models
  - Fix any Pylint warnings or errors
  - _Requirements: 11.2, 11.3_

- [x] 17.1 Write property test for type hint completeness


  - **Property 12: Type hint completeness**
  - **Validates: Requirements 11.2**

- [x] 17.2 Write property test for Pylint code quality


  - **Property 13: Pylint code quality**
  - **Validates: Requirements 11.3**

- [x] 18. Checkpoint - Ensure all tests pass





  - Ensure all unit tests pass
  - Ensure all property tests pass
  - Ensure all code quality tests pass
  - Ask the user if questions arise


- [x] 19. Integration and end-to-end testing




  - Test complete workflow from UI to database
  - Verify Kiro Power integration works correctly
  - Verify Context7 MCP integration works correctly
  - Test error recovery scenarios with retry logic (max 3 attempts)
  - Verify checkpoint and resume functionality
  - Test with default distribution (5 Pokémon, 3 Hockey, 2 Soccer)
  - Test with custom distributions
  - Verify sequential processing (one topic at a time)
  - Verify DOCUMENTATION.md and PROBLEMS.md are updated correctly
  - Test category-specific source consultation
  - Verify topic deduplication against Neon database
  - Verify JSON serialization of topics
  - _Requirements: All_


- [x] 20. Final documentation and deployment preparation


  - Update all documentation with final architecture
  - Verify AGENT_STRUCTURE.md diagram is accurate
  - Verify DOCUMENTATION.md contains system history
  - Verify PROBLEMS.md is properly formatted
  - Verify HOWTO.md is complete and accurate
  - Create deployment guide
  - Document known limitations
  - Create example configuration files
  - Document category source mappings
  - _Requirements: 6.5, 9.3, 9.4, 10.1, 12.1, 12.2, 12.3_

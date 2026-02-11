# Trading Card Content Generator - HOWTO Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Code Quality Tools](#code-quality-tools)
7. [Testing](#testing)
8. [Development Workflow](#development-workflow)
9. [Category-Specific Sources](#category-specific-sources)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Trading Card Content Generator is a multi-agent AI system that automates the creation of investment-focused articles about trading cards across three categories: Pokémon, Hockey, and Soccer. The system uses CrewAI for agent coordination, Streamlit for the user interface, and Neon PostgreSQL (via Kiro Power) as the data store.

### Key Features
- Two-phase orchestration (Strategy → Execution)
- SEO-optimized topic generation with web research
- Sequential article creation through specialized AI agents
- Category-specific web source consultation
- Automatic deduplication against existing content
- Property-based testing for correctness validation

---

## Prerequisites

### System Requirements
- Python 3.9 or higher
- pip (Python package manager)
- Git
- Internet connection for API access

### Required Accounts & API Keys
1. **Neon Database Account** - PostgreSQL database hosting
   - Sign up at: https://neon.tech
   - Create a new project and obtain connection string

2. **OpenAI API Key** - For AI agent operations
   - Sign up at: https://platform.openai.com
   - Generate API key from dashboard

3. **Serper.dev API Key** - For SEO and web research
   - Sign up at: https://serper.dev
   - Obtain API key from dashboard

4. **Kiro Power** - For Neon database integration
   - Ensure Kiro Power for Neon is activated in your Kiro IDE
   - Power name: `neon`

---

## Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd tcg-content-generator
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### Required Dependencies
The `requirements.txt` includes:
- **crewai** - Multi-agent orchestration framework
- **crewai-tools** - Tools for web scraping and SEO research
- **streamlit** - Web UI framework
- **psycopg2-binary** - PostgreSQL database adapter
- **pydantic>=2.0** - Data validation using Python type annotations
- **pylint>=3.0** - Code quality and style checker
- **hypothesis** - Property-based testing framework
- **pytest** - Testing framework
- **python-dotenv** - Environment variable management
- **requests** - HTTP library for API calls
- **openai** - OpenAI API client

### Step 4: Verify Installation
```bash
# Check Python version
python --version

# Verify key packages
pip list | grep -E "crewai|streamlit|pydantic|pylint|hypothesis"
```

---

## Configuration

### Step 1: Create Environment File
Copy the example environment file:
```bash
cp .env.example .env
```

### Step 2: Configure Environment Variables
Edit `.env` file with your credentials:

```bash
# Neon Database Configuration
NEON_CONNECTION_STRING=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Serper.dev API Configuration
SERPER_API_KEY=your-serper-api-key-here

# Kiro Power Configuration
KIRO_POWER_NAME=neon

# Topic Distribution (Optional - defaults shown)
DEFAULT_POKEMON_COUNT=5
DEFAULT_HOCKEY_COUNT=3
DEFAULT_SOCCER_COUNT=2

# System Configuration (Optional)
MAX_RETRIES=3
LOGGING_LEVEL=INFO
PYLINT_MIN_SCORE=8.0
```

### Environment Variable Details

#### Required Variables

**NEON_CONNECTION_STRING**
- Format: `postgresql://user:password@host.neon.tech/dbname?sslmode=require`
- Obtain from: Neon dashboard → Project → Connection Details
- Example: `postgresql://alex:AbC123xyz@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require`

**OPENAI_API_KEY**
- Format: `sk-` followed by alphanumeric string
- Obtain from: OpenAI Platform → API Keys
- Keep this secret and never commit to version control

**SERPER_API_KEY**
- Format: Alphanumeric string
- Obtain from: Serper.dev dashboard
- Used for SERP data, Google Trends, and keyword research

**KIRO_POWER_NAME**
- Value: `neon`
- This references the Kiro Power integration for Neon database access
- Ensure the power is activated in your Kiro IDE

#### Optional Variables

**Topic Distribution**
- `DEFAULT_POKEMON_COUNT`: Number of Pokémon topics (default: 5)
- `DEFAULT_HOCKEY_COUNT`: Number of Hockey topics (default: 3)
- `DEFAULT_SOCCER_COUNT`: Number of Soccer topics (default: 2)

**System Settings**
- `MAX_RETRIES`: Maximum retry attempts for failed operations (default: 3)
- `LOGGING_LEVEL`: Log verbosity - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `PYLINT_MIN_SCORE`: Minimum Pylint score required (default: 8.0)

### Step 3: Initialize Database
Run database migrations to create required tables:
```bash
# Run migrations in order
python -c "from src.tools.neon_db_client import NeonDBClient; from src.config.settings import Config; client = NeonDBClient(Config()); client.run_migrations()"
```

Or manually execute SQL files:
```bash
# Execute each migration file against your Neon database
psql $NEON_CONNECTION_STRING -f migrations/001_create_topics_table.sql
psql $NEON_CONNECTION_STRING -f migrations/002_create_content_table.sql
psql $NEON_CONNECTION_STRING -f migrations/003_create_context_table.sql
```

### Step 4: Verify Configuration
```bash
# Test database connection
python -c "from src.tools.neon_db_client import NeonDBClient; from src.config.settings import Config; print('Connected!' if NeonDBClient(Config()).verify_connection() else 'Failed')"
```

---

## Running the Application

### Start the Streamlit UI
```bash
streamlit run app.py
```

The application will:
1. Open in your default web browser at `http://localhost:8501`
2. Display the Strategy Phase configuration UI
3. Allow you to customize topic distribution
4. Show real-time progress during execution
5. Display generated articles and summaries

### Using the UI

#### 1. Configure Topic Distribution
- Adjust sliders for Pokémon, Hockey, and Soccer topic counts
- Default: 5 Pokémon + 3 Hockey + 2 Soccer = 10 total articles
- Click "Generate Content" to start

#### 2. Monitor Progress
- Strategy Phase: Watch topic generation and deduplication
- Execution Phase: See current topic being processed
- Progress bar shows completion percentage
- Category indicator shows which type of content is being created

#### 3. View Results
- Article summaries displayed after completion
- Links to full articles in database
- Success/failure status for each topic
- Total execution time and statistics

#### 4. View Documentation
- Click "Documentation" tab to view DOCUMENTATION.md
- Click "Problems" tab to view PROBLEMS.md
- Real-time updates as system runs

### Command-Line Execution (Alternative)
```bash
# Run orchestrator directly
python -c "from src.orchestrator import Orchestrator; from src.config.settings import Config; from src.tools.neon_db_client import NeonDBClient; orch = Orchestrator(Config(), NeonDBClient(Config())); orch.run()"
```

---

## Code Quality Tools

### Pylint - Code Quality Checker

#### Minimum Score Requirement
All Python modules must achieve a Pylint score of **8.0/10 or higher**.

#### Run Pylint on All Modules
```bash
# Check all Python files
pylint src/ tests/ app.py

# Check specific module
pylint src/agents/researcher.py

# Generate detailed report
pylint src/ --output-format=text > pylint_report.txt
```

#### Run Pylint with Configuration
```bash
# Use project .pylintrc configuration
pylint --rcfile=.pylintrc src/
```

#### Common Pylint Checks
- **C0103**: Invalid name (naming conventions)
- **C0114**: Missing module docstring
- **C0115**: Missing class docstring
- **C0116**: Missing function docstring
- **W0612**: Unused variable
- **E1101**: Instance has no member
- **R0913**: Too many arguments
- **R0914**: Too many local variables

#### Fix Common Issues
```bash
# Auto-format code with Black (helps with many Pylint issues)
black src/ tests/ app.py

# Check for unused imports
pylint --disable=all --enable=W0611 src/
```

#### Pylint Score Interpretation
- **10.0**: Perfect score (rare)
- **8.0-9.9**: Excellent (required minimum)
- **6.0-7.9**: Good (needs improvement)
- **Below 6.0**: Poor (requires significant refactoring)

### Type Hints
All functions must include type hints:
```python
from typing import List, Dict, Any

def process_topics(topics: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process topics with proper type hints."""
    pass
```

---

## Testing

### Pytest - Unit and Integration Tests

#### Run All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

#### Run Specific Test Files
```bash
# Run single test file
pytest tests/test_config.py

# Run specific test function
pytest tests/test_config.py::test_config_validation

# Run tests matching pattern
pytest -k "test_database"
```

#### Run Tests by Category
```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only property tests
pytest tests/property/
```

### Property-Based Testing with Hypothesis

#### What is Property-Based Testing?
Property-based testing validates that properties (universal rules) hold across many randomly generated inputs, rather than testing specific examples.

#### Run Property Tests
```bash
# Run all property tests
pytest tests/property/

# Run specific property test
pytest tests/property/test_topic_generation_properties.py

# Run with more examples (default is 100)
pytest tests/property/ --hypothesis-seed=12345
```

#### Property Test Examples
The system includes property tests for:
- **Property 1**: Pre-generation database query
- **Property 2**: Category-specific source consultation
- **Property 3**: Topic deduplication completeness
- **Property 4**: JSON-serializable topic format
- **Property 5**: Sequential topic processing
- And more...

#### Debugging Failed Property Tests
```bash
# Run with hypothesis verbosity
pytest tests/property/ -v --hypothesis-verbosity=verbose

# Save failing examples
pytest tests/property/ --hypothesis-show-statistics
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Development Workflow

### 1. Setup Development Environment
```bash
# Clone and setup
git clone <repository-url>
cd tcg-content-generator
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Development Cycle
```bash
# Make code changes
# ...

# Format code
black src/ tests/

# Check code quality
pylint src/ tests/

# Run tests
pytest

# Run property tests
pytest tests/property/

# Check coverage
pytest --cov=src --cov-report=term-missing
```

### 4. Pre-Commit Checklist
- [ ] All tests pass (`pytest`)
- [ ] Pylint score ≥ 8.0 (`pylint src/`)
- [ ] Code formatted (`black src/ tests/`)
- [ ] Type hints added to new functions
- [ ] Docstrings added to new classes/functions
- [ ] Property tests pass (`pytest tests/property/`)
- [ ] DOCUMENTATION.md updated if architecture changed
- [ ] PROBLEMS.md updated if issues found

### 5. Commit and Push
```bash
git add .
git commit -m "feat: descriptive commit message"
git push origin feature/your-feature-name
```

### 6. Code Review Guidelines
- Ensure all acceptance criteria are met
- Verify Pydantic models are used for data structures
- Check error handling and retry logic
- Validate integration with Kiro Power
- Confirm Context7 MCP usage where applicable

---

## Category-Specific Sources

### Pokémon Cards Sources
The system consults these sources for Pokémon content:

**Marketplaces:**
- eBay - General marketplace
- Cardmarket - European TCG marketplace
- TCGplayer - North American TCG marketplace

**News & Information:**
- Pokebeach.com - Pokémon TCG news and spoilers
- Pokeguardian.com - Investment and market analysis
- Pokemon.com/us/pokemon-news - Official Pokémon news
- IGN.com Pokémon TCG - Gaming news coverage

**Community & Data:**
- Pkmcards.fr - French Pokémon card database
- Limitlesstcg.com - Tournament results and meta analysis

### Hockey Cards Sources
The system consults these sources for Hockey content:

**Marketplaces:**
- eBay - General marketplace
- COMC - Check Out My Cards marketplace
- Beckett.com - Grading and marketplace

**Investment & Analysis:**
- Puckjunk.com - Hockey card investment strategies
- All Vintage Cards Hockey Blog - Vintage card analysis
- Uncut Hockey - Industry news and insights

**Retailers:**
- Bsportscards.com - Sports card retailer
- Cherrycollectables.com - Collectibles retailer

### Soccer Cards Sources
The system consults these sources for Soccer content:

**Marketplaces:**
- eBay - General marketplace
- COMC - Check Out My Cards marketplace

**News & Information:**
- Beckett.com Soccer News - Soccer card news
- Soccercardshq.com - Soccer card headquarters
- 130point.com - Soccer card community

**International Sources:**
- Usfcards.fr - French soccer cards
- Sportcard.fr - French sports cards

### Configuring Sources
Sources are configured in `src/config/web_sources.py`:
```python
POKEMON_SOURCES = [
    "https://www.ebay.com/b/Pokemon-Cards/...",
    "https://www.cardmarket.com/en/Pokemon",
    # Add more sources
]

HOCKEY_SOURCES = [
    "https://www.ebay.com/b/Hockey-Cards/...",
    # Add more sources
]

SOCCER_SOURCES = [
    "https://www.ebay.com/b/Soccer-Cards/...",
    # Add more sources
]
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Failures

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
```bash
# Verify connection string format
echo $NEON_CONNECTION_STRING

# Test connection manually
psql $NEON_CONNECTION_STRING -c "SELECT 1"

# Check Kiro Power activation
# In Kiro IDE: View → Powers → Ensure "neon" power is active

# Verify SSL mode is included
# Connection string must end with: ?sslmode=require
```

#### 2. OpenAI API Errors

**Error:** `openai.error.AuthenticationError: Incorrect API key`

**Solutions:**
```bash
# Verify API key format (starts with sk-)
echo $OPENAI_API_KEY

# Check API key validity at: https://platform.openai.com/api-keys

# Ensure no extra spaces in .env file
# Wrong: OPENAI_API_KEY= sk-123...
# Right: OPENAI_API_KEY=sk-123...

# Check API quota and billing
# Visit: https://platform.openai.com/account/billing
```

#### 3. Serper.dev API Errors

**Error:** `SerperDevTool: API request failed`

**Solutions:**
```bash
# Verify API key
echo $SERPER_API_KEY

# Check API quota at: https://serper.dev/dashboard

# Test API manually
curl -X POST https://google.serper.dev/search \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"pokemon cards"}'
```

#### 4. Pylint Score Below 8.0

**Error:** `Your code has been rated at 7.5/10`

**Solutions:**
```bash
# Run Black formatter first
black src/ tests/

# Check specific issues
pylint src/ --reports=y

# Fix common issues:
# - Add docstrings to all functions/classes
# - Remove unused imports
# - Fix naming conventions (snake_case)
# - Reduce function complexity

# Disable specific checks if justified (use sparingly)
# pylint: disable=too-many-arguments
```

#### 5. Property Test Failures

**Error:** `Falsifying example: test_topic_deduplication(...)`

**Solutions:**
```bash
# Run with verbose output to see counterexample
pytest tests/property/ -v --hypothesis-verbosity=verbose

# Check if counterexample reveals a bug
# Review the failing input in test output

# If bug found, fix code and re-run
# If test is incorrect, update test logic

# Reproduce specific failure
pytest tests/property/ --hypothesis-seed=<seed-from-output>
```

#### 6. Streamlit Won't Start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solutions:**
```bash
# Verify virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt

# Try running directly
python -m streamlit run app.py

# Check port availability (default 8501)
# If port in use, specify different port:
streamlit run app.py --server.port 8502
```

#### 7. Web Scraping Failures

**Error:** `ScrapeWebsiteTool: Failed to scrape source`

**Solutions:**
```bash
# Check internet connectivity
ping google.com

# Verify source URLs are accessible
curl -I https://www.pokebeach.com

# Check rate limiting
# System implements exponential backoff
# Wait a few minutes and retry

# Review logs for specific error
tail -f logs/tcg_generator.log

# Use fallback sources (automatic)
# System will try alternative sources if primary fails
```

#### 8. Context7 MCP Not Working

**Error:** `Context7Client: Failed to resolve library`

**Solutions:**
```bash
# Verify Context7 MCP is configured in Kiro
# Check .kiro/settings/mcp.json

# Test MCP connection
# In Kiro: View → MCP Servers → Check status

# System continues without Context7 if unavailable
# Check logs for warnings:
grep "Context7" logs/tcg_generator.log
```

#### 9. Memory Issues

**Error:** `MemoryError` or system slowdown

**Solutions:**
```bash
# Reduce topic distribution
# Edit .env:
DEFAULT_POKEMON_COUNT=2
DEFAULT_HOCKEY_COUNT=1
DEFAULT_SOCCER_COUNT=1

# Clear context between topics (automatic)
# System clears context after each ContentCrew

# Monitor memory usage
# On Linux/Mac:
top -p $(pgrep -f streamlit)

# On Windows:
# Task Manager → Details → python.exe
```

#### 10. Migration Failures

**Error:** `relation "topics" already exists`

**Solutions:**
```bash
# Check if tables already exist
psql $NEON_CONNECTION_STRING -c "\dt"

# Drop and recreate (WARNING: deletes data)
psql $NEON_CONNECTION_STRING -c "DROP TABLE IF EXISTS topics CASCADE"
psql $NEON_CONNECTION_STRING -c "DROP TABLE IF EXISTS content CASCADE"
psql $NEON_CONNECTION_STRING -c "DROP TABLE IF EXISTS context CASCADE"

# Re-run migrations
psql $NEON_CONNECTION_STRING -f migrations/001_create_topics_table.sql
psql $NEON_CONNECTION_STRING -f migrations/002_create_content_table.sql
psql $NEON_CONNECTION_STRING -f migrations/003_create_context_table.sql
```

### Getting Help

#### Check Logs
```bash
# View application logs
tail -f logs/tcg_generator.log

# View Streamlit logs
# Displayed in terminal where streamlit is running

# Check PROBLEMS.md for known issues
cat docs/PROBLEMS.md
```

#### Debug Mode
```bash
# Run with debug logging
export LOGGING_LEVEL=DEBUG
streamlit run app.py

# Or edit .env:
LOGGING_LEVEL=DEBUG
```

#### Community Support
- Check DOCUMENTATION.md for system architecture
- Review PROBLEMS.md for known issues
- Consult design.md for component details
- Review requirements.md for acceptance criteria

---

## Additional Resources

### Documentation Files
- **README.md** - Project overview and quick start
- **DOCUMENTATION.md** - System events and architectural decisions
- **PROBLEMS.md** - Active issues and their status
- **AGENT_STRUCTURE.md** - Visual system architecture with Mermaid diagrams
- **requirements.md** - Complete system requirements
- **design.md** - Detailed design specifications
- **tasks.md** - Implementation task list

### External Documentation
- **CrewAI**: https://docs.crewai.com
- **Streamlit**: https://docs.streamlit.io
- **Pydantic**: https://docs.pydantic.dev
- **Hypothesis**: https://hypothesis.readthedocs.io
- **Neon**: https://neon.tech/docs
- **OpenAI**: https://platform.openai.com/docs
- **Serper.dev**: https://serper.dev/docs

### Best Practices
1. Always activate virtual environment before working
2. Keep .env file secure and never commit it
3. Run tests before committing code
4. Maintain Pylint score above 8.0
5. Use Pydantic models for all data structures
6. Add type hints to all functions
7. Write docstrings for public APIs
8. Log significant events to DOCUMENTATION.md
9. Log errors to PROBLEMS.md
10. Clear context between ContentCrew instances

---

## Quick Reference

### Essential Commands
```bash
# Setup
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Run application
streamlit run app.py

# Run tests
pytest

# Check code quality
pylint src/ && black src/

# Run property tests
pytest tests/property/

# View logs
tail -f logs/tcg_generator.log
```

### Environment Variables Quick Check
```bash
# Verify all required variables are set
python -c "from src.config.settings import Config; print('Config OK' if Config() else 'Config Failed')"
```

### Database Quick Check
```bash
# Test connection
python -c "from src.tools.neon_db_client import NeonDBClient; from src.config.settings import Config; print('DB OK' if NeonDBClient(Config()).verify_connection() else 'DB Failed')"
```

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Maintainer:** TCG Content Generator Team

# Technology Stack

## Core Technologies
- **Language**: Python (recommended for AI/ML workflows)
- **AI/ML Framework**: OpenAI API, LangChain, or similar LLM frameworks
- **Data Processing**: Pandas, NumPy for content analysis
- **Web Framework**: FastAPI or Flask for API endpoints
- **Database**: PostgreSQL or MongoDB for article storage
- **Queue System**: Redis or Celery for async processing

## Development Tools
- **Package Manager**: pip with requirements.txt or Poetry
- **Code Quality**: Black (formatting), flake8 (linting), mypy (type checking)
- **Testing**: pytest for unit and integration tests
- **Environment**: python-dotenv for configuration management

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests
pytest tests/

# Code formatting
black .

# Linting
flake8 .
```

### Production
```bash
# Start the agent service
python -m colectio_agent.main

# Process article queue
python -m colectio_agent.worker
```

## Configuration
- Use environment variables for API keys and sensitive data
- Store configuration in `.env` files (never commit to version control)
- Use structured logging for monitoring and debugging
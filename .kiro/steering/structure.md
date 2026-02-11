# Project Structure

## Recommended Directory Layout

```
colectio-article-agent/
├── colectio_agent/           # Main application package
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Data models and schemas
│   ├── services/            # Business logic services
│   │   ├── article_generator.py
│   │   ├── content_processor.py
│   │   └── colectio_client.py
│   ├── workers/             # Background task workers
│   ├── utils/               # Utility functions
│   └── api/                 # API endpoints (if applicable)
├── tests/                   # Test files
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                    # Documentation
├── scripts/                 # Deployment and utility scripts
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## Naming Conventions

### Files and Directories
- Use snake_case for Python files and directories
- Use descriptive names that indicate purpose
- Keep module names short but clear

### Code Structure
- One class per file when possible
- Group related functionality in services
- Separate data models from business logic
- Use type hints throughout the codebase

## Architecture Patterns

### Service Layer Pattern
- Business logic in `services/` directory
- Each service handles a specific domain
- Services are stateless and testable

### Configuration Management
- All configuration in `config.py`
- Environment-specific settings via environment variables
- No hardcoded values in business logic

### Error Handling
- Custom exceptions in `exceptions.py`
- Structured logging for debugging
- Graceful degradation for external service failures

## File Organization Rules

1. **Import Order**: Standard library, third-party, local imports
2. **Module Structure**: Constants, classes, functions, main execution
3. **Test Organization**: Mirror the main package structure in tests/
4. **Documentation**: Docstrings for all public functions and classes
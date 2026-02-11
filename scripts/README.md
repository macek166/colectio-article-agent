# Scripts Directory

This directory contains utility scripts for the Trading Card Content Generator system.

## Available Scripts

### generate_agent_structure.py

Generates comprehensive documentation for the system architecture in `docs/AGENT_STRUCTURE.md`.

**Purpose:**
- Creates detailed documentation showing all five agents
- Generates Mermaid diagrams for system architecture, workflow, and data flow
- Documents two-phase orchestration (Strategy and Execution phases)
- Shows Neon database integration via Kiro Power
- Documents Context7 MCP integration
- Lists category-specific web sources

**Usage:**

```bash
# Run the script directly
python scripts/generate_agent_structure.py

# Or use the DocumentationManager
python -c "from src.utils.documentation_manager import DocumentationManager; DocumentationManager().regenerate_agent_structure()"
```

**Output:**
- Creates/updates `docs/AGENT_STRUCTURE.md` with current timestamp
- Logs regeneration event to `docs/DOCUMENTATION.md`

**When to Run:**
- After making changes to agent structure
- After modifying integration points (Neon, Context7, SEO tools)
- After updating category-specific sources
- After changing the two-phase workflow
- Automatically via DocumentationManager when system changes occur

**Generated Sections:**
1. Overview and key features
2. System architecture diagram (Mermaid)
3. Two-phase workflow sequence diagram (Mermaid)
4. Data flow diagram (Mermaid)
5. Detailed workflow descriptions
6. Agent details and responsibilities
7. Integration details (Neon, Context7, SEO)
8. Category-specific web sources
9. Error handling and retry logic
10. Configuration and environment variables
11. Technology stack
12. Data models and database schema
13. Performance considerations
14. Monitoring and observability
15. Development workflow

**Automatic Updates:**

The documentation can be automatically regenerated when system changes occur by calling:

```python
from src.utils.documentation_manager import DocumentationManager

doc_manager = DocumentationManager()
success = doc_manager.regenerate_agent_structure()
```

This is useful for:
- CI/CD pipelines
- Pre-commit hooks
- Automated testing
- System initialization

**Testing:**

Run the test suite to verify the generation script works correctly:

```bash
pytest tests/test_agent_structure_generation.py -v
```

The tests verify:
- Script exists and runs successfully
- Output file is created
- All required sections are present
- Mermaid diagrams are included
- All five agents are documented
- Two-phase orchestration is shown
- Neon and Context7 integrations are documented
- Category-specific sources are listed
- DocumentationManager integration works
- Regeneration events are logged

## Adding New Scripts

When adding new scripts to this directory:

1. Create a descriptive filename using snake_case
2. Add a docstring at the top explaining the script's purpose
3. Include usage examples in the docstring
4. Update this README with script details
5. Add tests in `tests/` directory
6. Make the script executable if needed: `chmod +x script_name.py`
7. Add shebang line: `#!/usr/bin/env python3`

## Script Guidelines

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Include error handling and logging
- Make scripts idempotent (safe to run multiple times)
- Document all command-line arguments
- Provide helpful error messages
- Test scripts thoroughly before committing

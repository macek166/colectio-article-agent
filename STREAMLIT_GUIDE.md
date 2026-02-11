# Streamlit UI Guide

## Overview

The Trading Card Content Generator includes a comprehensive Streamlit web interface for managing the content generation workflow.

## Features

### 1. Strategy Phase Configuration
- Configure topic distribution across three categories:
  - ⚡ Pokémon Cards (default: 5 articles)
  - 🏒 Hockey Cards (default: 3 articles)
  - ⚽ Soccer Cards (default: 2 articles)
- Adjust counts using number inputs
- View total article count before execution

### 2. Execution Progress Monitoring
- Real-time progress bar showing completion percentage
- Metrics display:
  - Completed topics
  - Remaining topics
  - Overall progress percentage
- Current topic information with category indicator

### 3. Results Dashboard
- Summary metrics:
  - Total topics processed
  - Successful articles
  - Failed articles
  - Total execution time
- Success rate visualization
- Detailed article information organized by category tabs
- Article previews with metadata:
  - Word count
  - Research sources count
  - Investment insights count
  - SEO keywords count

### 4. Documentation Viewer
- **Documentation Tab**: View DOCUMENTATION.md with system events
- **Problems Tab**: View PROBLEMS.md with issue tracking
  - Active problems count
  - Resolved problems count
  - Blocked problems count
- **Architecture Tab**: View AGENT_STRUCTURE.md with system diagrams

## Running the Application

### Prerequisites

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file with required configuration:

```bash
# Database
NEON_CONNECTION_STRING=postgresql://user:password@host/database
KIRO_POWER_NAME=neon

# AI APIs
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_dev_api_key

# Configuration (optional, defaults provided)
MAX_RETRIES=3
LOGGING_LEVEL=INFO
PYLINT_MIN_SCORE=8.0

# Topic Distribution (optional, defaults: 5/3/2)
TOPIC_DISTRIBUTION_POKEMON=5
TOPIC_DISTRIBUTION_HOCKEY=3
TOPIC_DISTRIBUTION_SOCCER=2
```

### Starting the Application

Run the Streamlit app:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Development Mode

For development with auto-reload:

```bash
streamlit run app.py --server.runOnSave true
```

### Production Mode

For production deployment:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Usage Workflow

### 1. Initialize System

1. Click the **"🔄 Initialize System"** button in the sidebar
2. Wait for system initialization to complete
3. Verify "✅ System Ready" status appears

### 2. Configure Topics

1. Adjust the number of articles for each category using the number inputs
2. Review the total article count
3. Ensure the total is between 1 and 50 articles

### 3. Start Generation

1. Click the **"🚀 Start Generation"** button
2. Monitor progress in real-time
3. Wait for completion message

### 4. Review Results

1. View summary metrics at the top
2. Navigate through category tabs (Pokémon, Hockey, Soccer)
3. Expand individual articles to see details
4. Review article previews and metadata

### 5. Check Documentation

1. Scroll to the **"📚 System Documentation"** section
2. Switch between tabs:
   - **Documentation**: System events and decisions
   - **Problems**: Active and resolved issues
   - **Architecture**: System structure diagrams

## Troubleshooting

### System Won't Initialize

**Problem**: "❌ Failed to connect to Neon database"

**Solution**:
- Verify `NEON_CONNECTION_STRING` in `.env` file
- Check network connectivity
- Ensure Kiro Power is properly configured

### Execution Fails

**Problem**: "❌ Execution failed: [error message]"

**Solution**:
- Check the **Problems** tab for detailed error information
- Verify all API keys are valid
- Check `docs/PROBLEMS.md` for troubleshooting steps

### No Results Displayed

**Problem**: Results section is empty after execution

**Solution**:
- Check if execution completed successfully
- Review the **Problems** tab for errors
- Verify topics were generated in Strategy Phase

## UI Components Reference

### Sidebar Controls

- **Initialize System**: Sets up all components and verifies connectivity
- **System Status**: Shows current system state
- **Quick Links**: Navigate to documentation sections

### Main Content Area

- **Strategy Phase Configuration**: Topic distribution inputs
- **Start Generation Button**: Initiates content generation
- **Execution Progress**: Real-time progress updates (when running)
- **Results Dashboard**: Detailed results after completion
- **Documentation Viewer**: System documentation access

### Status Indicators

- ✅ Success (green)
- ❌ Error (red)
- ⚠️ Warning (yellow)
- ℹ️ Information (blue)
- 🔄 In Progress (blue)

## Keyboard Shortcuts

Streamlit provides built-in keyboard shortcuts:

- `R`: Rerun the application
- `C`: Clear cache
- `?`: Show keyboard shortcuts help

## Performance Tips

1. **Limit Topic Count**: Start with smaller batches (5-10 topics) for testing
2. **Monitor Progress**: Use the progress indicators to track execution
3. **Check Documentation**: Review PROBLEMS.md if issues occur
4. **Clear Cache**: Use `C` keyboard shortcut if UI becomes unresponsive

## Advanced Features

### Custom Topic Distribution

Modify the default distribution in `.env`:

```bash
TOPIC_DISTRIBUTION_POKEMON=10
TOPIC_DISTRIBUTION_HOCKEY=5
TOPIC_DISTRIBUTION_SOCCER=5
```

### Logging Configuration

Adjust logging level for more detailed output:

```bash
LOGGING_LEVEL=DEBUG
```

### Retry Configuration

Modify retry attempts for failed operations:

```bash
MAX_RETRIES=5
```

## Support

For issues or questions:

1. Check `docs/PROBLEMS.md` for known issues
2. Review `docs/DOCUMENTATION.md` for system events
3. Check application logs in the console output
4. Verify environment configuration in `.env`

## Next Steps

After successful execution:

1. Review generated articles in the Results dashboard
2. Check the Neon database for stored content
3. Review documentation for system insights
4. Adjust topic distribution for future runs

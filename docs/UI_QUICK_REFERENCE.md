# Streamlit UI Quick Reference

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the application
streamlit run app.py
```

## UI Components at a Glance

### Sidebar
| Component | Purpose |
|-----------|---------|
| 🔄 Initialize System | Set up all components and verify connectivity |
| 📊 System Status | Shows if system is ready and running |
| 🔗 Quick Links | Navigate to documentation sections |

### Main Area
| Section | Purpose |
|---------|---------|
| 📋 Strategy Phase | Configure topic distribution (Pokémon/Hockey/Soccer) |
| 🚀 Start Button | Begin content generation |
| ⚙️ Progress | Real-time execution monitoring |
| 📊 Results | View generated articles and metrics |
| 📚 Documentation | Access system docs, problems, and architecture |

## Default Configuration

| Category | Default Count | Emoji |
|----------|--------------|-------|
| Pokémon | 5 | ⚡ |
| Hockey | 3 | 🏒 |
| Soccer | 2 | ⚽ |
| **Total** | **10** | 🎴 |

## Status Indicators

| Icon | Meaning |
|------|---------|
| ✅ | Success / Ready |
| ❌ | Error / Failed |
| ⚠️ | Warning |
| ℹ️ | Information |
| 🔄 | In Progress |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `R` | Rerun application |
| `C` | Clear cache |
| `?` | Show help |

## Common Tasks

### Generate 10 Articles (Default)
1. Click "Initialize System"
2. Keep default values (5/3/2)
3. Click "Start Generation"

### Custom Distribution
1. Click "Initialize System"
2. Adjust numbers for each category
3. Verify total ≤ 50
4. Click "Start Generation"

### View Results
1. Wait for execution to complete
2. Scroll to "Results Dashboard"
3. Click category tabs (⚡🏒⚽)
4. Expand articles to see details

### Check Problems
1. Scroll to "Documentation" section
2. Click "⚠️ Problems" tab
3. Review active/resolved/blocked counts
4. Read problem details

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Won't initialize | Check `.env` file and API keys |
| Database error | Verify `NEON_CONNECTION_STRING` |
| No results | Check "Problems" tab for errors |
| Slow execution | Reduce topic count for testing |

## Environment Variables

```bash
# Required
NEON_CONNECTION_STRING=postgresql://...
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...

# Optional (defaults shown)
MAX_RETRIES=3
LOGGING_LEVEL=INFO
TOPIC_DISTRIBUTION_POKEMON=5
TOPIC_DISTRIBUTION_HOCKEY=3
TOPIC_DISTRIBUTION_SOCCER=2
```

## Metrics Explained

### Strategy Phase
- **Topics Generated**: Number of unique topics created
- **Deduplication**: Topics filtered against database

### Execution Phase
- **Completed**: Successfully generated articles
- **Remaining**: Topics still to process
- **Progress**: Percentage complete

### Results
- **Total Topics**: All topics attempted
- **Successful**: Articles created and archived
- **Failed**: Topics that failed after retries
- **Time**: Total execution duration

## File Locations

| File | Purpose |
|------|---------|
| `docs/DOCUMENTATION.md` | System events log |
| `docs/PROBLEMS.md` | Issue tracking |
| `docs/AGENT_STRUCTURE.md` | Architecture diagrams |
| `logs/tcg_generator.log` | Application logs |

## Support

For detailed information, see:
- `STREAMLIT_GUIDE.md` - Complete user guide
- `docs/HOWTO.md` - Setup instructions
- `docs/PROBLEMS.md` - Known issues

---

**Quick Tip**: Start with a small batch (2-3 articles) to test the system before running larger batches.

"""Streamlit UI for TCG Content Generator.

This module provides the main user interface for the Trading Card Content Generator
system. It allows users to configure topic distribution, monitor execution progress,
view results, and access system documentation.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from src.config.settings import load_config
from src.orchestrator import Orchestrator, OrchestratorResult
from src.tools.context7_client import Context7Client
from src.tools.neon_db_client import NeonDBClient
from src.tools.seo_tools import SEOTools
from src.utils.documentation_manager import DocumentationManager
from src.utils.logger import setup_logging


# Configure logging
setup_logging(log_level="DEBUG")
logger = logging.getLogger(__name__)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'execution_result' not in st.session_state:
        st.session_state.execution_result = None
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    if 'current_category' not in st.session_state:
        st.session_state.current_category = ""
    if 'completed_count' not in st.session_state:
        st.session_state.completed_count = 0
    if 'total_count' not in st.session_state:
        st.session_state.total_count = 0


def initialize_orchestrator() -> Optional[Orchestrator]:
    """Initialize the Orchestrator with all required components.
    
    Returns:
        Orchestrator instance or None if initialization fails
    """
    try:
        # Load configuration
        config = load_config()
        
        # Override with UI selection if session state exists
        if 'llm_provider_select' in st.session_state:
            config.llm_provider = st.session_state.llm_provider_select
            
        # Initialize clients
        neon_client = NeonDBClient(config)
        context7_client = Context7Client(config)
        seo_tools = SEOTools(config)
        doc_manager = DocumentationManager()
        
        # Verify Neon database connectivity
        if not neon_client.verify_connection():
            st.error("❌ Failed to connect to Neon database. Please check your configuration.")
            return None
        
        # Create orchestrator
        orchestrator = Orchestrator(
            config=config,
            neon_client=neon_client,
            context7_client=context7_client,
            seo_tools=seo_tools,
            doc_manager=doc_manager
        )
        
        st.success("✅ System initialized successfully!")
        return orchestrator
        
    except Exception as e:  # pylint: disable=broad-except
        st.error(f"❌ Failed to initialize system: {str(e)}")
        logger.error("System initialization failed: %s", str(e))
        return None


def render_strategy_phase_ui() -> Dict[str, int]:
    """Render UI for topic distribution configuration.
    
    Returns:
        Dict with 'pokemon', 'hockey', 'soccer' counts
    """
    st.header("📋 Strategy Phase Configuration")
    st.write("Configure the number of articles to generate for each category.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("⚡ Pokémon Cards")
        pokemon_count = st.number_input(
            "Number of Pokémon articles",
            min_value=0,
            max_value=20,
            value=5,
            step=1,
            key="pokemon_count"
        )
    
    with col2:
        st.subheader("🏒 Hockey Cards")
        hockey_count = st.number_input(
            "Number of Hockey articles",
            min_value=0,
            max_value=20,
            value=3,
            step=1,
            key="hockey_count"
        )
    
    with col3:
        st.subheader("⚽ Soccer Cards")
        soccer_count = st.number_input(
            "Number of Soccer articles",
            min_value=0,
            max_value=20,
            value=2,
            step=1,
            key="soccer_count"
        )
    
    total = pokemon_count + hockey_count + soccer_count
    
    st.info(f"📊 Total articles to generate: **{total}**")
    
    if total == 0:
        st.warning("⚠️ Please select at least one article to generate.")
    elif total > 50:
        st.error("❌ Maximum 50 articles allowed per run.")
    
    return {
        'pokemon': int(pokemon_count),
        'hockey': int(hockey_count),
        'soccer': int(soccer_count)
    }


def render_execution_progress(
    current_topic: str,
    completed: int,
    total: int,
    category: str
) -> None:
    """Display execution phase progress.
    
    Args:
        current_topic: Current topic being processed
        completed: Number of completed topics
        total: Total number of topics
        category: Category of current topic
    """
    st.header("⚙️ Execution Phase Progress")
    
    # Progress bar
    progress = completed / total if total > 0 else 0
    st.progress(progress)
    
    # Status metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Completed", f"{completed}/{total}")
    
    with col2:
        st.metric("Remaining", total - completed)
    
    with col3:
        st.metric("Progress", f"{int(progress * 100)}%")
    
    # Current topic info
    if current_topic:
        category_emoji = {
            'pokemon': '⚡',
            'hockey': '🏒',
            'soccer': '⚽'
        }
        emoji = category_emoji.get(category, '📝')
        
        st.subheader(f"{emoji} Currently Processing")
        st.info(f"**Topic:** {current_topic}\n\n**Category:** {category.capitalize()}")


def render_results(result: OrchestratorResult) -> None:
    """Display final results and article summaries.
    
    Args:
        result: OrchestratorResult containing execution summary
    """
    st.header("📊 Execution Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Topics", result.total_topics)
    
    with col2:
        st.metric("✅ Successful", result.successful)
    
    with col3:
        st.metric("❌ Failed", result.failed)
    
    with col4:
        st.metric("⏱️ Time", f"{result.execution_time:.1f}s")
    
    # Success rate
    success_rate = (result.successful / result.total_topics * 100) if result.total_topics > 0 else 0
    st.progress(success_rate / 100)
    st.write(f"**Success Rate:** {success_rate:.1f}%")
    
    # Detailed results
    st.subheader("📝 Article Details")
    
    # Tabs for different categories
    tab1, tab2, tab3 = st.tabs(["⚡ Pokémon", "🏒 Hockey", "⚽ Soccer"])
    
    with tab1:
        render_category_results(result, 'pokemon')
    
    with tab2:
        render_category_results(result, 'hockey')
    
    with tab3:
        render_category_results(result, 'soccer')


def render_category_results(result: OrchestratorResult, category: str) -> None:
    """Render results for a specific category.
    
    Args:
        result: OrchestratorResult containing execution summary
        category: Category to display (pokemon, hockey, or soccer)
    """
    # Filter results by category
    category_results = [
        r for r in result.results
        if r.metadata.get('category', '').lower() == category
    ]
    
    if not category_results:
        st.info(f"No {category.capitalize()} articles generated.")
        return
    
    for idx, article_result in enumerate(category_results, start=1):
        # Format style for display (e.g. "The Investor")
        style = article_result.metadata.get('writing_style', 'Unknown').replace('_', ' ').title()
        topic = article_result.topic
        
        # Determine icon based on style (simple mapping)
        icon = "📝"
        if "investor" in style.lower(): icon = "📈"
        elif "skeptic" in style.lower(): icon = "🧐"
        elif "mentor" in style.lower(): icon = "🎓"
        elif "fanboy" in style.lower(): icon = "🤩"
        elif "trendsetter" in style.lower(): icon = "🔥"
        elif "historian" in style.lower(): icon = "📜"
        
        with st.expander(f"Article {idx}: {topic} | {icon} Style: {style}"):
            if article_result.success:
                st.success("✅ Successfully generated")
                
                # Display metadata
                metadata = article_result.metadata
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Word Count:** {metadata.get('draft_word_count', 'N/A')}")
                    st.write(f"**Sources:** {metadata.get('research_sources_count', 'N/A')}")
                
                with col2:
                    st.write(f"**Insights:** {metadata.get('investment_insights_count', 'N/A')}")
                    st.write(f"**Keywords:** {metadata.get('seo_keywords_count', 'N/A')}")
                    st.write(f"**Style:** {metadata.get('writing_style', 'N/A').replace('_', ' ').title()}")
                
                # Display article preview
                if article_result.article:
                    st.subheader("Article Preview")
                    preview = article_result.article[:500] + "..." if len(article_result.article) > 500 else article_result.article
                    st.text_area(
                        "Content",
                        value=preview,
                        height=200,
                        key=f"preview_{category}_{idx}",
                        disabled=True
                    )
            else:
                st.error(f"❌ Failed after {article_result.retry_count} attempts")
                error_msg = article_result.metadata.get('error', 'Unknown error')
                st.write(f"**Error:** {error_msg}")


def render_documentation_viewer() -> None:
    """Display DOCUMENTATION.md and PROBLEMS.md content."""
    st.header("📚 System Documentation")
    
    docs_dir = Path("docs")
    
    # 1. Architecture (Collapsible as requested)
    with st.expander("🏗️ System Architecture"):
         render_architecture_file(docs_dir / "AGENT_STRUCTURE.md")

    # 2. Problems (Only if active problems exist, or in a tab if we want to keep it accessible)
    # Check if there are active problems to decide how prominently to show it
    problems_path = docs_dir / "PROBLEMS.md"
    has_active_problems = False
    if problems_path.exists():
        with open(problems_path, 'r', encoding='utf-8') as f:
            if "**Status:** active" in f.read():
                has_active_problems = True
    
    if has_active_problems:
        st.error("⚠️ Active Problems Detected!")
        render_problems_file(problems_path)
    else:
        with st.expander("✅ System Status & Problems (All Clean)"):
            render_problems_file(problems_path)

    # 3. Logs/Documentation (Cleaned up)
    with st.expander("📖 Recent Activity Logs"):
        render_documentation_file(docs_dir / "DOCUMENTATION.md")


def render_documentation_file(file_path: Path) -> None:
    """Render DOCUMENTATION.md content with filtering.
    
    Args:
        file_path: Path to DOCUMENTATION.md file
    """
    if not file_path.exists():
        st.info("No activity logs yet.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            st.info("No activity logs yet.")
            return

        # Show only last 20 significant events to avoid "balast"
        # Filter out repetitive "Initialized" messages if there are too many
        filtered_lines = []
        for line in reversed(lines):
            filtered_lines.append(line)
            if len(filtered_lines) > 200: # Limit total characters/lines
                break
        
        content = "".join(reversed(filtered_lines))
        st.markdown(content)
    
    except Exception as e:  # pylint: disable=broad-except
        st.error(f"Failed to read documentation file: {str(e)}")


def render_problems_file(file_path: Path) -> None:
    """Render PROBLEMS.md content.
    
    Args:
        file_path: Path to PROBLEMS.md file
    """
    if not file_path.exists():
        st.info("No problems recorded.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.strip():
            # Count active problems
            active_count = content.count("**Status:** active")
            resolved_count = content.count("**Status:** resolved")
            blocked_count = content.count("**Status:** blocked")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 Active", active_count)
            with col2:
                st.metric("✅ Resolved", resolved_count)
            with col3:
                st.metric("🚫 Blocked", blocked_count)
            
            st.markdown("---")
            st.markdown(content)
        else:
            st.success("✅ No problems reported!")
    
    except Exception as e:  # pylint: disable=broad-except
        st.error(f"Failed to read problems file: {str(e)}")


def render_architecture_file(file_path: Path) -> None:
    """Render AGENT_STRUCTURE.md content.
    
    Args:
        file_path: Path to AGENT_STRUCTURE.md file
    """
    st.subheader("🏗️ System Architecture")
    
    if not file_path.exists():
        st.warning("Architecture documentation not found.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.strip():
            st.markdown(content)
        else:
            st.info("No architecture documentation available.")
    
    except Exception as e:  # pylint: disable=broad-except
        st.error(f"Failed to read architecture file: {str(e)}")


def main() -> None:
    """Main Streamlit application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="TCG Content Generator",
        page_icon="🎴",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Title and description
    st.title("🎴 Trading Card Content Generator")
    st.markdown("""
    Generate investment-focused articles about trading cards across three categories:
    **Pokémon**, **Hockey**, and **Soccer**.
    
    The system uses AI agents to research, write, edit, and archive high-quality content.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Controls")
        
        # Initialize button
        if st.button("🔄 Initialize System", use_container_width=True):
            with st.spinner("Initializing system..."):
                orchestrator = initialize_orchestrator()
                if orchestrator:
                    st.session_state.orchestrator = orchestrator
        
        st.markdown("---")
        
        # System status
        st.subheader("📊 System Status")
        if st.session_state.orchestrator:
            st.success("✅ System Ready")
        else:
            st.warning("⚠️ System Not Initialized")
        
        if st.session_state.is_running:
            st.info("🔄 Execution in Progress")
        
        # LLM Settings
        st.subheader("🤖 LLM Settings")
        
        # Get current provider from session state or config
        current_provider = st.session_state.get('llm_provider', 'openai')
        
        provider_options = ["openai", "gemini", "anthropic"]
        default_index = 0
        if current_provider in provider_options:
            default_index = provider_options.index(current_provider)

        llm_provider = st.selectbox(
            "LLM Provider",
            options=provider_options,
            index=default_index,
            key="llm_provider_select"
        )
        st.session_state.llm_provider = llm_provider
        
        if llm_provider == "openai":
            st.info("Using OpenAI (gpt-4o)")
        elif llm_provider == "anthropic":
            st.info("Using Anthropic (Claude Sonnet 4.5)")
        else:
            st.info("Using Google Gemini (gemini-2.0-flash)")

        st.markdown("---")
        
        # Quick links
        st.subheader("🔗 Quick Links")
        st.markdown("""
        - [View Documentation](#system-documentation)
        - [Check Problems](#system-documentation)
        - [System Architecture](#system-documentation)
        """)
    
    # Main content area
    if not st.session_state.orchestrator:
        st.info("👆 Click 'Initialize System' in the sidebar to get started.")
        
        # Show documentation viewer even when not initialized
        st.markdown("---")
        render_documentation_viewer()
        return
    
    # Strategy Phase Configuration
    topic_distribution = render_strategy_phase_ui()
    
    st.markdown("---")
    
    # Start execution button
    total_topics = sum(topic_distribution.values())
    
    if total_topics > 0 and total_topics <= 50:
        if st.button(
            f"🚀 Start Generation ({total_topics} articles)",
            use_container_width=True,
            disabled=st.session_state.is_running
        ):
            st.session_state.is_running = True
            st.session_state.completed_count = 0
            st.session_state.total_count = total_topics
            
            try:
                # Prepare UI elements for real-time updates
                progress_container = st.container()
                
                with progress_container:
                    st.header("⚙️ Execution Phase Progress")
                    progress_bar = st.progress(0)
                    status_area = st.empty()
                    metrics_area = st.empty()
                    
                    # specific initial message so user knows something is happening immediately
                    status_area.markdown("""
                    ### 🧠 Strategy Phase
                    > **Status:** Strategist Agent is generating topic candidates...
                    *Please wait, this initial brainstorming takes about 10-20 seconds.*
                    """)
                
                def update_ui_progress(topic: str, completed: int, total: int, category: str, status_message: Optional[str] = None):
                    """Callback to update UI during execution."""
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Update session state
                    st.session_state.current_topic = topic
                    st.session_state.completed_count = completed
                    st.session_state.total_count = total
                    st.session_state.current_category = category
                    
                    # Update Visuals
                    progress = completed / total if total > 0 else 0
                    progress_bar.progress(progress)
                    
                    category_emoji = {'pokemon': '⚡', 'hockey': '🏒', 'soccer': '⚽'}.get(category, '📝')
                    
                    # Dynamic status message
                    if not status_message:
                        status_message = "Agents are researching, writing, and refining content..."
                        
                    status_area.markdown(f"""
                    ### {category_emoji} Processing: {topic}
                    **Category:** {category.title()}
                    
                    > 🔄 **Status:** {status_message}
                    
                    *System is investigating global sources (EN, DE, ES, IT).*
                    *Timeout Protection Active: Max 20s per source.*
                    *Last Heartbeat: {timestamp}*
                    """)
                    
                    metrics_area.info(f"⏳ Progress: {completed}/{total} | Remaining: {total - completed}")

                # Execute orchestrator with callback
                result = st.session_state.orchestrator.run(
                    topic_distribution=topic_distribution,
                    progress_callback=update_ui_progress
                )
                st.session_state.execution_result = result
                
                requested_total = st.session_state.total_count
                if result.successful >= requested_total:
                    st.success(f"✅ Generation complete! Goal met: {result.successful}/{requested_total} articles created.")
                elif result.successful > 0:
                    st.warning(f"⚠️ Generation partial! {result.successful}/{requested_total} articles created. (Check failures below)")
                else:
                    st.error(f"❌ Generation failed! 0/{requested_total} articles created. (Check failures below)")
                
            except Exception as e:  # pylint: disable=broad-except
                st.error(f"❌ Execution failed: {str(e)}")
                logger.error("Execution failed: %s", str(e))
            
            finally:
                st.session_state.is_running = False
    
    # Show execution progress if running (Static view for state reload)
    elif st.session_state.is_running:
        render_execution_progress(
            current_topic=st.session_state.current_topic,
            completed=st.session_state.completed_count,
            total=st.session_state.total_count,
            category=st.session_state.current_category
        )
    
    # Show results if available
    if st.session_state.execution_result:
        st.markdown("---")
        render_results(st.session_state.execution_result)
    
    # Documentation viewer
    st.markdown("---")
    render_documentation_viewer()


if __name__ == "__main__":
    main()

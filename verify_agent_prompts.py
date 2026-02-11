import logging
import sys
import time
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import Config, load_config
from src.tools.neon_db_client import NeonDBClient
from src.tools.context7_client import Context7Client
from src.tools.seo_tools import SEOTools
from src.utils.documentation_manager import DocumentationManager
from src.utils.context_manager import ContextManager
from src.agents.content_crew import ContentCrew

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("🚀 Starting Agent Prompt Verification...")
    
    # 1. Initialize Configuration
    try:
        config = load_config()
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return

    # 2. Initialize Tools
    print("🛠️ Initializing tools...")
    try:
        neon_client = NeonDBClient(config)
        context7_client = Context7Client(config)
        seo_tools = SEOTools(config)
        doc_manager = DocumentationManager()
        context_manager = ContextManager()
        print("✅ Tools initialized")
    except Exception as e:
        print(f"❌ Failed to initialize tools: {e}")
        return

    # 3. Define Test Topic
    topic = "Investiční potenciál karty Charizard Base Set 1. edice"
    category = "pokemon"
    writing_style = "investor" # This triggers the "investor" style which we modified to be collector-focused

    print(f"\n🧪 Running ContentCrew for topic: '{topic}'")
    print(f"   Category: {category}")
    print(f"   Style: {writing_style}")
    print("   Please wait, this may take 2-3 minutes...")

    # 4. Initialize ContentCrew
    crew = ContentCrew(
        topic=topic,
        category=category,
        context_manager=context_manager,
        neon_client=neon_client,
        context7_client=context7_client,
        seo_tools=seo_tools,
        config=config,
        doc_manager=doc_manager,
        writing_style=writing_style
    )

    # 5. Execute Pipeline
    try:
        # Step 1: Research
        print("\n🔍 Step 1: Researching...")
        crew._setup_agents()
        research_result = crew.researcher.research(topic, category)
        print(f"   found {len(research_result.sources)} sources and {len(research_result.investment_insights)} insights")

        # Step 2: Write (Draft)
        print("\n✍️ Step 2: Writing Draft...")
        draft = crew.writer.write(topic, research_result, writing_style)
        print(f"   Draft word count: {draft.word_count}")
        print("\n--- DRAFT PREVIEW (First 500 chars) ---")
        print(draft.content[:500] + "...")
        print("---------------------------------------")

        # Step 3: Edit
        print("\n🎨 Step 3: Editing...")
        edited = crew.editor.edit(draft, topic)
        print(f"   Improvements made: {len(edited.improvements)}")
        for i, imp in enumerate(edited.improvements, 1):
            print(f"   - {imp}")

        print("\n--- FINAL ARTICLE PREVIEW ---")
        print(edited.content[:1000] + "...")
        print("--------------------------------")

        # Save full output to file for review
        with open("verification_result.txt", "w", encoding="utf-8") as f:
            f.write(f"TOPIC: {topic}\n\n")
            f.write("--- DRAFT ---\n")
            f.write(draft.content)
            f.write("\n\n--- EDITED ---\n")
            f.write(edited.content)
            f.write("\n\n--- IMPROVEMENTS ---\n")
            for imp in edited.improvements:
                f.write(f"- {imp}\n")
        
        print("\n✅ Verification Complete! Output saved to verification_result.txt")

    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

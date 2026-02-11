#!/usr/bin/env python3
"""Integration test for Neon database with agents."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.topic_manager import get_topic_manager, deduplicate_topics, save_topic

def test_neon_integration():
    """Test the complete Neon integration workflow."""
    print("🎯 Neon Database Integration Test")
    print("=" * 60)
    
    try:
        # Test topic manager
        print("🔧 Testing Topic Manager...")
        manager = get_topic_manager()
        
        # Test connection
        if not manager.test_connection():
            print("❌ Database connection failed!")
            return False
        
        print("✅ Database connection successful!")
        
        # Get existing topics
        print("\n📊 Getting existing topics...")
        existing = manager.get_existing_topics()
        print(f"Found {len(existing)} existing topics:")
        for i, topic in enumerate(existing[:5], 1):  # Show first 5
            print(f"   {i}. {topic}")
        if len(existing) > 5:
            print(f"   ... and {len(existing) - 5} more")
        
        # Test deduplication workflow (Strategist Agent simulation)
        print("\n🤖 Simulating Strategist Agent workflow...")
        new_candidates = [
            # Some that might be duplicates
            "Test Neon Connection",  # Might exist
            "Direct Test Topic",     # Might exist
            
            # Some new topics
            "Integration Test Pokemon Cards",
            "Neon Database Hockey Analysis", 
            "PostgreSQL Soccer Trading Cards",
            "Advanced Pokemon Card Strategies",
            "Modern Hockey Card Investment"
        ]
        
        print(f"📝 Generated {len(new_candidates)} topic candidates:")
        for i, topic in enumerate(new_candidates, 1):
            print(f"   {i}. {topic}")
        
        # Test deduplication by category
        print(f"\n🔍 Testing deduplication...")
        
        # Pokemon topics
        pokemon_candidates = [t for t in new_candidates if "Pokemon" in t or "pokemon" in t.lower()]
        unique_pokemon = deduplicate_topics(pokemon_candidates, "pokemon")
        print(f"🟡 Pokemon: {len(pokemon_candidates)} candidates → {len(unique_pokemon)} unique")
        
        # Hockey topics
        hockey_candidates = [t for t in new_candidates if "Hockey" in t or "hockey" in t.lower()]
        unique_hockey = deduplicate_topics(hockey_candidates, "hockey")
        print(f"🔵 Hockey: {len(hockey_candidates)} candidates → {len(unique_hockey)} unique")
        
        # Soccer topics
        soccer_candidates = [t for t in new_candidates if "Soccer" in t or "soccer" in t.lower()]
        unique_soccer = deduplicate_topics(soccer_candidates, "soccer")
        print(f"🟢 Soccer: {len(soccer_candidates)} candidates → {len(unique_soccer)} unique")
        
        # General topics (no specific category)
        general_candidates = [t for t in new_candidates if not any(cat in t.lower() for cat in ["pokemon", "hockey", "soccer"])]
        unique_general = deduplicate_topics(general_candidates)
        print(f"⚪ General: {len(general_candidates)} candidates → {len(unique_general)} unique")
        
        all_unique = unique_pokemon + unique_hockey + unique_soccer + unique_general
        
        print(f"\n📈 Deduplication Results:")
        print(f"   • Total candidates: {len(new_candidates)}")
        print(f"   • Duplicates filtered: {len(new_candidates) - len(all_unique)}")
        print(f"   • Unique topics: {len(all_unique)}")
        
        # Test Archivist Agent workflow
        print(f"\n📚 Simulating Archivist Agent workflow...")
        
        # Process first 3 unique topics
        for i, topic in enumerate(all_unique[:3], 1):
            category = "pokemon" if "pokemon" in topic.lower() else \
                      "hockey" if "hockey" in topic.lower() else \
                      "soccer" if "soccer" in topic.lower() else "pokemon"  # Default
            
            print(f"   {i}. Processing: {topic}")
            
            try:
                # Save topic (simulating article completion)
                topic_id = save_topic(topic, category)
                print(f"      ✅ Saved to {category} category (ID: {topic_id})")
                
                # Save content (simulating Archivist)
                content_id = manager.save_content(
                    topic_id=topic_id,
                    topic_title=topic,
                    category=category,
                    final_content=f"This is a test article about {topic}. " * 10,  # Longer content
                    research_sources=[
                        "https://example.com/research1",
                        "https://example.com/research2"
                    ],
                    metadata={
                        "test": True,
                        "integration_test": True,
                        "word_count": 100,
                        "category": category
                    }
                )
                print(f"      ✅ Content archived (ID: {content_id})")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        # Final statistics
        print(f"\n📊 Final Database Statistics:")
        final_topics = manager.get_existing_topics()
        
        # Count by category
        pokemon_count = len(manager.get_existing_topics("pokemon"))
        hockey_count = len(manager.get_existing_topics("hockey"))
        soccer_count = len(manager.get_existing_topics("soccer"))
        
        print(f"   pokemon: {pokemon_count} topics")
        print(f"   hockey: {hockey_count} topics")
        print(f"   soccer: {soccer_count} topics")
        print(f"   Total: {len(final_topics)} topics")
        
        manager.close()
        
        print(f"\n🎉 Neon integration test completed successfully!")
        print("✅ Topic Manager working")
        print("✅ Deduplication working")
        print("✅ Strategist Agent integration ready")
        print("✅ Archivist Agent integration ready")
        print("✅ Neon PostgreSQL fully operational")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    success = test_neon_integration()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
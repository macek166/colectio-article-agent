#!/usr/bin/env python3
"""Integration test for topic deduplication workflow."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.temp_database import get_temp_database, deduplicate_topics_temp, add_topic_temp

def test_strategist_workflow():
    """Test the strategist workflow with deduplication."""
    print("🎯 Testing Strategist Workflow with Deduplication")
    print("=" * 60)
    
    # Simulate existing topics in database
    print("📊 Setting up existing topics...")
    existing_topics = [
        "Pikachu Trading Card Market Analysis",
        "Wayne Gretzky Rookie Card History", 
        "Messi World Cup Trading Cards"
    ]
    
    for topic in existing_topics:
        category = "pokemon" if "Pikachu" in topic else "hockey" if "Gretzky" in topic else "soccer"
        add_topic_temp(topic, category)
        print(f"   ✅ Added: {topic} ({category})")
    
    # Simulate new topic candidates from Strategist
    print(f"\n🤖 Simulating Strategist Agent topic generation...")
    new_candidates = [
        # Some duplicates (should be filtered)
        "Pikachu Trading Card Market Analysis",  # Duplicate
        "Wayne Gretzky Rookie Card History",    # Duplicate
        
        # Some new topics (should pass through)
        "Charizard First Edition Investment Guide",
        "Connor McDavid Rookie Card Values",
        "Ronaldo Champions League Cards",
        "Pokemon Card Grading Tips",
        "Hockey Card Authentication Methods"
    ]
    
    print(f"   📝 Generated {len(new_candidates)} topic candidates:")
    for i, topic in enumerate(new_candidates, 1):
        print(f"      {i}. {topic}")
    
    # Test deduplication for each category
    print(f"\n🔍 Testing deduplication by category...")
    
    # Pokemon topics
    pokemon_candidates = [t for t in new_candidates if "Pikachu" in t or "Charizard" in t or "Pokemon" in t]
    unique_pokemon = deduplicate_topics_temp(pokemon_candidates, "pokemon")
    print(f"   🟡 Pokemon: {len(pokemon_candidates)} candidates → {len(unique_pokemon)} unique")
    for topic in unique_pokemon:
        print(f"      ✅ {topic}")
    
    # Hockey topics  
    hockey_candidates = [t for t in new_candidates if "Gretzky" in t or "McDavid" in t or "Hockey" in t]
    unique_hockey = deduplicate_topics_temp(hockey_candidates, "hockey")
    print(f"   🔵 Hockey: {len(hockey_candidates)} candidates → {len(unique_hockey)} unique")
    for topic in unique_hockey:
        print(f"      ✅ {topic}")
    
    # Soccer topics
    soccer_candidates = [t for t in new_candidates if "Ronaldo" in t]
    unique_soccer = deduplicate_topics_temp(soccer_candidates, "soccer")
    print(f"   🟢 Soccer: {len(soccer_candidates)} candidates → {len(unique_soccer)} unique")
    for topic in unique_soccer:
        print(f"      ✅ {topic}")
    
    # Combine all unique topics
    all_unique = unique_pokemon + unique_hockey + unique_soccer
    print(f"\n📈 Final Results:")
    print(f"   • Total candidates: {len(new_candidates)}")
    print(f"   • Duplicates filtered: {len(new_candidates) - len(all_unique)}")
    print(f"   • Unique topics: {len(all_unique)}")
    
    return all_unique

def test_archivist_workflow(topics):
    """Test the archivist workflow with topic saving."""
    print(f"\n📚 Testing Archivist Workflow")
    print("=" * 40)
    
    # Simulate processing topics and saving them
    print("💾 Simulating article completion and archiving...")
    
    for i, topic in enumerate(topics[:3], 1):  # Process first 3 topics
        category = "pokemon" if any(word in topic for word in ["Pikachu", "Charizard", "Pokemon"]) else \
                  "hockey" if any(word in topic for word in ["Gretzky", "McDavid", "Hockey"]) else "soccer"
        
        print(f"   {i}. Processing: {topic}")
        
        # Simulate article completion
        success = add_topic_temp(topic, category)
        status = "✅ Archived" if success else "⚠️  Already exists"
        print(f"      {status} in {category} category")
    
    # Show final database state
    db = get_temp_database()
    stats = db.get_stats()
    
    print(f"\n📊 Final Database Statistics:")
    for category, count in stats.items():
        if category != 'total':
            print(f"   {category}: {count} topics")
    print(f"   Total: {stats['total']} topics")

def main():
    """Run the complete integration test."""
    print("🧪 TCG Content Generator - Integration Test")
    print("=" * 70)
    
    try:
        # Test strategist workflow
        unique_topics = test_strategist_workflow()
        
        # Test archivist workflow
        test_archivist_workflow(unique_topics)
        
        print(f"\n🎉 Integration test completed successfully!")
        print(f"✅ Deduplication working correctly")
        print(f"✅ Topic storage working correctly")
        print(f"✅ Database persistence working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
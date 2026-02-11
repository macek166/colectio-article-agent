#!/usr/bin/env python3
"""Test script for temporary topic database."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.temp_database import TempTopicDatabase, deduplicate_topics_temp, add_topic_temp

def main():
    """Test the temporary database functionality."""
    print("🧪 Testing Temporary Topic Database")
    print("=" * 50)
    
    # Create database instance
    db = TempTopicDatabase("topics_storage.json")
    
    print("📊 Current topic statistics:")
    stats = db.get_stats()
    for category, count in stats.items():
        print(f"   {category}: {count} topics")
    
    print("\n🔍 Testing deduplication...")
    
    # Test topics with some duplicates
    test_topics = [
        "Pikachu Trading Card Market Analysis",
        "Charizard First Edition Values", 
        "Pokemon Card Investment Guide",
        "Wayne Gretzky Rookie Card History",
        "Connor McDavid Rookie Cards",
        "Messi World Cup Trading Cards"
    ]
    
    print(f"Original topics ({len(test_topics)}):")
    for i, topic in enumerate(test_topics, 1):
        print(f"   {i}. {topic}")
    
    # Test deduplication for Pokemon
    pokemon_topics = [t for t in test_topics if "Pokemon" in t or "Pikachu" in t or "Charizard" in t]
    unique_pokemon = deduplicate_topics_temp(pokemon_topics, "pokemon")
    
    print(f"\n✅ Unique Pokemon topics ({len(unique_pokemon)}):")
    for topic in unique_pokemon:
        print(f"   • {topic}")
    
    # Add the unique topics
    print(f"\n💾 Adding unique topics to database...")
    for topic in unique_pokemon:
        added = add_topic_temp(topic, "pokemon")
        status = "✅ Added" if added else "⚠️  Already exists"
        print(f"   {status}: {topic}")
    
    # Test hockey topics
    hockey_topics = [t for t in test_topics if "Gretzky" in t or "McDavid" in t]
    unique_hockey = deduplicate_topics_temp(hockey_topics, "hockey")
    
    print(f"\n🏒 Unique Hockey topics ({len(unique_hockey)}):")
    for topic in unique_hockey:
        print(f"   • {topic}")
        add_topic_temp(topic, "hockey")
    
    # Test soccer topics  
    soccer_topics = [t for t in test_topics if "Messi" in t]
    unique_soccer = deduplicate_topics_temp(soccer_topics, "soccer")
    
    print(f"\n⚽ Unique Soccer topics ({len(unique_soccer)}):")
    for topic in unique_soccer:
        print(f"   • {topic}")
        add_topic_temp(topic, "soccer")
    
    # Final statistics
    print(f"\n📈 Final topic statistics:")
    final_stats = db.get_stats()
    for category, count in final_stats.items():
        print(f"   {category}: {count} topics")
    
    print(f"\n🎉 Temporary database test completed!")
    print(f"📁 Topics stored in: topics_storage.json")
    
    # Test duplicate detection
    print(f"\n🔄 Testing duplicate detection...")
    duplicate_test = [
        "Pikachu Trading Card Market Analysis",  # Should be duplicate
        "New Pokemon Card Topic"                 # Should be unique
    ]
    
    filtered = deduplicate_topics_temp(duplicate_test, "pokemon")
    print(f"   Input: {duplicate_test}")
    print(f"   Filtered: {filtered}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
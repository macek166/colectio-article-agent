#!/usr/bin/env python3
"""Test updated Neon database client."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Force reload of the module
import importlib
if 'utils.database' in sys.modules:
    importlib.reload(sys.modules['utils.database'])

from utils.database import NeonDatabaseClient

async def test_updated_client():
    """Test the updated Neon database client."""
    
    print("🎯 Testing Updated Neon Database Client")
    print("=" * 50)
    
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if not conn_str:
        print("❌ NEON_CONNECTION_STRING not found!")
        return False
    
    try:
        # Create client
        print("🔧 Creating database client...")
        client = NeonDatabaseClient(conn_str)
        
        # Test connection
        print("🔍 Testing connection...")
        success = await client.test_connection()
        
        if not success:
            print("❌ Connection test failed!")
            return False
        
        print("✅ Connection successful!")
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Get existing topics
        topics = await client.get_existing_topics()
        print(f"📊 Found {len(topics)} existing topics")
        
        # Test saving a topic
        topic_id = await client.save_topic("Updated Client Test", "pokemon")
        print(f"✅ Test topic saved with ID: {topic_id}")
        
        # Update topic status
        await client.update_topic_status(topic_id, "in_progress")
        print("✅ Topic status updated")
        
        # Test content saving (this should work now)
        print("🧪 Testing content saving...")
        content_id = await client.save_content(
            topic_id=topic_id,
            topic_title="Updated Client Test",
            category="pokemon",
            final_content="This is a test article content for the updated Neon database client.",
            research_sources=["https://example.com", "https://test.com"],
            metadata={"test": True, "updated_client": True, "version": "2.0"}
        )
        print(f"✅ Test content saved with ID: {content_id}")
        
        # Update topic to completed
        await client.update_topic_status(topic_id, "completed")
        print("✅ Topic marked as completed")
        
        # Final topic count
        final_topics = await client.get_existing_topics()
        print(f"📊 Final topic count: {len(final_topics)}")
        
        await client.disconnect()
        
        print("\n🎉 Updated client test completed successfully!")
        print("✅ Connection working")
        print("✅ Topic operations working")
        print("✅ Content operations working")
        print("✅ JSONB handling fixed")
        print("✅ Ready for agent integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_updated_client())
    sys.exit(0 if success else 1)
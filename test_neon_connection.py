#!/usr/bin/env python3
"""Test Neon database connection and setup."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.database import NeonDatabaseClient

async def test_neon_connection():
    """Test Neon database connection and setup."""
    
    print("🎯 Testing Neon Database Connection")
    print("=" * 50)
    
    # Check connection string
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if not conn_str:
        print("❌ NEON_CONNECTION_STRING not found!")
        return False
    
    # Mask for display
    masked = conn_str[:30] + "..." + conn_str[-20:]
    print(f"📡 Connection: {masked}")
    
    try:
        # Create client
        print("\n🔧 Creating database client...")
        client = NeonDatabaseClient(conn_str)
        
        # Test connection
        print("🔍 Testing connection...")
        success = await client.test_connection()
        
        if not success:
            print("❌ Connection test failed!")
            return False
        
        print("✅ Connection successful!")
        
        # Run migrations
        print("\n🔧 Running database migrations...")
        await client.execute_migrations()
        print("✅ Migrations completed!")
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Get existing topics
        topics = await client.get_existing_topics()
        print(f"📊 Found {len(topics)} existing topics")
        
        # Test saving a topic
        topic_id = await client.save_topic("Test Neon Connection", "pokemon")
        print(f"✅ Test topic saved with ID: {topic_id}")
        
        # Update topic status
        await client.update_topic_status(topic_id, "completed")
        print("✅ Topic status updated")
        
        # Test content saving
        content_id = await client.save_content(
            topic_id=topic_id,
            topic_title="Test Neon Connection",
            category="pokemon",
            final_content="This is a test article content for Neon database connection.",
            research_sources=["https://example.com"],
            metadata={"test": True, "connection_test": "successful"}
        )
        print(f"✅ Test content saved with ID: {content_id}")
        
        # Final topic count
        final_topics = await client.get_existing_topics()
        print(f"📊 Final topic count: {len(final_topics)}")
        
        await client.disconnect()
        
        print("\n🎉 Neon database setup completed successfully!")
        print("✅ Connection working")
        print("✅ Migrations executed")
        print("✅ Basic operations tested")
        print("✅ Ready for production use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your connection string format")
        print("2. Verify Neon project is active")
        print("3. Check network connectivity")
        return False

async def main():
    """Main function."""
    success = await test_neon_connection()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
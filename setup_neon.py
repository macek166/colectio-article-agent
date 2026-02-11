#!/usr/bin/env python3
"""Setup script for Neon database - run this to initialize your database."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.database import NeonDatabaseClient

async def main():
    """Setup Neon database with proper error handling."""
    print("🚀 Neon Database Setup")
    print("=" * 50)
    
    # Check environment
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if not conn_str:
        print("❌ NEON_CONNECTION_STRING not found!")
        print("\n📝 Please add this to your .env file:")
        print("NEON_CONNECTION_STRING=postgresql://user:password@host.neon.tech/dbname?sslmode=require")
        return False
    
    # Mask connection string for display
    masked = conn_str[:25] + "..." + conn_str[-15:] if len(conn_str) > 40 else "***"
    print(f"📡 Connection: {masked}")
    
    try:
        # Create client and test connection
        client = NeonDatabaseClient(conn_str)
        print("\n🔍 Testing connection...")
        
        success = await client.test_connection()
        if not success:
            print("❌ Connection failed!")
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
        
        # Test saving a topic (won't duplicate if exists)
        test_topic_id = await client.save_topic("Test Topic - Setup", "pokemon")
        print(f"✅ Test topic saved with ID: {test_topic_id}")
        
        await client.disconnect()
        
        print("\n🎉 Neon database setup completed successfully!")
        print("\n📋 Summary:")
        print(f"   • Database connected: ✅")
        print(f"   • Schema created: ✅") 
        print(f"   • Existing topics: {len(topics)}")
        print(f"   • Test operations: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your NEON_CONNECTION_STRING format")
        print("2. Ensure your Neon project is active")
        print("3. Verify database permissions")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
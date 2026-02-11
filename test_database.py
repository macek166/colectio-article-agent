#!/usr/bin/env python3
"""Quick test script for Neon database connection."""

import asyncio
import os
from src.utils.database import test_database_connection, setup_database

async def main():
    """Test database connection and setup."""
    print("🔍 Testing Neon database connection...")
    
    # Check if connection string is configured
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if not conn_str:
        print("❌ NEON_CONNECTION_STRING not found in environment")
        print("Please check your .env file")
        return
    
    # Mask the connection string for security
    masked = conn_str[:20] + "..." + conn_str[-20:] if len(conn_str) > 40 else "***"
    print(f"📡 Using connection: {masked}")
    
    # Test connection
    success = await test_database_connection()
    if success:
        print("✅ Database connection successful!")
        
        print("\n🔧 Setting up database schema...")
        try:
            await setup_database()
            print("✅ Database schema setup completed!")
            print("\n🎉 Neon database is ready for use!")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
    else:
        print("❌ Database connection failed!")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your NEON_CONNECTION_STRING in .env")
        print("2. Ensure your Neon project is active")
        print("3. Verify network connectivity")

if __name__ == "__main__":
    asyncio.run(main())
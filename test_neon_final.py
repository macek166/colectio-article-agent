#!/usr/bin/env python3
"""Final test for Neon database connection."""

import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_neon_direct():
    """Test Neon connection directly with asyncpg."""
    
    print("🎯 Direct Neon Database Test")
    print("=" * 40)
    
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if not conn_str:
        print("❌ No connection string found")
        return False
    
    try:
        # Direct connection
        print("🔗 Connecting to Neon...")
        conn = await asyncpg.connect(conn_str)
        
        # Test basic query
        print("🔍 Testing basic query...")
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Basic query result: {result}")
        
        # Check if tables exist
        print("📊 Checking tables...")
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        table_names = [row['table_name'] for row in tables]
        print(f"📋 Found tables: {table_names}")
        
        # If no tables, create them
        if not table_names:
            print("🔧 Creating tables...")
            
            # Create topics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(200) NOT NULL UNIQUE,
                    category VARCHAR(20) NOT NULL CHECK (category IN ('pokemon', 'hockey', 'soccer')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'))
                );
            """)
            
            # Create content table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
                    topic_title VARCHAR(200) NOT NULL,
                    category VARCHAR(20) NOT NULL CHECK (category IN ('pokemon', 'hockey', 'soccer')),
                    draft TEXT,
                    final_content TEXT NOT NULL,
                    research_sources JSONB DEFAULT '[]'::jsonb,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('draft', 'completed', 'published', 'archived'))
                );
            """)
            
            print("✅ Tables created!")
        
        # Test topic insertion
        print("🧪 Testing topic insertion...")
        topic_result = await conn.fetchrow("""
            INSERT INTO topics (title, category, status)
            VALUES ($1, $2, 'pending')
            ON CONFLICT (title) DO NOTHING
            RETURNING id
        """, "Direct Test Topic", "pokemon")
        
        if topic_result:
            topic_id = topic_result['id']
            print(f"✅ Topic created: {topic_id}")
        else:
            # Get existing topic
            existing = await conn.fetchrow(
                "SELECT id FROM topics WHERE title = $1", "Direct Test Topic"
            )
            topic_id = existing['id']
            print(f"✅ Using existing topic: {topic_id}")
        
        # Test content insertion with proper JSONB
        print("🧪 Testing content insertion...")
        
        research_sources = ["https://example.com", "https://test.com"]
        metadata = {"test": True, "direct_connection": True}
        
        content_result = await conn.fetchrow("""
            INSERT INTO content (topic_id, topic_title, category, final_content, research_sources, metadata)
            VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
            RETURNING id
        """, topic_id, "Direct Test Topic", "pokemon", 
            "This is a test article content.", 
            json.dumps(research_sources), 
            json.dumps(metadata))
        
        content_id = content_result['id']
        print(f"✅ Content created: {content_id}")
        
        # Test querying
        print("📊 Testing queries...")
        topics = await conn.fetch("SELECT title FROM topics")
        topic_titles = [row['title'] for row in topics]
        print(f"📋 Topics: {topic_titles}")
        
        await conn.close()
        
        print("\n🎉 Direct Neon test completed successfully!")
        print("✅ Connection working")
        print("✅ Tables created/verified")
        print("✅ Topic insertion working")
        print("✅ Content insertion working")
        print("✅ JSONB handling working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_neon_direct())
    exit(0 if success else 1)
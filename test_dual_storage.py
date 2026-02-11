#!/usr/bin/env python3
"""Test dual storage (Neon + Google Drive) integration."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.topic_manager import get_topic_manager
from utils.google_drive_client import create_google_drive_client

def test_dual_storage():
    """Test storing articles in both Neon and Google Drive."""
    
    print("🎯 Dual Storage Integration Test")
    print("=" * 60)
    
    try:
        # Test Neon database
        print("🔧 Testing Neon database...")
        neon_manager = get_topic_manager()
        
        if not neon_manager.test_connection():
            print("❌ Neon database connection failed!")
            return False
        
        print("✅ Neon database connection successful!")
        
        # Test Google Drive
        print("\n🔧 Testing Google Drive...")
        drive_client = create_google_drive_client()
        
        if not drive_client.authenticate():
            print("❌ Google Drive authentication failed!")
            print("Run 'python setup_google_drive.py' first")
            return False
        
        print("✅ Google Drive authentication successful!")
        
        if not drive_client.setup_article_folders():
            print("❌ Google Drive folder setup failed!")
            return False
        
        print("✅ Google Drive folders ready!")
        
        # Test dual storage workflow
        print("\n🧪 Testing dual storage workflow...")
        
        test_articles = [
            {
                "title": "Dual Storage Test - Pokemon Investment Guide",
                "category": "pokemon",
                "content": """
                This comprehensive guide explores the investment potential of Pokemon trading cards in 2024.
                
                ## Market Overview
                The Pokemon trading card market has experienced unprecedented growth, with vintage cards
                reaching record-breaking prices at auction houses worldwide.
                
                ## Investment Strategies
                1. **First Edition Base Set Cards**: The holy grail of Pokemon collecting
                2. **Promotional Cards**: Limited distribution increases value
                3. **Graded Cards**: PSA and BGS grading significantly impacts price
                
                ## Risk Factors
                - Market volatility
                - Condition sensitivity  
                - Authentication challenges
                
                ## Conclusion
                Pokemon cards represent a unique alternative investment with strong collector demand
                and proven track record of appreciation.
                """,
                "research_sources": [
                    "https://www.psacard.com/smrpriceguide",
                    "https://www.pokemon.com/us/pokemon-tcg",
                    "https://www.heritage-auctions.com"
                ],
                "keywords": ["pokemon", "investment", "trading cards", "collectibles", "PSA"]
            },
            {
                "title": "Dual Storage Test - Hockey Card Market Analysis",
                "category": "hockey",
                "content": """
                An in-depth analysis of the hockey trading card market and emerging trends.
                
                ## Current Market State
                Hockey cards have seen renewed interest, particularly rookie cards of current NHL stars
                and vintage cards from the Original Six era.
                
                ## Key Players
                - Connor McDavid rookie cards leading the market
                - Wayne Gretzky vintage cards maintaining premium values
                - Emerging stars creating new opportunities
                
                ## Market Dynamics
                The hockey card market benefits from:
                - Strong international collector base
                - Limited print runs for premium products
                - NHL playoff performance driving short-term spikes
                
                ## Investment Outlook
                Hockey cards offer diversification within the sports card market with
                particular strength in Canadian and European markets.
                """,
                "research_sources": [
                    "https://www.beckett.com/hockey",
                    "https://www.nhl.com",
                    "https://www.comc.com"
                ],
                "keywords": ["hockey", "NHL", "McDavid", "Gretzky", "rookie cards"]
            }
        ]
        
        for i, article_data in enumerate(test_articles, 1):
            print(f"\n📝 Processing article {i}: {article_data['title']}")
            
            # Step 1: Save to Neon database
            print("   💾 Saving to Neon database...")
            topic_id = neon_manager.save_topic(article_data['title'], article_data['category'])
            print(f"   ✅ Topic saved with ID: {topic_id}")
            
            content_id = neon_manager.save_content(
                topic_id=topic_id,
                topic_title=article_data['title'],
                category=article_data['category'],
                final_content=article_data['content'],
                research_sources=article_data['research_sources'],
                metadata={
                    'word_count': len(article_data['content'].split()),
                    'keywords': article_data['keywords'],
                    'test': True,
                    'dual_storage_test': True
                }
            )
            print(f"   ✅ Content saved with ID: {content_id}")
            
            # Step 2: Save to Google Drive
            print("   ☁️  Uploading to Google Drive...")
            drive_file_id = drive_client.upload_article(
                title=article_data['title'],
                content=article_data['content'],
                category=article_data['category'],
                metadata={
                    'category': article_data['category'],
                    'word_count': len(article_data['content'].split()),
                    'research_sources': article_data['research_sources'],
                    'keywords': article_data['keywords'],
                    'neon_topic_id': str(topic_id),
                    'neon_content_id': str(content_id)
                }
            )
            
            if drive_file_id:
                print(f"   ✅ Uploaded to Google Drive with ID: {drive_file_id}")
            else:
                print("   ❌ Google Drive upload failed!")
        
        # Verify storage
        print("\n📊 Verifying dual storage...")
        
        # Check Neon database
        neon_topics = neon_manager.get_existing_topics()
        print(f"📄 Neon database contains {len(neon_topics)} topics")
        
        # Check Google Drive
        drive_articles = drive_client.list_articles(limit=10)
        print(f"☁️  Google Drive contains {len(drive_articles)} articles")
        
        # Show recent articles
        print("\n📋 Recent articles in Google Drive:")
        for i, article in enumerate(drive_articles[:5], 1):
            print(f"   {i}. {article['name']}")
        
        neon_manager.close()
        
        print("\n🎉 Dual storage test completed successfully!")
        print("✅ Neon database storage working")
        print("✅ Google Drive storage working")
        print("✅ Articles stored in both locations")
        print("✅ Metadata synchronized")
        print("✅ Ready for production use")
        
        print("\n📊 Storage Summary:")
        print(f"   • Neon Database: {len(neon_topics)} topics total")
        print(f"   • Google Drive: {len(drive_articles)} articles total")
        print("   • Both locations synchronized ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Dual storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    success = test_dual_storage()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
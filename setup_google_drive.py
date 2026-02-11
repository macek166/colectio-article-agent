#!/usr/bin/env python3
"""Setup script for Google Drive integration."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.google_drive_client import GoogleDriveClient

def setup_google_drive():
    """Setup Google Drive integration."""
    
    print("🎯 Google Drive Integration Setup")
    print("=" * 50)
    
    # Check if credentials file exists
    credentials_file = os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE', 'credentials.json')
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        print("\n📋 To setup Google Drive integration, you need:")
        print("1. Google Cloud Project with Drive API enabled")
        print("2. OAuth 2.0 credentials JSON file")
        print("3. Download and save as 'credentials.json'")
        print("\nSee setup instructions below.")
        return False
    
    print(f"✅ Found credentials file: {credentials_file}")
    
    try:
        # Create client
        print("\n🔧 Creating Google Drive client...")
        client = GoogleDriveClient(credentials_file)
        
        # Authenticate
        print("🔐 Authenticating with Google Drive...")
        if not client.authenticate():
            print("❌ Authentication failed!")
            return False
        
        print("✅ Authentication successful!")
        
        # Setup folder structure
        print("\n📁 Setting up folder structure...")
        root_folder_name = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER', 'TCG Articles')
        
        if not client.setup_article_folders(root_folder_name):
            print("❌ Failed to setup folder structure!")
            return False
        
        print("✅ Folder structure created!")
        
        # Test upload
        print("\n🧪 Testing article upload...")
        
        test_content = """
        This is a test article to verify Google Drive integration.
        
        The TCG Content Generator can now store articles in both:
        1. Neon PostgreSQL Database (for structured data and queries)
        2. Google Drive (for easy access and sharing)
        
        This dual storage approach provides:
        - Database benefits: Fast queries, relationships, metadata
        - Google Drive benefits: Easy sharing, human-readable format, backup
        
        Articles are automatically organized by:
        - Category (Pokemon, Hockey, Soccer)
        - Date (YYYY-MM folders)
        - Unique filenames with timestamps
        """
        
        file_id = client.upload_article(
            title="Google Drive Integration Test",
            content=test_content,
            category="pokemon",
            metadata={
                "category": "pokemon",
                "word_count": len(test_content.split()),
                "research_sources": ["https://example.com/test"],
                "keywords": ["test", "integration", "google drive"],
                "test": True
            }
        )
        
        if file_id:
            print(f"✅ Test article uploaded successfully!")
            print(f"📄 File ID: {file_id}")
        else:
            print("❌ Test upload failed!")
            return False
        
        # List articles
        print("\n📋 Listing uploaded articles...")
        articles = client.list_articles(limit=5)
        
        if articles:
            print(f"Found {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"   {i}. {article['name']} ({article.get('created', 'Unknown date')})")
        else:
            print("No articles found (this might be normal for first setup)")
        
        print("\n🎉 Google Drive integration setup completed successfully!")
        print("✅ Authentication working")
        print("✅ Folder structure created")
        print("✅ Article upload working")
        print("✅ Ready for production use")
        
        print(f"\n📁 Your articles will be stored in:")
        print(f"   Google Drive → {root_folder_name} → [Category] → [YYYY-MM]")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_setup_instructions():
    """Print detailed setup instructions."""
    
    print("\n" + "=" * 80)
    print("📋 GOOGLE DRIVE SETUP INSTRUCTIONS")
    print("=" * 80)
    
    print("\n🔧 Step 1: Create Google Cloud Project")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create new project or select existing one")
    print("3. Note your project name/ID")
    
    print("\n🔧 Step 2: Enable Google Drive API")
    print("1. Go to: https://console.cloud.google.com/apis/library")
    print("2. Search for 'Google Drive API'")
    print("3. Click 'Enable'")
    
    print("\n🔧 Step 3: Create OAuth 2.0 Credentials")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click 'Create Credentials' → 'OAuth 2.0 Client IDs'")
    print("3. Choose 'Desktop application'")
    print("4. Name it 'TCG Content Generator'")
    print("5. Download the JSON file")
    
    print("\n🔧 Step 4: Save Credentials File")
    print("1. Rename downloaded file to 'credentials.json'")
    print("2. Place it in your project root directory")
    print("3. Make sure it's in .gitignore (never commit credentials!)")
    
    print("\n🔧 Step 5: Run Setup")
    print("1. Run: python setup_google_drive.py")
    print("2. Browser will open for Google authentication")
    print("3. Grant permissions to access Google Drive")
    print("4. Setup will create folder structure and test upload")
    
    print("\n🔒 Security Notes:")
    print("- Never commit credentials.json to version control")
    print("- token.json will be auto-generated (also don't commit)")
    print("- Add both files to .gitignore")
    print("- Use separate Google account for testing if preferred")
    
    print("\n📁 Folder Structure Created:")
    print("Google Drive/")
    print("└── TCG Articles/")
    print("    ├── Pokemon/")
    print("    │   ├── 2024-12/")
    print("    │   └── 2025-01/")
    print("    ├── Hockey/")
    print("    │   └── 2024-12/")
    print("    └── Soccer/")
    print("        └── 2024-12/")
    
    print("\n" + "=" * 80)

def main():
    """Main function."""
    
    success = setup_google_drive()
    
    if not success:
        print_setup_instructions()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
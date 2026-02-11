"""Google Drive client for storing articles in organized folders.

This module provides functionality to upload articles to Google Drive
with automatic folder organization by category and date.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
import io

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveClient:
    """Client for uploading articles to Google Drive."""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        """Initialize Google Drive client.
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON file
            token_file: Path to store OAuth token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.root_folder_id = None
        
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                logger.warning(f"Failed to load existing token: {e}")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Failed to authenticate: {e}")
                    return False
            
            # Save credentials for next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.warning(f"Failed to save token: {e}")
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive authentication successful")
            return True
        except Exception as e:
            logger.error(f"Failed to build Drive service: {e}")
            return False
    
    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Create a folder in Google Drive.
        
        Args:
            name: Folder name
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Not authenticated with Google Drive")
            return None
        
        try:
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Created folder '{name}' with ID: {folder_id}")
            return folder_id
            
        except HttpError as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None
    
    def find_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Find a folder by name.
        
        Args:
            name: Folder name to search for
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder ID if found, None otherwise
        """
        if not self.service:
            logger.error("Not authenticated with Google Drive")
            return None
        
        try:
            query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                folder_id = files[0]['id']
                logger.info(f"Found folder '{name}' with ID: {folder_id}")
                return folder_id
            else:
                logger.info(f"Folder '{name}' not found")
                return None
                
        except HttpError as e:
            logger.error(f"Failed to search for folder '{name}': {e}")
            return None
    
    def get_or_create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Get existing folder or create new one.
        
        Args:
            name: Folder name
            parent_id: Parent folder ID
            
        Returns:
            Folder ID if successful, None otherwise
        """
        # Try to find existing folder
        folder_id = self.find_folder(name, parent_id)
        
        # Create if not found
        if not folder_id:
            folder_id = self.create_folder(name, parent_id)
        
        return folder_id
    
    def setup_article_folders(self, root_folder_name: str = "TCG Articles") -> bool:
        """Setup folder structure for articles.
        
        Args:
            root_folder_name: Name of root folder for articles
            
        Returns:
            True if setup successful, False otherwise
        """
        if not self.service:
            logger.error("Not authenticated with Google Drive")
            return False
        
        try:
            # Create/get root folder
            self.root_folder_id = self.get_or_create_folder(root_folder_name)
            if not self.root_folder_id:
                logger.error("Failed to create root folder")
                return False
            
            # Create category folders
            categories = ['pokemon', 'hockey', 'soccer']
            for category in categories:
                folder_id = self.get_or_create_folder(
                    category.title(), 
                    self.root_folder_id
                )
                if not folder_id:
                    logger.warning(f"Failed to create {category} folder")
            
            logger.info("Article folder structure setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup article folders: {e}")
            return False
    
    def upload_article(
        self, 
        title: str, 
        content: str, 
        category: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Upload article to Google Drive.
        
        Args:
            title: Article title
            content: Article content
            category: Article category (pokemon, hockey, soccer)
            metadata: Additional metadata
            
        Returns:
            File ID if successful, None otherwise
        """
        if not self.service or not self.root_folder_id:
            logger.error("Google Drive not properly initialized")
            return None
        
        try:
            # Get category folder
            category_folder_id = self.get_or_create_folder(
                category.title(), 
                self.root_folder_id
            )
            
            if not category_folder_id:
                logger.error(f"Failed to get {category} folder")
                return None
            
            # Create date-based subfolder
            date_str = datetime.now().strftime("%Y-%m")
            date_folder_id = self.get_or_create_folder(
                date_str,
                category_folder_id
            )
            
            if not date_folder_id:
                logger.warning(f"Failed to create date folder, using category folder")
                date_folder_id = category_folder_id
            
            # Prepare article content with metadata
            article_text = self._format_article_content(title, content, metadata)
            
            # Create filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Upload file with conversion to Google Docs
            media = MediaIoBaseUpload(
                io.BytesIO(article_text.encode('utf-8')),
                mimetype='text/plain',
                resumable=True
            )
            
            file_metadata = {
                'name': title,  # Use clean title without extension for Google Docs
                'parents': [date_folder_id],
                'mimeType': 'application/vnd.google-apps.document'  # Convert to Google Doc
            }
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Uploaded article '{title}' to Google Drive with ID: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to upload article '{title}': {e}")
            return None
    
    def _format_article_content(
        self, 
        title: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ) -> str:
        """Format article content with metadata header.
        
        Args:
            title: Article title
            content: Article content
            metadata: Additional metadata
            
        Returns:
            Formatted article text
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"TITLE: {title}")
        lines.append(f"GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if metadata:
            lines.append(f"CATEGORY: {metadata.get('category', 'Unknown')}")
            lines.append(f"WORD COUNT: {metadata.get('word_count', 'Unknown')}")
            
            if 'research_sources' in metadata:
                lines.append("RESEARCH SOURCES:")
                sources = metadata['research_sources']
                if sources:
                    for i, source in enumerate(sources[:5], 1):
                        lines.append(f"  {i}. {source}")
                else:
                    lines.append("  (No web sources found - Generated from internal knowledge)")
            
            if 'keywords' in metadata:
                keywords = metadata.get('keywords', [])
                if keywords:
                    lines.append(f"KEYWORDS: {', '.join(keywords[:10])}")
        
        lines.append("=" * 80)
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("=" * 80)
        lines.append("Generated by TCG Content Generator")
        lines.append("Stored in Neon Database and Google Drive")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def list_articles(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List uploaded articles.
        
        Args:
            category: Filter by category (optional)
            limit: Maximum number of articles to return
            
        Returns:
            List of article information
        """
        if not self.service or not self.root_folder_id:
            logger.error("Google Drive not properly initialized")
            return []
        
        try:
            query = f"'{self.root_folder_id}' in parents"
            if category:
                category_folder_id = self.find_folder(category.title(), self.root_folder_id)
                if category_folder_id:
                    query = f"'{category_folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                orderBy='createdTime desc',
                pageSize=limit,
                fields="files(id, name, createdTime, size)"
            ).execute()
            
            files = results.get('files', [])
            articles = []
            
            for file in files:
                if file['name'].endswith('.txt'):
                    articles.append({
                        'id': file['id'],
                        'name': file['name'],
                        'created': file.get('createdTime'),
                        'size': file.get('size', 0)
                    })
            
            logger.info(f"Found {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to list articles: {e}")
            return []


def create_google_drive_client() -> GoogleDriveClient:
    """Create and return Google Drive client instance."""
    return GoogleDriveClient()


if __name__ == "__main__":
    # Test the Google Drive client
    client = GoogleDriveClient()
    
    print("Testing Google Drive client...")
    
    if client.authenticate():
        print("✅ Authentication successful!")
        
        if client.setup_article_folders():
            print("✅ Folder structure created!")
            
            # Test upload
            test_article = """
            This is a test article about Pokemon trading cards.
            
            Pokemon cards have been popular collectibles since the 1990s.
            The most valuable cards are often first edition holographic cards
            from the original Base Set.
            
            Investment in Pokemon cards has grown significantly in recent years,
            with some cards selling for hundreds of thousands of dollars.
            """
            
            file_id = client.upload_article(
                title="Test Pokemon Article",
                content=test_article,
                category="pokemon",
                metadata={
                    "category": "pokemon",
                    "word_count": len(test_article.split()),
                    "research_sources": ["https://example.com"],
                    "keywords": ["pokemon", "trading cards", "investment"]
                }
            )
            
            if file_id:
                print(f"✅ Test article uploaded! File ID: {file_id}")
            else:
                print("❌ Failed to upload test article")
        else:
            print("❌ Failed to setup folders")
    else:
        print("❌ Authentication failed")
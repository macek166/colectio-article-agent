#!/usr/bin/env python3
"""Create Neon project using API key and get connection string."""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_neon_project():
    """Create a new Neon project and return connection string."""
    
    api_key = os.getenv('NEON_API_KEY')
    if not api_key:
        print("❌ NEON_API_KEY not found in .env file")
        return None
    
    print("🚀 Creating Neon project...")
    print(f"📡 Using API key: {api_key[:20]}...")
    
    # Neon API endpoint
    url = "https://console.neon.tech/api/v2/projects"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Project configuration
    project_data = {
        "project": {
            "name": "colectio-article-agent",
            "region_id": "aws-us-east-1"  # You can change this
        }
    }
    
    try:
        # Create project
        response = requests.post(url, headers=headers, json=project_data, timeout=30)
        
        if response.status_code == 201:
            project = response.json()
            print("✅ Project created successfully!")
            
            # Extract project details
            project_id = project['project']['id']
            project_name = project['project']['name']
            
            print(f"📊 Project ID: {project_id}")
            print(f"📊 Project Name: {project_name}")
            
            # Get connection string
            connection_string = get_connection_string(api_key, project_id)
            
            if connection_string:
                # Update .env file
                update_env_file(connection_string)
                return connection_string
            else:
                print("❌ Failed to get connection string")
                return None
                
        else:
            print(f"❌ Failed to create project: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None

def get_connection_string(api_key, project_id):
    """Get connection string for the project."""
    
    print("🔗 Getting connection string...")
    
    # First get project details to find database name and branch
    project_url = f"https://console.neon.tech/api/v2/projects/{project_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get project details
        project_response = requests.get(project_url, headers=headers, timeout=30)
        
        if project_response.status_code != 200:
            print(f"❌ Failed to get project details: {project_response.status_code}")
            return None
        
        project_data = project_response.json()
        
        # Extract database name and branch info
        databases = project_data['project']['databases']
        branches = project_data['project']['branches']
        
        if not databases or not branches:
            print("❌ No databases or branches found")
            return None
        
        database_name = databases[0]['name']
        branch_id = branches[0]['id']
        
        print(f"📊 Database: {database_name}")
        print(f"📊 Branch: {branch_id}")
        
        # Now get connection string with proper parameters
        conn_url = f"https://console.neon.tech/api/v2/projects/{project_id}/connection_uri"
        params = {
            'database_name': database_name,
            'branch_id': branch_id
        }
        
        response = requests.get(conn_url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            connection_string = data.get('uri')
            
            if connection_string:
                print("✅ Connection string retrieved!")
                # Mask for display
                masked = connection_string[:30] + "..." + connection_string[-20:]
                print(f"📡 Connection: {masked}")
                return connection_string
            else:
                print("❌ No connection string in response")
                return None
        else:
            print(f"❌ Failed to get connection string: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting connection string: {e}")
        return None

def update_env_file(connection_string):
    """Update .env file with the connection string."""
    
    print("📝 Updating .env file...")
    
    try:
        # Read current .env file
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add or update NEON_CONNECTION_STRING
        if 'NEON_CONNECTION_STRING=' in content:
            # Replace existing line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('NEON_CONNECTION_STRING=') or line.startswith('# NEON_CONNECTION_STRING'):
                    lines[i] = f'NEON_CONNECTION_STRING={connection_string}'
                    break
            content = '\n'.join(lines)
        else:
            # Add new line
            content += f'\nNEON_CONNECTION_STRING={connection_string}\n'
        
        # Write back to file
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ .env file updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        print(f"Please manually add this line to your .env file:")
        print(f"NEON_CONNECTION_STRING={connection_string}")

def main():
    """Main function."""
    print("🎯 Neon Project Creator")
    print("=" * 50)
    
    connection_string = create_neon_project()
    
    if connection_string:
        print("\n🎉 Setup completed successfully!")
        print("✅ Neon project created")
        print("✅ Connection string retrieved")
        print("✅ .env file updated")
        print("\nNext steps:")
        print("1. Run: python setup_neon.py")
        print("2. Test: python test_database.py")
        return True
    else:
        print("\n❌ Setup failed!")
        print("Please check your API key and try again.")
        print("Or manually create project in console.neon.tech")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
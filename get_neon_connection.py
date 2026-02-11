#!/usr/bin/env python3
"""Get connection string for existing Neon project."""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_existing_projects():
    """List all existing Neon projects."""
    
    api_key = os.getenv('NEON_API_KEY')
    if not api_key:
        print("❌ NEON_API_KEY not found in .env file")
        return None
    
    print("📋 Listing existing Neon projects...")
    
    url = "https://console.neon.tech/api/v2/projects"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            
            print(f"✅ Found {len(projects)} projects:")
            for project in projects:
                print(f"   📊 {project['name']} (ID: {project['id']})")
            
            return projects
        else:
            print(f"❌ Failed to list projects: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error listing projects: {e}")
        return None

def get_project_connection_string(project_id):
    """Get connection string for a specific project."""
    
    api_key = os.getenv('NEON_API_KEY')
    
    print(f"🔗 Getting connection string for project: {project_id}")
    
    # Get project details first
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
            print(f"Response: {project_response.text}")
            return None
        
        project_data = project_response.json()
        project_info = project_data['project']
        
        print(f"📊 Project: {project_info['name']}")
        print(f"📊 Region: {project_info['region_id']}")
        
        # Get databases and branches
        databases = project_info.get('databases', [])
        branches = project_info.get('branches', [])
        
        if not databases:
            print("❌ No databases found in project")
            return None
        
        if not branches:
            print("❌ No branches found in project")
            return None
        
        # Use first database and main branch
        database_name = databases[0]['name']
        main_branch = None
        
        # Find main branch
        for branch in branches:
            if branch.get('primary', False) or branch['name'] == 'main':
                main_branch = branch
                break
        
        if not main_branch:
            main_branch = branches[0]  # Use first branch if no main found
        
        branch_id = main_branch['id']
        
        print(f"📊 Database: {database_name}")
        print(f"📊 Branch: {main_branch['name']} ({branch_id})")
        
        # Get connection string
        conn_url = f"https://console.neon.tech/api/v2/projects/{project_id}/connection_uri"
        params = {
            'database_name': database_name,
            'branch_id': branch_id,
            'role_name': project_info['owner']['email'].split('@')[0]  # Use email prefix as role
        }
        
        conn_response = requests.get(conn_url, headers=headers, params=params, timeout=30)
        
        if conn_response.status_code == 200:
            conn_data = conn_response.json()
            connection_string = conn_data.get('uri')
            
            if connection_string:
                print("✅ Connection string retrieved!")
                # Mask for display
                masked = connection_string[:30] + "..." + connection_string[-20:]
                print(f"📡 Connection: {masked}")
                return connection_string
            else:
                print("❌ No connection string in response")
                print(f"Response: {conn_data}")
                return None
        else:
            print(f"❌ Failed to get connection string: {conn_response.status_code}")
            print(f"Response: {conn_response.text}")
            
            # Try alternative approach - build connection string manually
            print("🔄 Trying to build connection string manually...")
            return build_connection_string_manually(project_info, database_name, main_branch)
            
    except Exception as e:
        print(f"❌ Error getting connection string: {e}")
        return None

def build_connection_string_manually(project_info, database_name, branch):
    """Build connection string manually from project info."""
    
    try:
        # Extract connection details
        region = project_info['region_id']
        project_id = project_info['id']
        
        # Get endpoint from branch
        endpoint = None
        if 'endpoints' in project_info:
            for ep in project_info['endpoints']:
                if ep['branch_id'] == branch['id']:
                    endpoint = ep
                    break
        
        if not endpoint:
            print("❌ No endpoint found for branch")
            return None
        
        host = endpoint['host']
        
        # Build connection string
        # Format: postgresql://username:password@host:port/database?sslmode=require
        # Note: We don't have the password, user will need to get it from console
        username = f"neondb_owner"  # Default username
        
        connection_string = f"postgresql://{username}:[PASSWORD]@{host}/{database_name}?sslmode=require"
        
        print("⚠️  Built partial connection string (password needed):")
        print(f"📡 {connection_string}")
        print("\n🔧 To get the complete connection string:")
        print("1. Go to console.neon.tech")
        print("2. Select your project")
        print("3. Go to 'Connection Details' or 'Dashboard'")
        print("4. Copy the full connection string with password")
        
        return connection_string
        
    except Exception as e:
        print(f"❌ Error building connection string: {e}")
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
        
        print("✅ .env file updated!")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

def main():
    """Main function."""
    print("🎯 Neon Connection String Retriever")
    print("=" * 50)
    
    # List existing projects
    projects = get_existing_projects()
    
    if not projects:
        return False
    
    # Use the first project (or the one we just created)
    target_project = None
    for project in projects:
        if 'colectio' in project['name'].lower():
            target_project = project
            break
    
    if not target_project:
        target_project = projects[0]  # Use first project
    
    print(f"\n🎯 Using project: {target_project['name']}")
    
    # Get connection string
    connection_string = get_project_connection_string(target_project['id'])
    
    if connection_string and '[PASSWORD]' not in connection_string:
        update_env_file(connection_string)
        print("\n🎉 Setup completed successfully!")
        print("✅ Connection string retrieved")
        print("✅ .env file updated")
        print("\nNext steps:")
        print("1. Run: python setup_neon.py")
        print("2. Test: python test_database.py")
        return True
    else:
        print("\n⚠️  Partial setup completed")
        print("Please get the full connection string from Neon console")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
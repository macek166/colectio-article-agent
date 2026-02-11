#!/usr/bin/env python3
"""Check Neon project status and guide user to get connection string."""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_project_status():
    """Check if Neon project is ready and has databases."""
    
    api_key = os.getenv('NEON_API_KEY')
    if not api_key:
        print("❌ NEON_API_KEY not found in .env file")
        return False
    
    print("🔍 Checking Neon project status...")
    
    # List projects to find our project
    url = "https://console.neon.tech/api/v2/projects"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to list projects: {response.status_code}")
            return False
        
        data = response.json()
        projects = data.get('projects', [])
        
        # Find our project
        target_project = None
        for project in projects:
            if 'colectio' in project['name'].lower():
                target_project = project
                break
        
        if not target_project:
            print("❌ Project 'colectio-article-agent' not found")
            return False
        
        project_id = target_project['id']
        project_name = target_project['name']
        
        print(f"✅ Found project: {project_name}")
        print(f"📊 Project ID: {project_id}")
        print(f"📊 Status: {target_project.get('status', 'unknown')}")
        
        # Get detailed project info
        project_url = f"https://console.neon.tech/api/v2/projects/{project_id}"
        project_response = requests.get(project_url, headers=headers, timeout=30)
        
        if project_response.status_code != 200:
            print(f"❌ Failed to get project details: {project_response.status_code}")
            return False
        
        project_data = project_response.json()
        project_info = project_data['project']
        
        # Check databases
        databases = project_info.get('databases', [])
        branches = project_info.get('branches', [])
        endpoints = project_info.get('endpoints', [])
        
        print(f"📊 Databases: {len(databases)}")
        print(f"📊 Branches: {len(branches)}")
        print(f"📊 Endpoints: {len(endpoints)}")
        
        if databases:
            print("✅ Project has databases - ready for connection!")
            
            # Show database info
            for db in databases:
                print(f"   🗄️  Database: {db['name']}")
            
            # Show branch info
            for branch in branches:
                status = "🟢 Active" if branch.get('primary', False) else "🔵 Branch"
                print(f"   🌿 {status}: {branch['name']}")
            
            # Show endpoint info
            for endpoint in endpoints:
                print(f"   🔗 Endpoint: {endpoint['host']}")
            
            print("\n🎯 Your project is ready!")
            print("Now get the connection string from Neon Console:")
            print("1. Go to https://console.neon.tech")
            print(f"2. Select project '{project_name}'")
            print("3. Look for 'Connection Details' or 'Dashboard'")
            print("4. Copy the PostgreSQL connection string")
            print("5. Run: python set_connection_string.py")
            
            return True
        else:
            print("⏳ Project is still initializing...")
            print("Databases are being created. This usually takes 1-2 minutes.")
            print("Please wait a moment and try again.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking project status: {e}")
        return False

def main():
    """Main function."""
    print("🎯 Neon Project Status Checker")
    print("=" * 50)
    
    # Check if we already have connection string
    conn_str = os.getenv('NEON_CONNECTION_STRING')
    if conn_str and conn_str.startswith('postgresql://') and 'password' not in conn_str.lower():
        print("✅ Connection string already configured!")
        masked = conn_str[:30] + "..." + conn_str[-20:]
        print(f"📡 Current: {masked}")
        print("\nTesting connection...")
        
        # Test the connection
        os.system('python setup_neon.py')
        return True
    
    # Check project status
    success = check_project_status()
    
    if success:
        print("\n🚀 Ready for connection string setup!")
        print("Run: python set_connection_string.py")
    else:
        print("\n⏳ Please wait for project initialization to complete")
        print("Try again in 1-2 minutes")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
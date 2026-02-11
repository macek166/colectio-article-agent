#!/usr/bin/env python3
"""Simple script to set Neon connection string in .env file."""

import os

def set_connection_string():
    """Prompt user for connection string and update .env file."""
    
    print("🔗 Neon Connection String Setup")
    print("=" * 40)
    print()
    print("Please get your connection string from Neon Console:")
    print("1. Go to console.neon.tech")
    print("2. Select project 'colectio-article-agent'")
    print("3. Find 'Connection Details' or 'Dashboard'")
    print("4. Copy the PostgreSQL connection string")
    print()
    print("It should look like:")
    print("postgresql://neondb_owner:XXXXXXXX@ep-icy-butterfly-22248351.us-east-1.aws.neon.tech/neondb?sslmode=require")
    print()
    
    # Get connection string from user
    connection_string = input("📝 Paste your connection string here: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided")
        return False
    
    if not connection_string.startswith('postgresql://'):
        print("❌ Invalid connection string format")
        print("Should start with 'postgresql://'")
        return False
    
    # Update .env file
    try:
        # Read current .env file
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace or add NEON_CONNECTION_STRING
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('NEON_CONNECTION_STRING=') or line.startswith('# NEON_CONNECTION_STRING'):
                lines[i] = f'NEON_CONNECTION_STRING={connection_string}'
                updated = True
                break
        
        if not updated:
            lines.append(f'NEON_CONNECTION_STRING={connection_string}')
        
        # Write back to file
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Connection string saved to .env file!")
        
        # Mask for display
        masked = connection_string[:30] + "..." + connection_string[-20:]
        print(f"📡 Saved: {masked}")
        
        print("\n🚀 Next steps:")
        print("1. Run: python setup_neon.py")
        print("2. Test: python test_database.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    success = set_connection_string()
    exit(0 if success else 1)
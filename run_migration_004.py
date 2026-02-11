
import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    dsn = os.getenv("NEON_CONNECTION_STRING")
    if not dsn:
        print("Error: NEON_CONNECTION_STRING not set")
        return

    print(f"Connecting to Neon DB...")
    try:
        conn = await asyncpg.connect(dsn)
        
        migration_file = "migrations/004_add_source_url_to_topics.sql"
        if os.path.exists(migration_file):
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            print(f"Executing migration: {migration_file}")
            print(f"SQL: {sql}")
            await conn.execute(sql)
            print("Migration successful!")
        else:
            print(f"Migration file not found: {migration_file}")
            
        await conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())

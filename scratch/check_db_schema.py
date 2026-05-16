import asyncio
import os
import asyncpg
import json

_PG_URL = os.getenv(
    "ARIFOS_MEMORY_POSTGRES_URL",
    "postgresql://arifos_admin:ArifPostgresVault2026!@postgres:5432/vault999",
)

async def check_schema():
    print(f"Connecting to {_PG_URL}...")
    try:
        conn = await asyncpg.connect(_PG_URL, timeout=5)
        print("Connected.")
        
        # Check if table exists and list columns
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'memory_store'
        """)
        
        if not columns:
            print("Table 'memory_store' NOT FOUND.")
        else:
            print("Table 'memory_store' columns:")
            for col in columns:
                print(f"  - {col['column_name']} ({col['data_type']})")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())

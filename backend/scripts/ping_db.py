import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load backend/.env explicitly
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

sys.path.insert(0, backend_dir)

from core.config import get_async_database_uri
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def ping():
    db_url = os.environ.get("DATABASE_URL") or get_async_database_uri()
    print(f"[{datetime.now().isoformat()}] Connecting to Supabase database...")
    engine = create_async_engine(db_url, connect_args={"timeout": 10, "statement_cache_size": 0})
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            print(f"[{datetime.now().isoformat()}] SUCCESS: Supabase is ALIVE and responded with: {val}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ERROR: Failed to ping database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(ping())


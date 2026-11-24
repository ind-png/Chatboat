import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import uvicorn

from core.config import settings, validate_production_settings
from db.session import engine
from db.base import Base
from api.v1.api import api_router

logger = logging.getLogger(__name__)

async def _keep_alive_task():
    """Background task to ping Supabase periodically to prevent inactivity pause."""
    while True:
        try:
            await asyncio.sleep(60 * 60 * 6)  # Runs every 6 hours
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Supabase keep-alive ping successful.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Supabase keep-alive ping warning: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    is_production = settings.ENVIRONMENT.lower() in {"production", "prod"}
    if not is_production:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    ping_task = asyncio.create_task(_keep_alive_task())
    try:
        yield
    finally:
        ping_task.cancel()
        try:
            await ping_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS configuration allowing frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Primary API Router (includes auth, users, and tickets)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct root-level /auth router for backward compatibility
from api.v1.endpoints.auth import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])



@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs"
    }


@app.get("/health/db")
async def health_db():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

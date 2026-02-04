import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from . import database as db
from .config import FRONTEND_URLS
from .routers import auth_router, projects_router, tasks_router

logger = logging.getLogger("taskforge.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="TaskForge API", version="1.0.0", lifespan=lifespan)

# Request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        status_code = response.status_code if response else status.HTTP_500_INTERNAL_SERVER_ERROR
        payload = {
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
        logger.info(json.dumps(payload))

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])

async def init_db(max_attempts: int = 10, delay_seconds: float = 1.0) -> None:
    """Initialize database tables with a simple retry for container startup."""
    last_error = None
    for _ in range(max_attempts):
        try:
            await asyncio.to_thread(_run_migrations)
            return
        except (OperationalError, OSError, Exception) as exc:
            last_error = exc
            await asyncio.sleep(delay_seconds)
    if last_error:
        raise last_error


def _run_migrations() -> None:
    from run_migrations import run_migrations

    run_migrations()


@app.get("/api/health")
async def health_check():
    async with db.SessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
        except (OperationalError, OSError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable",
            ) from exc
    return {"status": "healthy"}

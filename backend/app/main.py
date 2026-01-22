import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from .routers import auth_router
from . import database as db
from .config import FRONTEND_URLS

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="TaskForge API", version="1.0.0", lifespan=lifespan)

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

def init_db(max_attempts: int = 10, delay_seconds: float = 1.0) -> None:
    """Initialize database tables with a simple retry for container startup."""
    last_error = None
    for _ in range(max_attempts):
        try:
            db.Base.metadata.create_all(bind=db.engine)
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(delay_seconds)
    if last_error:
        raise last_error


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

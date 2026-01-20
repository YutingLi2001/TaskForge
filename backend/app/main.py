from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth_router
from .database import engine, Base
from .config import FRONTEND_URL

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskForge API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

"""Zervi Pattern Platform API entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, patterns


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Zervi Pattern Platform API",
    description="AI-first pattern intelligence for car seat cover manufacturing",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(patterns.router, prefix="/api/v1/patterns", tags=["patterns"])


@app.get("/")
async def root():
    return {
        "name": "Zervi Pattern Platform API",
        "version": "0.1.0",
        "status": "running",
    }

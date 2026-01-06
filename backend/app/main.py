"""
Main FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal
from app.routers import auth_router, todos_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting To-Do App API...")
    yield
    # Shutdown
    logger.info("Shutting down To-Do App API...")


app = FastAPI(
    title="To-Do App API",
    description="A simple to-do list application API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(todos_router)


@app.get("/")
def root():
    """Root endpoint returning API status."""
    return {
        "status": "ok",
        "message": "To-Do App API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    Returns status of API and database connectivity.
    """
    health_status = {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "database": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

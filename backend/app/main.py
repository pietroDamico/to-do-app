"""
Main FastAPI application entry point.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="To-Do App API",
    description="A simple to-do list application with user authentication",
    version="1.0.0"
)

# CORS configuration using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint returning API information."""
    return {
        "status": "ok",
        "message": "To-Do App API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns the health status of the API and database connection.
    """
    db_status = "unknown"
    db_message = ""
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
        db_message = "Database connection successful"
        logger.info("Health check: Database connection successful")
    except Exception as e:
        db_status = "unhealthy"
        db_message = f"Database connection failed: {str(e)}"
        logger.error(f"Health check: Database connection failed - {e}")
    
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "components": {
            "api": {
                "status": "healthy",
                "message": "API is running"
            },
            "database": {
                "status": db_status,
                "message": db_message
            }
        }
    }


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("Starting To-Do App API")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Shutting down To-Do App API")

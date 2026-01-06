"""
FastAPI routers for API endpoints.
"""
from app.routers.auth import router as auth_router
from app.routers.todos import router as todos_router

__all__ = ["auth_router", "todos_router"]

"""
Authentication dependencies for FastAPI route protection.
Provides JWT token validation and user extraction.
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate JWT token and return authenticated user.
    
    This dependency can be used in route handlers to require authentication:
    
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException 401: If token is missing, invalid, expired, or user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    try:
        # Decode and validate token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            logger.warning("Token validation failed: missing 'sub' claim")
            raise credentials_exception
        
        user_id = int(user_id_str)
        
    except JWTError as e:
        logger.warning(f"Token validation failed: {type(e).__name__}")
        raise credentials_exception
    except (ValueError, TypeError):
        logger.warning("Token validation failed: invalid 'sub' claim format")
        raise credentials_exception
    
    # Load user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        logger.warning(f"Token validation failed: user_id {user_id} not found")
        raise credentials_exception
    
    logger.debug(f"User authenticated: {user.id}")
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optionally validate JWT token and return authenticated user.
    
    This dependency can be used in routes that work with or without authentication:
    
        @router.get("/public-or-private")
        async def flexible_route(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            if current_user:
                return {"message": f"Hello, {current_user.username}!"}
            return {"message": "Hello, anonymous!"}
    
    Args:
        credentials: Optional HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object if token is valid, None otherwise
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            return None
        
        user_id = int(user_id_str)
        
    except (JWTError, ValueError, TypeError):
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

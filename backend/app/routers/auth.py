"""
Authentication router for user registration and login endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, LoginResponse, LoginUserInfo
from app.utils.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **username**: 3-50 characters, alphanumeric and underscore only
    - **password**: minimum 8 characters
    
    Returns the created user (without password).
    """
    # Log registration attempt (never log password)
    logger.info(f"Registration attempt for username: {user_data.username}")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning(f"Registration failed: username '{user_data.username}' already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Hash the password
    password_hash = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        password_hash=password_hash
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User registered successfully: {new_user.username} (id: {new_user.id})")
        return new_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    
    - **username**: The user's username (case-insensitive)
    - **password**: The user's password
    
    Returns an access token and user information on success.
    """
    # Log login attempt (never log password)
    logger.info(f"Login attempt for username: {login_data.username}")
    
    # Normalize username to lowercase for case-insensitive lookup
    username = login_data.username.lower()
    
    # Look up user by username
    user = db.query(User).filter(User.username == username).first()
    
    # Use generic error message to prevent username enumeration
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if user exists
    if not user:
        logger.warning(f"Login failed: username '{username}' not found")
        raise credentials_exception
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Login failed: invalid password for username '{username}'")
        raise credentials_exception
    
    # Generate JWT token
    token_data = {
        "sub": str(user.id),
        "username": user.username
    }
    access_token = create_access_token(data=token_data)
    
    logger.info(f"Login successful for user_id: {user.id}")
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=LoginUserInfo(id=user.id, username=user.username)
    )

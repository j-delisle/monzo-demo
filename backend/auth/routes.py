from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from models import UserCreate, UserLogin, Token, User
from auth.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)
from database.repository import db
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=User)
async def signup(user_data: UserCreate):
    # Check if user already exists
    if db.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        name=user_data.name,
        created_at=datetime.now()
    )

    db.create_user(new_user)
    db.set_user_password_hash(user_data.email, hashed_password)

    # Create default accounts for new user
    from models import Account

    default_accounts = [
        Account(
            id=str(uuid.uuid4()),
            name="Current Account",
            balance=100.0,
            user_id=new_user.id
        ),
        Account(
            id=str(uuid.uuid4()),
            name="Savings Account",
            balance=500.0,
            user_id=new_user.id
        )
    ]

    # Add accounts using repository
    for account in default_accounts:
        db.add_account(account)

    return new_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    logger.info(f"Login attempt for email: {user_credentials.email}")
    
    # Check if user exists first
    user_exists = db.get_user_by_email(user_credentials.email)
    if not user_exists:
        logger.warning(f"Login failed: User {user_credentials.email} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User {user_credentials.email} found, checking password")
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        logger.warning(f"Login failed: Invalid password for {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Login successful for {user_credentials.email}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/demo-login", response_model=Token)
async def demo_login():
    """Quick login for demo purposes"""
    logger.info("Demo login attempt")
    
    user = db.get_user_by_email("demo@monzo.com")
    if not user:
        logger.error("Demo login failed: Demo user not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo user not found"
        )

    logger.info(f"Demo login successful for user: {user.email}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

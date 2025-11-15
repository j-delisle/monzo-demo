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
from database import db
import uuid
from datetime import datetime

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
            id=f"acc_{new_user.id}_1",
            name="Current Account",
            balance=100.0,
            user_id=new_user.id
        ),
        Account(
            id=f"acc_{new_user.id}_2", 
            name="Savings Account",
            balance=500.0,
            user_id=new_user.id
        )
    ]
    
    for account in default_accounts:
        db.accounts.append(account)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/demo-login", response_model=Token)
async def demo_login():
    """Quick login for demo purposes"""
    user = db.get_user_by_email("demo@monzo.com")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo user not found"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
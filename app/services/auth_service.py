from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.db.crud import crud_user
from app.core.security import verify_password

async def register_new_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Handle new user registration.
    Checks if user already exists and creates a new one if not.
    """
    existing_user = await crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user = await crud_user.create_user(db=db, user_in=user_in)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    Returns the user object if authentication is successful, None otherwise.
    """
    user = await crud_user.get_user_by_email(db, email=email)
    if not user:
        return None # User not found
    if not user.is_active:
        # You might want to raise an HTTPException here or handle it in the router
        return None # User is inactive
    if not verify_password(password, user.hashed_password):
        return None # Invalid password
        
    return user
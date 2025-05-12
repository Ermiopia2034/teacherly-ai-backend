from typing import Dict
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.user_model import User
from app.schemas.user_schema import UserCreate, ResetPasswordRequest # Added ResetPasswordRequest for type hint
from app.db.crud import crud_user
from app.core.security import (
    verify_password,
    create_password_reset_token,
    verify_password_reset_token,
    get_password_hash # Needed for reset logic via update_user
)
from app.utils.email import send_email_async
from app.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

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


async def handle_forgot_password(db: AsyncSession, email: str):
    """
    Handles the forgot password request.
    Generates a reset token and sends it via email if the user exists.
    """
    user = await crud_user.get_user_by_email(db, email=email)
    
    if not user or not user.is_active:
        # Don't reveal if the user exists or not, or if they are inactive
        logger.info(f"Password reset requested for non-existent or inactive user: {email}")
        # Still return a success message to prevent user enumeration
        return {"message": "If an account with that email exists, a password reset link has been sent."}
        
    reset_token = create_password_reset_token(email=user.email)
    reset_link = f"{settings.FRONTEND_URL}/auth/reset-password/{reset_token}"
    
    subject = "Reset Your Password for Teacherly AI"
    body = f"""
    <html>
    <body>
        <p>Hi {user.full_name or 'there'},</p>
        <p>You requested a password reset for your Teacherly AI account.</p>
        <p>Click the link below to set a new password:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>Thanks,</p>
        <p>The Teacherly AI Team</p>
    </body>
    </html>
    """
    
    await send_email_async(subject=subject, email_to=user.email, body=body)
    
    logger.info(f"Password reset email sent to {email}")
    return {"message": "If an account with that email exists, a password reset link has been sent."}


async def handle_reset_password(db: AsyncSession, token: str, new_password: str) -> Dict[str, str]:
    """
    Handles the password reset using a token.
    Verifies the token, finds the user, and updates the password.
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )
        
    user = await crud_user.get_user_by_email(db, email=email)
    if not user:
        # Should not happen if token was valid, but as a safeguard
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with this token not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive",
        )
        
    # Use the update_user crud function which handles hashing
    # Pass password in a dictionary as expected by update_user
    await crud_user.update_user(db=db, user=user, user_in={"password": new_password})
    
    logger.info(f"Password successfully reset for user {email}")
    return {"message": "Password has been successfully reset."}
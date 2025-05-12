from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm # For form data login
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas import user_schema, token_schema
from app.services import auth_service
from app.core import security
from app.db.models.user_model import User
from app.core.config import settings # For cookie settings

router = APIRouter()

@router.post("/register", response_model=user_schema.UserRead)
async def register_user(
    user_in: user_schema.UserCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Register a new user.
    """
    # The service layer handles checking for existing users
    user = await auth_service.register_new_user(db=db, user_in=user_in)
    if not user: # Should be handled by service raising HTTPException, but as a safeguard
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user."
        )
    return user

@router.post("/login") # No response_model here as token is in cookie
async def login_for_access_token(
    response: Response, # To set the cookie
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # Using form data for login
):
    """
    Log in a user and set an HttpOnly access token cookie.
    Returns user details in the response body.
    """
    user = await auth_service.authenticate_user(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}, # Standard, even if using cookies
        )
    
    access_token = security.create_access_token(
        subject=str(user.id) # Ensure subject is a string for JWT
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, # in seconds
        samesite="lax", # Or "strict" or "none" (if cross-site)
        secure=True if settings.API_V1_STR.startswith("https") else False, # Set Secure flag in production
        path="/" # Cookie available for all paths
    )
    # Return user info in body as per plan
    return user_schema.UserRead.from_orm(user)


@router.post("/logout")
async def logout(response: Response):
    """
    Log out a user by clearing the access token cookie.
    """
    response.delete_cookie(key="access_token", path="/", httponly=True)
    return {"message": "Successfully logged out"}

@router.get("/users/me", response_model=user_schema.UserRead)
async def read_users_me(
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get current logged-in user.
    """
    return current_user
# --- Forgot/Reset Password Endpoints ---

@router.post("/forgot-password")
async def request_password_reset(
    request: user_schema.ForgotPasswordRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Request a password reset link to be sent via email.
    """
    # The service handles finding the user and sending the email (or not)
    # It returns a generic message to prevent user enumeration
    result = await auth_service.handle_forgot_password(db=db, email=request.email)
    return result # e.g., {"message": "If an account exists..."}

@router.post("/reset-password")
async def reset_password(
    request: user_schema.ResetPasswordRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Reset the user's password using a valid token.
    """
    # The service handles token verification and password update
    # It raises HTTPException on errors (invalid token, user not found, etc.)
    result = await auth_service.handle_reset_password(
        db=db, token=request.token, new_password=request.new_password
    )
    return result # e.g., {"message": "Password has been successfully reset."}
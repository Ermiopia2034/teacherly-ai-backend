from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db # Using the one from database.py
from app.core import security
from app.schemas.token_schema import TokenData
from app.db.models.user_model import User
from app.db.crud import crud_user

# Define the cookie security scheme
# The name "access_token" should match the cookie name set during login
oauth2_scheme_cookie = APIKeyCookie(name="access_token", auto_error=False)

async def get_current_user(
    token: Optional[str] = Security(oauth2_scheme_cookie), 
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if token is None:
        # Allow unauthenticated access if token is not present,
        # specific routes can enforce authentication by checking if user is None.
        # Or, raise HTTPException if all routes using this must be authenticated.
        # For now, let's make it strict for routes that use get_current_active_user
        return None

    token_data: Optional[TokenData] = security.decode_access_token(token)
    if not token_data or token_data.user_id is None: # Check if user_id is present
        # If you want to be strict and always require a token for routes using this dependency:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid authentication credentials",
        #     headers={"WWW-Authenticate": "Bearer"}, # Though it's a cookie
        # )
        return None # Or handle as unauthenticated

    user = await crud_user.get_user_by_id(db, user_id=token_data.user_id)
    if not user:
        # This case means token is valid but user doesn't exist, which is unusual
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return None # Or handle as unauthenticated
    return user

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}, # Or a custom scheme for cookies
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
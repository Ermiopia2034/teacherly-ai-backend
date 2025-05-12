from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from app.schemas.token_schema import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Usually the user ID
        expires_delta: Token expiration time
        
    Returns:
        JWT token as a string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode JWT access token.
    
    Args:
        token: The JWT token string.
        
    Returns:
        TokenData if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # The 'sub' claim is expected to be the user_id as a string
        subject: Optional[str] = payload.get("sub")
        
        if subject is None:
            return None # No subject claim found
        
        try:
            user_id = int(subject)
        except ValueError:
            return None # Subject is not a valid integer for user_id
            
        return TokenData(user_id=user_id)
    except JWTError: # Catches various JWT errors like ExpiredSignatureError, InvalidTokenError
        return None
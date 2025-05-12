from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.user_model import User, UserRole
from app.schemas.user_schema import UserCreate
from app.core.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Create a new user.
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=UserRole.TEACHER  # Default role as per plan
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
from typing import Any, Dict

async def update_user(db: AsyncSession, user: User, user_in: Dict[str, Any]) -> User:
    """
    Update a user's information.
    Handles password hashing if a new password is provided in the input dictionary.
    """
    update_data = user_in.copy() # Work with a copy

    if "password" in update_data and update_data["password"]:
        # If a new password is provided, hash it and update the 'hashed_password' field
        hashed_password = get_password_hash(update_data["password"])
        setattr(user, "hashed_password", hashed_password)
        # Remove plain password from dict to avoid trying to set it directly on the model
        del update_data["password"] 
    elif "password" in update_data:
        # If 'password' key exists but is empty/None, remove it to avoid issues
        del update_data["password"]

    # Update other fields provided in user_in
    for field, value in update_data.items():
        # Ensure the field exists on the User model before attempting to set it
        if hasattr(user, field) and field != "hashed_password": # Avoid overwriting hashed_password again
             setattr(user, field, value)

    # Add the user object to the session (SQLAlchemy handles updates)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
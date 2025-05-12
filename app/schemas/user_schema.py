from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Assuming UserRole is defined in your models, adjust import as necessary
from app.db.models.user_model import UserRole
# For now, let's define it here if not readily importable or to avoid circular deps
# import enum

# class UserRole(enum.Enum):
#     TEACHER = "teacher"
#     ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr # Changed from username to email to align with User model
    password: str

class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    # updated_at: Optional[datetime] # Add if needed

    class Config:
        # orm_mode = True # Pydantic V1
        from_attributes = True # Pydantic V2
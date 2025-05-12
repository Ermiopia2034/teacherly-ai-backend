import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base # Corrected import from the new database.py
class UserRole(enum.Enum):
    TEACHER = "teacher"
    ADMIN = "admin" # For future use

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.TEACHER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # A teacher (user) can have many students
    students = relationship("Student", back_populates="teacher", cascade="all, delete-orphan")
    # A teacher (user) can create many content items
    content_items = relationship("Content", back_populates="teacher", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
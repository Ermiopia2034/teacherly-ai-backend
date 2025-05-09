from sqlalchemy.orm import declarative_base

# Base class for all SQLAlchemy models
Base = declarative_base()

# Import all models here so Alembic can find them
from .user_model import User
from .student_model import Student
from .content_model import Content
from .grade_model import Grade
from .attendance_model import Attendance
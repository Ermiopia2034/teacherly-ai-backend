# Import all models here so Alembic can find them, and ensure Base is imported consistently
# from ..database import Base # This line might be needed elsewhere if __init__ itself needs Base

from .user_model import User
from .student_model import Student
from .content_model import Content
from .grade_model import Grade
from .attendance_model import Attendance
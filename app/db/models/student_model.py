from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base # Import Base from the central database module

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    grade_level = Column(String(50), nullable=True) # e.g., "Grade 10", "Year 2"
    parent_email = Column(String(255), nullable=True) # For sending reports
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Link to the teacher
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher = relationship("User", back_populates="students")
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.full_name}', teacher_id={self.teacher_id})>"
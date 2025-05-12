import enum
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, func, Date, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base # Import Base from the central database module

class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attendance_date = Column(Date, nullable=False)
    status = Column(SAEnum(AttendanceStatus), nullable=False)
    notes = Column(Text, nullable=True) # Optional notes for the attendance record
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # When the attendance record was created

    # Relationships
    student = relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance(id={self.id}, student_id={self.student_id}, date='{self.attendance_date}', status='{self.status.value}')>"
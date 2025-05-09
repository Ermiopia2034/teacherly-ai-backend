from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..models import Base # Corrected import

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=True) # Max possible score for this assessment
    feedback = Column(Text, nullable=True) # AI generated or teacher's feedback
    grading_date = Column(DateTime(timezone=True), server_default=func.now())
    # Storing OCR text temporarily might be useful for audit/review, but can be large.
    # Consider if this is truly needed in the DB long-term or handled differently.
    # extracted_ocr_text = Column(Text, nullable=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False) # The exam/quiz this grade is for
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # When the grade record was created

    # Relationships
    student = relationship("Student", back_populates="grades")
    content = relationship("Content", back_populates="grades") # The specific exam/quiz

    def __repr__(self):
        return f"<Grade(id={self.id}, student_id={self.student_id}, content_id={self.content_id}, score={self.score})>"
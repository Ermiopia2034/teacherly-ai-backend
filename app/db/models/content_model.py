import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base # Import Base from the central database module

class ContentType(enum.Enum):
    MATERIAL = "material" # Teaching material, lesson plan, worksheet
    EXAM = "exam"
    QUIZ = "quiz"

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content_type = Column(SAEnum(ContentType), nullable=False)
    description = Column(Text, nullable=True)
    # For exams/quizzes: questions, options, type (multiple choice, short answer etc.)
    # For material: structure, text, links
    data = Column(JSON, nullable=True)
    # For exams/quizzes: correct answers, scoring logic if complex
    answer_key = Column(JSON, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Link to the teacher who created it
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher = relationship("User", back_populates="content_items")
    grades = relationship("Grade", back_populates="content", cascade="all, delete-orphan") # Grades for this exam/quiz

    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type.value}')>"
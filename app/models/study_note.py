from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.db.database import Base


class StudyNote(Base):
    __tablename__ = "study_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    original_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    quiz = Column(Text, nullable=True)
    slides = Column(Text, nullable=True)
    note_type = Column(String(40), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

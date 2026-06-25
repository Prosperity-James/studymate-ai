from sqlalchemy import Column, DateTime, Integer, Text, func

from app.db.database import Base


class Note(Base):
    """Represents a saved student note."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

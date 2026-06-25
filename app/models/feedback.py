from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, func

from app.db.database import Base


class FeedbackRecord(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=True, index=True)
    feature_type = Column(Text, nullable=False, default="summary")
    original_text = Column(Text, nullable=False)
    ai_output = Column(Text, nullable=False)
    user_corrected_output = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    trusted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

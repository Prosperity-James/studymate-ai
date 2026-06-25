from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.db.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False, unique=True, index=True)
    theme = Column(String(40), default="light")
    accent = Column(String(40), default="blue")
    card_style = Column(String(40), default="soft")
    persona = Column(String(40), default="student")
    summary_length = Column(String(40), default="balanced")
    explanation_style = Column(String(40), default="clear")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

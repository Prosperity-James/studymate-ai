from sqlalchemy.orm import Session

from app.models.preference import UserPreference
from app.schemas.study import PreferencesRequest


def get_or_create_preferences(db: Session, user_id: int) -> UserPreference:
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if prefs:
        return prefs

    prefs = UserPreference(user_id=user_id)
    db.add(prefs)
    db.commit()
    db.refresh(prefs)
    return prefs


def update_preferences(db: Session, user_id: int, payload: PreferencesRequest) -> UserPreference:
    prefs = get_or_create_preferences(db, user_id)
    prefs.theme = payload.theme
    prefs.accent = payload.accent
    prefs.card_style = payload.card_style
    prefs.persona = payload.persona
    prefs.summary_length = payload.summary_length
    prefs.explanation_style = payload.explanation_style
    db.commit()
    db.refresh(prefs)
    return prefs

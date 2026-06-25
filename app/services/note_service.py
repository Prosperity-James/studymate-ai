from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import SaveRequest


def create_note(db: Session, payload: SaveRequest) -> Note:
    """Saves a processed note to the database."""
    note = Note(
        original_text=payload.original_text,
        summary=payload.summary,
        explanation=payload.explanation,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes(db: Session):
    """Returns saved notes with the newest first."""
    return db.query(Note).order_by(Note.created_at.desc()).all()

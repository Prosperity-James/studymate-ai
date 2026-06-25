from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.router import api_router
from app.core.config import settings
from app.db.database import Base, engine
from app.models.feedback import FeedbackRecord
from app.models.preference import UserPreference
from app.models.study_note import StudyNote
from app.models.user import AppUser
from app.services.file_service import ensure_upload_dir


app = FastAPI(title=settings.app_name)

# Create database tables automatically if they do not already exist.
Base.metadata.create_all(bind=engine)
ensure_upload_dir()


def ensure_runtime_schema() -> None:
    """Adds lightweight missing columns for older local databases."""
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    statements = []

    if "user_preferences" in table_names:
        columns = {column["name"] for column in inspector.get_columns("user_preferences")}
        if "persona" not in columns:
            statements.append(
                "ALTER TABLE user_preferences ADD COLUMN persona VARCHAR(40) DEFAULT 'student'"
            )
        if "summary_length" not in columns:
            statements.append(
                "ALTER TABLE user_preferences ADD COLUMN summary_length VARCHAR(40) DEFAULT 'balanced'"
            )
        if "explanation_style" not in columns:
            statements.append(
                "ALTER TABLE user_preferences ADD COLUMN explanation_style VARCHAR(40) DEFAULT 'clear'"
            )

    added_note_type = False
    if "study_notes" in table_names:
        note_columns = {column["name"] for column in inspector.get_columns("study_notes")}
        if "note_type" not in note_columns:
            statements.append(
                "ALTER TABLE study_notes ADD COLUMN note_type VARCHAR(40) DEFAULT NULL"
            )
            added_note_type = True

    for statement in statements:
        with engine.begin() as connection:
            connection.execute(text(statement))

    if added_note_type:
        with engine.begin() as connection:
            connection.execute(text(
                "UPDATE study_notes SET note_type = "
                "CASE WHEN quiz IS NOT NULL AND quiz <> '' THEN 'quiz' "
                "WHEN slides IS NOT NULL AND slides <> '' THEN 'slides' "
                "WHEN explanation IS NOT NULL AND explanation <> '' THEN 'explanation' "
                "WHEN summary IS NOT NULL AND summary <> '' THEN 'summary' "
                "ELSE 'note' END "
                "WHERE note_type IS NULL"
            ))


ensure_runtime_schema()

app.include_router(api_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

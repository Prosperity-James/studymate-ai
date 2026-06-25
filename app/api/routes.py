from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.note import (
    ExplanationResponse,
    NoteResponse,
    SaveRequest,
    SummaryResponse,
    TextRequest,
)
from app.services.file_service import extract_text_from_file, save_upload_file
from app.services.nlp_service import nlp_service
from app.services.note_service import create_note, get_notes


router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
def summarize_text(payload: TextRequest):
    """Summarizes the provided text into bullet points."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    bullets = nlp_service.summarize_text(text)
    return SummaryResponse(bullets=bullets, source_text=text)


@router.post("/explain", response_model=ExplanationResponse)
def explain_text(payload: TextRequest):
    """Explains complex concepts in simpler language."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    explanation = nlp_service.simplify_concepts(text)
    keywords = nlp_service.extract_keywords(text)
    return ExplanationResponse(explanation=explanation, keywords=keywords)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a file and extracts its text for later processing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Please choose a file to upload.")

    file_path = await save_upload_file(file)
    extracted_text = extract_text_from_file(file_path)

    if not extracted_text:
        raise HTTPException(status_code=400, detail="No readable text was found in the file.")

    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
    }


@router.post("/save", response_model=NoteResponse)
def save_note(payload: SaveRequest, db: Session = Depends(get_db)):
    """Stores the original text, summary, and explanation in MySQL."""
    return create_note(db, payload)


@router.get("/history", response_model=list[NoteResponse])
def note_history(db: Session = Depends(get_db)):
    """Returns previously saved notes."""
    return get_notes(db)

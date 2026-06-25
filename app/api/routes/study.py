from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.study import (
    AskRequest,
    AskResponse,
    ExplainRequest,
    ExplainResponse,
    FeedbackRequest,
    FeedbackResponse,
    PreferencesRequest,
    PreferencesResponse,
    QuizResponse,
    SaveStudyNoteRequest,
    SlideResponse,
    SummaryResponse,
    TextRequest,
)
from app.services.auth_service import get_current_user, get_current_user_from_cookie
from app.services.feedback_service import create_feedback_record, get_feedback_records, set_feedback_trusted
from app.services.file_service import extract_text_from_file, save_upload_file
from app.services.nlp_service import nlp_service
from app.services import tts_service
from app.services.preference_service import get_or_create_preferences, update_preferences
from app.services.study_service import (
    create_study_note,
    delete_study_note,
    generate_quiz,
    generate_slides,
    get_study_notes,
    summarize_text,
    explain_text,
)


router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
async def summarize(payload: TextRequest, request: Request, db: Session = Depends(get_db)):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    current_user = get_current_user_from_cookie(request, db)
    bullets = await run_in_threadpool(
        summarize_text, text, payload.title, payload.file_name, db, getattr(current_user, "id", None)
    )
    return SummaryResponse(bullets=bullets, source_text=text)


@router.post("/explain", response_model=ExplainResponse)
async def explain(payload: ExplainRequest, request: Request, db: Session = Depends(get_db)):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    current_user = get_current_user_from_cookie(request, db)
    explanation, keywords = await run_in_threadpool(
        explain_text, text, payload.level, payload.title, payload.file_name, db, getattr(current_user, "id", None)
    )
    return ExplainResponse(level=payload.level, explanation=explanation, keywords=keywords)


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    answer = await run_in_threadpool(nlp_service.answer_question, question, payload.context)
    return AskResponse(answer=answer)


@router.post("/quiz", response_model=QuizResponse)
def quiz(payload: TextRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    return QuizResponse(questions=generate_quiz(text, payload.title, payload.file_name))


@router.post("/slides", response_model=SlideResponse)
def slides(payload: TextRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    return SlideResponse(slides=generate_slides(text, payload.title, payload.file_name))


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Please choose a file to upload.")

    file_path = await save_upload_file(file)
    extracted_text = extract_text_from_file(file_path)
    if not extracted_text:
        raise HTTPException(status_code=400, detail="No readable text was found in the file.")

    return {"filename": file.filename, "extracted_text": extracted_text}


@router.post("/save")
def save_note(
    payload: SaveStudyNoteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_study_note(db, current_user.id, payload)


@router.get("/history")
def history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_study_notes(db, current_user.id)


@router.delete("/history/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = delete_study_note(db, note_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}


@router.get("/preferences", response_model=PreferencesResponse)
def preferences(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    prefs = get_or_create_preferences(db, current_user.id)
    return PreferencesResponse.model_validate(prefs)


@router.post("/preferences", response_model=PreferencesResponse)
def save_preferences(
    payload: PreferencesRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    prefs = update_preferences(db, current_user.id, payload)
    return PreferencesResponse.model_validate(prefs)


@router.post("/feedback", response_model=FeedbackResponse)
def save_feedback(
    payload: FeedbackRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_current_user_from_cookie(request, db)
    record = create_feedback_record(db, payload, user_id=getattr(current_user, "id", None))
    return FeedbackResponse.model_validate(record)


@router.get("/feedback/admin", response_model=list[FeedbackResponse])
def feedback_admin(
    feature_type: str | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_feedback_records(db, feature_type=feature_type)
    return [FeedbackResponse.model_validate(record) for record in records]


@router.post("/feedback/{feedback_id}/trust", response_model=FeedbackResponse)
def trust_feedback(
    feedback_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = set_feedback_trusted(db, feedback_id, trusted=True)
    if not record:
        raise HTTPException(status_code=404, detail="Feedback record not found.")
    return FeedbackResponse.model_validate(record)


# ── ElevenLabs TTS endpoints ──────────────────────────────────────────

@router.get("/tts/voices")
def tts_voices():
    """Return available ElevenLabs voices (or defaults if key not set)."""
    return {
        "configured": tts_service.is_configured(),
        "voices": tts_service.list_voices(),
    }


@router.post("/tts/speak")
def tts_speak(payload: dict):
    """
    Synthesize text with ElevenLabs and stream back MP3 audio.
    Body: { "text": "...", "voice_id": "...", "stability": 0.5, "similarity": 0.75, "speed": 1.0 }
    """
    from fastapi.responses import StreamingResponse

    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    if not tts_service.is_configured():
        raise HTTPException(status_code=503, detail="ElevenLabs API key is not configured.")

    voice_id   = payload.get("voice_id") or "EXAVITQu4vr4xnSDxMaL"
    stability  = float(payload.get("stability", 0.5))
    similarity = float(payload.get("similarity", 0.75))
    speed      = float(payload.get("speed", 1.0))

    try:
        stream = tts_service.synthesize_stream(text, voice_id, stability, similarity, speed)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return StreamingResponse(
        stream,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-cache"},
    )

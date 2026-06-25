from typing import List

from sqlalchemy.orm import Session

from app.models.study_note import StudyNote
from app.schemas.study import QuizQuestion, SaveStudyNoteRequest, SlideItem
from app.services.feedback_service import get_prompt_enhancement
from app.services.nlp_service import nlp_service


def build_study_context(text: str, title: str = "", file_name: str = "") -> str:
    context_parts = []

    if title.strip():
        context_parts.append(f"Note title: {title.strip()}.")
    if file_name.strip():
        context_parts.append(f"Source file: {file_name.strip()}.")

    context_parts.append(f"Study content: {text.strip()}")
    return "\n".join(context_parts)


def summarize_text(
    text: str,
    title: str = "",
    file_name: str = "",
    db: Session | None = None,
    user_id: int | None = None,
) -> List[str]:
    enriched_text = build_study_context(text, title, file_name)
    enhancement = get_prompt_enhancement(db, enriched_text, "summary", user_id) if db else None
    return nlp_service.summarize_text(enriched_text, enhancement=enhancement)


def explain_text(
    text: str,
    level: str,
    title: str = "",
    file_name: str = "",
    db: Session | None = None,
    user_id: int | None = None,
):
    enriched_text = build_study_context(text, title, file_name)
    topic_label = title.strip() or file_name.strip()
    enhancement = get_prompt_enhancement(db, enriched_text, "explanation", user_id) if db else None
    return nlp_service.generate_explanation(
        enriched_text,
        mode=level,
        topic_label=topic_label,
        enhancement=enhancement,
    )


def generate_quiz(text: str, title: str = "", file_name: str = "") -> List[QuizQuestion]:
    enriched_text = build_study_context(text, title, file_name)
    cleaned_text = nlp_service.clean_study_text(enriched_text)
    keywords = nlp_service.extract_keywords(cleaned_text, limit=4)
    sentences = nlp_service.select_key_sentences(cleaned_text, 4)
    questions: List[QuizQuestion] = []

    for index, sentence in enumerate(sentences):
        keyword = keywords[index % len(keywords)] if keywords else f"concept {index + 1}"
        questions.append(
            QuizQuestion(
                question=f"Which idea is most connected to '{keyword}' in the notes?",
                options=[
                    sentence[:90] + ("..." if len(sentence) > 90 else ""),
                    f"A definition unrelated to {keyword}",
                    f"A historical fact about {keyword}",
                    f"A random statement with no connection to the notes",
                ],
                answer=sentence[:90] + ("..." if len(sentence) > 90 else ""),
            )
        )

    if not questions:
        questions.append(
            QuizQuestion(
                question="What should you do before generating quiz questions?",
                options=[
                    "Provide meaningful study text",
                    "Delete the note",
                    "Close the app",
                    "Disable file uploads",
                ],
                answer="Provide meaningful study text",
            )
        )
    return questions


def generate_slides(text: str, title: str = "", file_name: str = "") -> List[SlideItem]:
    enriched_text = build_study_context(text, title, file_name)
    cleaned_text = nlp_service.clean_study_text(enriched_text)
    summary = nlp_service.summarize_text(cleaned_text)
    keywords = nlp_service.extract_keywords(cleaned_text)
    slides = [
        SlideItem(title="Topic Overview", points=summary[:3] or ["Add more text to build slides."]),
        SlideItem(title="Key Concepts", points=keywords[:5] or ["No key concepts detected yet."]),
    ]

    if len(summary) > 3:
        slides.append(SlideItem(title="Important Details", points=summary[3:6]))

    slides.append(
        SlideItem(
            title="Revision Prompt",
            points=[
                "Explain the topic in your own words.",
                "Review the keywords and connect them to the summary.",
                "Turn the explanation into flashcards or quick revision notes.",
            ],
        )
    )
    return slides


def create_study_note(db: Session, user_id: int, payload: SaveStudyNoteRequest) -> StudyNote:
    note_type = payload.note_type.strip() or (
        "quiz" if payload.quiz else
        "slides" if payload.slides else
        "explanation" if payload.explanation else
        "summary" if payload.summary else
        "note"
    )
    note = StudyNote(
        user_id=user_id,
        title=payload.title,
        original_text=payload.original_text,
        summary=payload.summary,
        explanation=payload.explanation,
        quiz=payload.quiz,
        slides=payload.slides,
        note_type=note_type,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_study_notes(db: Session, user_id: int):
    return (
        db.query(StudyNote)
        .filter(StudyNote.user_id == user_id)
        .order_by(StudyNote.created_at.desc())
        .all()
    )


def delete_study_note(db: Session, note_id: int, user_id: int) -> bool:
    note = db.query(StudyNote).filter(StudyNote.id == note_id, StudyNote.user_id == user_id).first()
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True

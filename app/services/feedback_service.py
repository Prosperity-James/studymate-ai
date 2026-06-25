import re
from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.feedback import FeedbackRecord
from app.models.preference import UserPreference
from app.schemas.study import FeedbackRequest


@dataclass
class PromptEnhancement:
    """Controlled prompt improvements built from trusted feedback only."""

    examples: list[str]
    extra_instruction: str
    personalization_instruction: str


def create_feedback_record(db: Session, payload: FeedbackRequest, user_id: int | None = None) -> FeedbackRecord:
    record = FeedbackRecord(
        user_id=user_id,
        feature_type=payload.feature_type,
        original_text=payload.original_text,
        ai_output=payload.ai_output,
        user_corrected_output=payload.user_corrected_output.strip() or None,
        rating=payload.rating,
        trusted=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def set_feedback_trusted(db: Session, feedback_id: int, trusted: bool = True) -> FeedbackRecord | None:
    record = db.query(FeedbackRecord).filter(FeedbackRecord.id == feedback_id).first()
    if not record:
        return None
    record.trusted = trusted
    db.commit()
    db.refresh(record)
    return record


def get_feedback_records(db: Session, feature_type: str | None = None) -> list[FeedbackRecord]:
    query = db.query(FeedbackRecord).order_by(FeedbackRecord.created_at.desc())
    if feature_type:
        query = query.filter(FeedbackRecord.feature_type == feature_type)
    return query.limit(100).all()


def tokenize_for_similarity(text: str) -> set[str]:
    return set(re.findall(r"\b[a-zA-Z]{4,}\b", text.lower()))


def similarity_score(source_text: str, candidate_text: str) -> int:
    source_tokens = tokenize_for_similarity(source_text)
    candidate_tokens = tokenize_for_similarity(candidate_text)
    return len(source_tokens.intersection(candidate_tokens))


def get_user_preference_instruction(db: Session, user_id: int | None, feature_type: str) -> str:
    if not user_id:
        return ""

    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not prefs:
        return ""

    if feature_type == "summary":
        mapping = {
            "short": "Keep the summary short and revision-focused.",
            "balanced": "Keep the summary balanced, clear, and concise.",
            "detailed": "Allow a little more detail while staying structured.",
        }
        return mapping.get(prefs.summary_length, "")

    mapping = {
        "clear": "Keep the explanation simple and easy to follow.",
        "detailed": "Provide a little more depth while staying student-friendly.",
        "step-by-step": "Use a strongly step-by-step teaching style.",
    }
    return mapping.get(prefs.explanation_style, "")


def build_feedback_examples(records: list[FeedbackRecord]) -> list[str]:
    examples = []
    for record in records[:2]:
        better_output = record.user_corrected_output or record.ai_output
        examples.append(
            "Here is a good example of how this output should look:\n"
            f"INPUT:\n{record.original_text[:700]}\n"
            f"OUTPUT:\n{better_output[:700]}"
        )
    return examples


def build_adaptive_instruction(records: list[FeedbackRecord]) -> str:
    likes = sum(1 for record in records if record.rating == 1)
    dislikes = sum(1 for record in records if record.rating == -1)
    corrected = sum(1 for record in records if record.user_corrected_output)

    instructions = []
    if dislikes > likes:
        instructions.append("Be simpler, more structured, and more concise than usual.")
    if corrected >= 3:
        instructions.append("Prefer the style shown in corrected examples and avoid overly generic phrasing.")
    return " ".join(instructions)


def get_prompt_enhancement(
    db: Session,
    source_text: str,
    feature_type: str,
    user_id: int | None = None,
) -> PromptEnhancement:
    """Only uses controlled, trusted feedback signals to improve future prompts."""
    query = (
        db.query(FeedbackRecord)
        .filter(FeedbackRecord.feature_type == feature_type)
        .filter(
            or_(
                FeedbackRecord.trusted.is_(True),
                FeedbackRecord.rating == 1,
                FeedbackRecord.user_corrected_output.isnot(None),
            )
        )
    )
    records = query.all()
    ranked = sorted(records, key=lambda record: similarity_score(source_text, record.original_text), reverse=True)
    examples = build_feedback_examples([record for record in ranked if similarity_score(source_text, record.original_text) > 0])
    adaptive_instruction = build_adaptive_instruction(records)
    personalization_instruction = get_user_preference_instruction(db, user_id, feature_type)
    return PromptEnhancement(
        examples=examples[:2],
        extra_instruction=adaptive_instruction,
        personalization_instruction=personalization_instruction,
    )

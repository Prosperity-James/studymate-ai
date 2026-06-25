from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


ExplainLevel = Literal["basic", "intermediate", "advanced"]


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    title: str = ""
    file_name: str = ""


class ExplainRequest(TextRequest):
    level: ExplainLevel = "basic"


class SummaryResponse(BaseModel):
    bullets: List[str]
    source_text: str


class ExplainResponse(BaseModel):
    level: ExplainLevel
    explanation: List[str]
    keywords: List[str]


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]


class SlideItem(BaseModel):
    title: str
    points: List[str]


class SlideResponse(BaseModel):
    slides: List[SlideItem]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: str = ""


class AskResponse(BaseModel):
    answer: str


class SaveStudyNoteRequest(BaseModel):
    title: str = Field(..., min_length=2)
    original_text: str = Field(..., min_length=1)
    summary: str = ""
    explanation: str = ""
    quiz: str = ""
    slides: str = ""
    note_type: str = ""


class StudyNoteResponse(BaseModel):
    id: int
    title: str
    original_text: str
    summary: str | None
    explanation: str | None
    quiz: str | None
    slides: str | None
    note_type: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreferencesRequest(BaseModel):
    theme: str = "light"
    accent: str = "blue"
    card_style: str = "soft"
    persona: str = "student"
    summary_length: str = "balanced"
    explanation_style: str = "clear"


class PreferencesResponse(BaseModel):
    theme: str
    accent: str
    card_style: str
    persona: str
    summary_length: str
    explanation_style: str

    model_config = ConfigDict(from_attributes=True)


class FeedbackRequest(BaseModel):
    feature_type: Literal["summary", "explanation"]
    original_text: str = Field(..., min_length=1)
    ai_output: str = Field(..., min_length=1)
    user_corrected_output: str = ""
    rating: int | None = Field(default=None, ge=-1, le=1)


class FeedbackResponse(BaseModel):
    id: int
    feature_type: str
    original_text: str
    ai_output: str
    user_corrected_output: str | None
    rating: int | None
    trusted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

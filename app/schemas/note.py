from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to process.")


class SummaryResponse(BaseModel):
    bullets: List[str]
    source_text: str


class ExplanationResponse(BaseModel):
    explanation: List[str]
    keywords: List[str]


class SaveRequest(BaseModel):
    original_text: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: int
    original_text: str
    summary: str
    explanation: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

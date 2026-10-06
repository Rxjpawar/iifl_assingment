from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class EntryCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=20_000)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Text must not be blank")
        return value


class EntryResponse(BaseModel):
    id: int
    original_text: str
    summary: str
    tags: list[str]
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def created_at_is_utc(cls, value: datetime) -> datetime:
        # SQLite drops tzinfo; values are stored as UTC, so mark them as such
        # to let clients convert to local time correctly.
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

    model_config = {"from_attributes": True}

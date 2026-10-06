import json

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.entry import Entry
from app.core.exceptions import EntryNotFoundException
from app.schemas.entry import EntryCreate, EntryResponse
from app.services.ai_service import generate_content

router = APIRouter()


def serialize_entry(entry: Entry) -> EntryResponse:
    return EntryResponse(
        id=entry.id,
        original_text=entry.original_text,
        summary=entry.summary,
        tags=json.loads(entry.tags_json),
        created_at=entry.created_at,
    )


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(payload: EntryCreate, db: Session = Depends(get_db)) -> EntryResponse:
    ai_result = await generate_content(payload.text)

    entry = Entry(
        original_text=payload.text,
        summary=ai_result["summary"],
        tags_json=json.dumps(ai_result["tags"]),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return serialize_entry(entry)


@router.get("", response_model=list[EntryResponse])
def list_entries(db: Session = Depends(get_db)) -> list[EntryResponse]:
    entries = db.scalars(select(Entry).order_by(Entry.created_at.desc())).all()
    return [serialize_entry(entry) for entry in entries]


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(entry_id: int, db: Session = Depends(get_db)) -> EntryResponse:
    entry = db.get(Entry, entry_id)
    if entry is None:
        raise EntryNotFoundException(entry_id)
    return serialize_entry(entry)

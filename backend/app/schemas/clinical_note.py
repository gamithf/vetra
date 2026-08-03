import uuid
from datetime import datetime
from pydantic import BaseModel
from app.enums import ClinicalNoteStatus


class ClinicalNoteCreate(BaseModel):
    pet_id: uuid.UUID
    appointment_id: uuid.UUID
    raw_transcript: str
    structured_note: str | None = None
    ai_model_version: str | None = None
    status: ClinicalNoteStatus | None = None


class ClinicalNoteUpdate(BaseModel):
    raw_transcript: str | None = None
    structured_note: str | None = None
    status: ClinicalNoteStatus | None = None
    is_edited: bool | None = None


class ClinicalNoteResponse(BaseModel):
    id: uuid.UUID
    pet_id: uuid.UUID
    appointment_id: uuid.UUID | None
    vet_id: uuid.UUID
    raw_transcript: str
    structured_note: str | None
    status: ClinicalNoteStatus
    ai_model_version: str | None
    is_edited: bool
    reviewed_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

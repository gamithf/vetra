import uuid
from datetime import datetime
from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    clinical_note_id: uuid.UUID | None = None
    pet_id: uuid.UUID
    medication_name: str
    dosage: str
    frequency: str
    duration: str | None = None
    route: str | None = None
    notes: str | None = None


class PrescriptionUpdate(BaseModel):
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    route: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class PrescriptionResponse(BaseModel):
    id: uuid.UUID
    clinical_note_id: uuid.UUID | None
    pet_id: uuid.UUID
    vet_id: uuid.UUID
    medication_name: str
    dosage: str
    frequency: str
    duration: str | None
    route: str | None
    notes: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

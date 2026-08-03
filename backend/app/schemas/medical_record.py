import uuid
from datetime import datetime
from pydantic import BaseModel
from app.enums import RecordType


class MedicalRecordCreate(BaseModel):
    pet_id: uuid.UUID
    vet_id: uuid.UUID | None = None
    appointment_id: uuid.UUID | None = None
    record_type: RecordType = RecordType.EXAMINATION
    diagnosis: str | None = None
    treatment: str | None = None
    notes: str | None = None


class MedicalRecordUpdate(BaseModel):
    record_type: RecordType | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    notes: str | None = None


class MedicalRecordResponse(BaseModel):
    id: uuid.UUID
    pet_id: uuid.UUID
    vet_id: uuid.UUID | None
    appointment_id: uuid.UUID | None
    record_type: RecordType
    diagnosis: str | None
    treatment: str | None
    notes: str | None
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}

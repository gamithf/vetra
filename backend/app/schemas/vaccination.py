import uuid
from datetime import datetime, date
from pydantic import BaseModel


class VaccinationCreate(BaseModel):
    pet_id: uuid.UUID
    vaccine_name: str
    vaccine_type: str | None = None
    administered_date: date
    next_due_date: date | None = None
    vet_id: uuid.UUID | None = None
    batch_number: str | None = None
    notes: str | None = None


class VaccinationUpdate(BaseModel):
    next_due_date: date | None = None
    notes: str | None = None


class VaccinationResponse(BaseModel):
    id: uuid.UUID
    pet_id: uuid.UUID
    vaccine_name: str
    vaccine_type: str | None
    administered_date: date
    next_due_date: date | None
    vet_id: uuid.UUID | None
    batch_number: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

import uuid
from datetime import datetime
from pydantic import BaseModel
from app.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    pet_id: uuid.UUID
    vet_id: uuid.UUID | None = None
    owner_id: uuid.UUID
    room_id: uuid.UUID | None = None
    start_time: datetime
    end_time: datetime
    reason: str | None = None
    notes: str | None = None
    is_urgent: bool = False


class AppointmentUpdate(BaseModel):
    vet_id: uuid.UUID | None = None
    room_id: uuid.UUID | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: AppointmentStatus | None = None
    reason: str | None = None
    notes: str | None = None
    is_urgent: bool | None = None


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    pet_id: uuid.UUID
    vet_id: uuid.UUID | None
    owner_id: uuid.UUID
    room_id: uuid.UUID | None
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    reason: str | None
    notes: str | None
    is_urgent: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

import uuid
from datetime import datetime, date
from pydantic import BaseModel


class LabResultCreate(BaseModel):
    pet_id: uuid.UUID
    appointment_id: uuid.UUID | None = None
    test_name: str
    test_category: str | None = None
    result_value: str | None = None
    reference_range: str | None = None
    unit: str | None = None
    is_abnormal: bool = False
    notes: str | None = None
    performed_by: uuid.UUID | None = None
    result_date: date


class LabResultUpdate(BaseModel):
    result_value: str | None = None
    reference_range: str | None = None
    is_abnormal: bool | None = None
    notes: str | None = None


class LabResultResponse(BaseModel):
    id: uuid.UUID
    pet_id: uuid.UUID
    appointment_id: uuid.UUID | None
    test_name: str
    test_category: str | None
    result_value: str | None
    reference_range: str | None
    unit: str | None
    is_abnormal: bool
    notes: str | None
    performed_by: uuid.UUID | None
    result_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}

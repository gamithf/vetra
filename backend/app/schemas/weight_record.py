import uuid
from datetime import datetime
from pydantic import BaseModel


class WeightRecordCreate(BaseModel):
    pet_id: uuid.UUID
    weight_kg: float


class WeightRecordResponse(BaseModel):
    id: uuid.UUID
    pet_id: uuid.UUID
    weight_kg: float
    recorded_by: uuid.UUID | None
    recorded_at: datetime

    model_config = {"from_attributes": True}

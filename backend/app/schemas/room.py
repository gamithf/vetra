import uuid
from datetime import datetime
from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    number: int | None = None


class RoomUpdate(BaseModel):
    name: str | None = None
    number: int | None = None
    is_active: bool | None = None


class RoomResponse(BaseModel):
    id: uuid.UUID
    name: str
    number: int | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

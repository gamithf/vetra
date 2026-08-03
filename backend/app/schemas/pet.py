import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.enums import PetSpecies, PetGender


class PetCreate(BaseModel):
    owner_id: uuid.UUID
    name: str
    species: PetSpecies
    breed: str | None = None
    color: str | None = None
    gender: PetGender = PetGender.UNKNOWN
    date_of_birth: date | None = None
    weight_kg: float | None = None
    microchip_id: str | None = None
    photo_url: str | None = None


class PetUpdate(BaseModel):
    name: str | None = None
    species: PetSpecies | None = None
    breed: str | None = None
    color: str | None = None
    gender: PetGender | None = None
    date_of_birth: date | None = None
    weight_kg: float | None = None
    microchip_id: str | None = None
    photo_url: str | None = None
    is_active: bool | None = None


class PetResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    species: PetSpecies
    breed: str | None
    color: str | None
    gender: PetGender
    date_of_birth: date | None
    weight_kg: float | None
    microchip_id: str | None
    photo_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

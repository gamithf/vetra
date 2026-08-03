import uuid
from datetime import datetime, timezone, date
from sqlmodel import SQLModel, Field, Column, String, Enum as SAEnum, Date, Float
from sqlalchemy import DateTime, ForeignKey
from app.enums import PetSpecies, PetGender


class Pet(SQLModel, table=True):
    __tablename__ = "pets"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    owner_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("owners.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))
    species: PetSpecies = Field(
        sa_column=Column(SAEnum(PetSpecies), nullable=False)
    )
    breed: str | None = Field(sa_column=Column(String(100), default=None))
    color: str | None = Field(sa_column=Column(String(100), default=None))
    gender: PetGender = Field(
        sa_column=Column(SAEnum(PetGender), nullable=False, default=PetGender.UNKNOWN)
    )
    date_of_birth: date | None = Field(sa_column=Column(Date, default=None))
    weight_kg: float | None = Field(sa_column=Column(Float, default=None))
    microchip_id: str | None = Field(sa_column=Column(String(50), default=None, index=True))
    photo_url: str | None = Field(sa_column=Column(String(500), default=None))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )

import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String, Text
from sqlalchemy import DateTime, ForeignKey


class Prescription(SQLModel, table=True):
    __tablename__ = "prescriptions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    clinical_note_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("clinical_notes.id", ondelete="SET NULL"), nullable=True)
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    vet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    medication_name: str = Field(sa_column=Column(String(255), nullable=False))
    dosage: str = Field(sa_column=Column(String(100), nullable=False))
    frequency: str = Field(sa_column=Column(String(100), nullable=False))
    duration: str | None = Field(sa_column=Column(String(100), default=None))
    route: str | None = Field(sa_column=Column(String(50), default=None))
    notes: str | None = Field(sa_column=Column(Text, default=None))
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

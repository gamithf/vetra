import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String, Enum as SAEnum, Text
from sqlalchemy import DateTime, ForeignKey
from app.enums import ClinicalNoteStatus


class ClinicalNote(SQLModel, table=True):
    __tablename__ = "clinical_notes"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    appointment_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    )
    vet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    raw_transcript: str = Field(sa_column=Column(Text, nullable=False))
    structured_note: str | None = Field(sa_column=Column(Text, default=None))
    status: ClinicalNoteStatus = Field(
        sa_column=Column(SAEnum(ClinicalNoteStatus), nullable=False, default=ClinicalNoteStatus.DRAFT)
    )
    ai_model_version: str | None = Field(sa_column=Column(String(50), default=None))
    is_edited: bool = Field(default=False)
    reviewed_by: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
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

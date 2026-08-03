import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String, Enum as SAEnum, Text
from sqlalchemy import DateTime, ForeignKey
from app.enums import RecordType


class MedicalRecord(SQLModel, table=True):
    __tablename__ = "medical_records"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    vet_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    appointment_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    )
    record_type: RecordType = Field(
        sa_column=Column(SAEnum(RecordType), nullable=False, default=RecordType.EXAMINATION)
    )
    diagnosis: str | None = Field(sa_column=Column(Text, default=None))
    treatment: str | None = Field(sa_column=Column(Text, default=None))
    notes: str | None = Field(sa_column=Column(Text, default=None))
    recorded_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )

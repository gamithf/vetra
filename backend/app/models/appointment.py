import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String, Enum as SAEnum, Text
from sqlalchemy import DateTime, ForeignKey
from app.enums import AppointmentStatus


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    vet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    )
    owner_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("owners.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    room_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    )
    start_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    end_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    status: AppointmentStatus = Field(
        sa_column=Column(SAEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    )
    reason: str | None = Field(sa_column=Column(Text, default=None))
    notes: str | None = Field(sa_column=Column(Text, default=None))
    is_urgent: bool = Field(default=False)
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

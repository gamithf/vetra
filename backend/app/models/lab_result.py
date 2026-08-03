import uuid
from datetime import datetime, timezone, date
from sqlmodel import SQLModel, Field, Column, String, Text, Boolean, Float
from sqlalchemy import DateTime, ForeignKey


class LabResult(SQLModel, table=True):
    __tablename__ = "lab_results"

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
    test_name: str = Field(sa_column=Column(String(255), nullable=False))
    test_category: str | None = Field(sa_column=Column(String(100), default=None))
    result_value: str | None = Field(sa_column=Column(Text, default=None))
    reference_range: str | None = Field(sa_column=Column(String(255), default=None))
    unit: str | None = Field(sa_column=Column(String(50), default=None))
    is_abnormal: bool = Field(default=False)
    notes: str | None = Field(sa_column=Column(Text, default=None))
    performed_by: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    result_date: date = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )

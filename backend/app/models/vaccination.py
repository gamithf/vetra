import uuid
from datetime import datetime, timezone, date
from sqlmodel import SQLModel, Field, Column, String, Date
from sqlalchemy import DateTime, ForeignKey


class Vaccination(SQLModel, table=True):
    __tablename__ = "vaccinations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    vaccine_name: str = Field(sa_column=Column(String(255), nullable=False))
    vaccine_type: str | None = Field(sa_column=Column(String(100), default=None))
    administered_date: date = Field(sa_column=Column(Date, nullable=False))
    next_due_date: date | None = Field(sa_column=Column(Date, default=None))
    vet_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    batch_number: str | None = Field(sa_column=Column(String(100), default=None))
    notes: str | None = Field(sa_column=Column(String(2000), default=None))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )

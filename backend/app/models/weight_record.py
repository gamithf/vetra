import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Float
from sqlalchemy import DateTime, ForeignKey


class WeightRecord(SQLModel, table=True):
    __tablename__ = "weight_records"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    weight_kg: float = Field(sa_column=Column(Float, nullable=False))
    recorded_by: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    recorded_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )

import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String, Integer
from sqlalchemy import DateTime


class Room(SQLModel, table=True):
    __tablename__ = "rooms"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))
    number: int | None = Field(sa_column=Column(Integer, default=None))
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

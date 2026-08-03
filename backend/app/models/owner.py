import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import DateTime


class Owner(SQLModel, table=True):
    __tablename__ = "owners"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    email: str | None = Field(sa_column=Column(String(255), default=None, index=True))
    phone: str | None = Field(sa_column=Column(String(50), default=None))
    address: str | None = Field(sa_column=Column(String(500), default=None))
    notes: str | None = Field(sa_column=Column(String(2000), default=None))
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

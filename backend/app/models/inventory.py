import uuid
from datetime import datetime, timezone, date
from sqlmodel import SQLModel, Field, Column, String, Integer, Float, Enum as SAEnum, Text, Date
from sqlalchemy import DateTime
from app.enums import InventoryCategory


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(sa_column=Column(String(255), nullable=False, index=True))
    category: InventoryCategory = Field(
        sa_column=Column(SAEnum(InventoryCategory), nullable=False)
    )
    description: str | None = Field(sa_column=Column(Text, default=None))
    unit: str = Field(sa_column=Column(String(50), nullable=False))
    quantity: float = Field(sa_column=Column(Float, nullable=False, default=0))
    min_quantity: float = Field(sa_column=Column(Float, nullable=False, default=10))
    price_per_unit: float | None = Field(sa_column=Column(Float, default=None))
    supplier: str | None = Field(sa_column=Column(String(255), default=None))
    batch_number: str | None = Field(sa_column=Column(String(100), default=None))
    expiry_date: date | None = Field(sa_column=Column(Date, default=None))
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

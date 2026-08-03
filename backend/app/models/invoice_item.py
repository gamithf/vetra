import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, String, Integer, Float, Text
from sqlalchemy import DateTime, ForeignKey


class InvoiceItem(SQLModel, table=True):
    __tablename__ = "invoice_items"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    invoice_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    description: str = Field(sa_column=Column(String(500), nullable=False))
    quantity: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    unit_price: float = Field(sa_column=Column(Float, nullable=False))
    total_price: float = Field(sa_column=Column(Float, nullable=False))
    notes: str | None = Field(sa_column=Column(Text, default=None))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    )

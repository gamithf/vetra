import uuid
from datetime import datetime, timezone, date
from sqlmodel import SQLModel, Field, Column, Float, Enum as SAEnum, Text, Date
from sqlalchemy import DateTime, ForeignKey
from app.enums import InvoiceStatus, PaymentMethod


class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    appointment_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    )
    owner_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("owners.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    pet_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    total_amount: float = Field(sa_column=Column(Float, nullable=False, default=0))
    paid_amount: float = Field(sa_column=Column(Float, nullable=False, default=0))
    status: InvoiceStatus = Field(
        sa_column=Column(SAEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)
    )
    payment_method: PaymentMethod | None = Field(
        sa_column=Column(SAEnum(PaymentMethod), nullable=True)
    )
    paid_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=True))
    due_date: date | None = Field(sa_column=Column(Date, default=None))
    notes: str | None = Field(sa_column=Column(Text, default=None))
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

import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.enums import InvoiceStatus, PaymentMethod


class InvoiceCreate(BaseModel):
    appointment_id: uuid.UUID | None = None
    owner_id: uuid.UUID
    pet_id: uuid.UUID
    total_amount: float = 0
    paid_amount: float = 0
    due_date: date | None = None
    notes: str | None = None


class InvoiceUpdate(BaseModel):
    total_amount: float | None = None
    paid_amount: float | None = None
    status: InvoiceStatus | None = None
    payment_method: PaymentMethod | None = None
    paid_at: datetime | None = None
    due_date: date | None = None
    notes: str | None = None


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    appointment_id: uuid.UUID | None
    owner_id: uuid.UUID
    pet_id: uuid.UUID
    total_amount: float
    paid_amount: float
    status: InvoiceStatus
    payment_method: PaymentMethod | None
    paid_at: datetime | None
    due_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvoiceItemCreate(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float
    notes: str | None = None


class InvoiceItemResponse(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    description: str
    quantity: int
    unit_price: float
    total_price: float
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceWithItemsResponse(InvoiceResponse):
    items: list[InvoiceItemResponse]

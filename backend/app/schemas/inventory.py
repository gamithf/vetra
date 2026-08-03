import uuid
from datetime import datetime, date
from pydantic import BaseModel, computed_field
from app.enums import InventoryCategory


class InventoryCreate(BaseModel):
    name: str
    category: InventoryCategory
    description: str | None = None
    unit: str
    quantity: float = 0
    min_quantity: float = 10
    price_per_unit: float | None = None
    supplier: str | None = None
    batch_number: str | None = None
    expiry_date: date | None = None


class InventoryUpdate(BaseModel):
    name: str | None = None
    category: InventoryCategory | None = None
    description: str | None = None
    unit: str | None = None
    quantity: float | None = None
    min_quantity: float | None = None
    price_per_unit: float | None = None
    supplier: str | None = None
    batch_number: str | None = None
    expiry_date: date | None = None
    is_active: bool | None = None


class InventoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: InventoryCategory
    description: str | None
    unit: str
    quantity: float
    min_quantity: float
    price_per_unit: float | None
    supplier: str | None
    batch_number: str | None
    expiry_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.min_quantity

    model_config = {"from_attributes": True}


class LowStockAlert(BaseModel):
    id: uuid.UUID
    name: str
    category: InventoryCategory
    quantity: float
    min_quantity: float

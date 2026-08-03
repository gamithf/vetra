import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.inventory import Inventory
from app.models.user import User
from app.enums import InventoryCategory
from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    LowStockAlert,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/", response_model=list[InventoryResponse])
async def list_inventory(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    category: InventoryCategory | None = None,
    low_stock: bool = False,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Inventory).where(Inventory.is_active == True)
    if category:
        query = query.where(Inventory.category == category)
    if low_stock:
        query = query.where(Inventory.quantity <= Inventory.min_quantity)
    query = query.order_by(Inventory.name.asc()).offset(skip).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()
    return [InventoryResponse.model_validate(i) for i in items]


@router.get("/low-stock", response_model=list[LowStockAlert])
async def get_low_stock_items(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Inventory)
        .where(Inventory.is_active == True)
        .where(Inventory.quantity <= Inventory.min_quantity)
        .order_by(Inventory.quantity.asc())
    )
    items = result.scalars().all()
    return [
        LowStockAlert(
            id=item.id,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            min_quantity=item.min_quantity,
        )
        for item in items
    ]


@router.get("/{item_id}", response_model=InventoryResponse)
async def get_inventory_item(
    item_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Inventory).where(Inventory.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundError("Inventory item not found")
    return InventoryResponse.model_validate(item)


@router.post("/", response_model=InventoryResponse, status_code=201)
async def create_inventory_item(
    body: InventoryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = Inventory(**body.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return InventoryResponse.model_validate(item)


@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: uuid.UUID,
    body: InventoryUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Inventory).where(Inventory.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundError("Inventory item not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return InventoryResponse.model_validate(item)


@router.post("/{item_id}/adjust", response_model=InventoryResponse)
async def adjust_inventory_quantity(
    item_id: uuid.UUID,
    quantity_change: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Inventory).where(Inventory.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundError("Inventory item not found")

    item.quantity += quantity_change
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return InventoryResponse.model_validate(item)

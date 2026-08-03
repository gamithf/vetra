import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import User
from app.models.invoice_item import InvoiceItem
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceItemCreate,
    InvoiceItemResponse,
    InvoiceWithItemsResponse,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    owner_id: uuid.UUID | None = None,
    status: InvoiceStatus | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Invoice)
    if owner_id:
        query = query.where(Invoice.owner_id == owner_id)
    if status:
        query = query.where(Invoice.status == status)
    query = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    invoices = result.scalars().all()
    return [InvoiceResponse.model_validate(i) for i in invoices]


@router.get("/{invoice_id}", response_model=InvoiceWithItemsResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice not found")

    items_result = await session.execute(
        select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
    )
    items = items_result.scalars().all()

    response = InvoiceResponse.model_validate(invoice)
    return InvoiceWithItemsResponse(
        **response.model_dump(),
        items=[InvoiceItemResponse.model_validate(i) for i in items],
    )


@router.post("/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    body: InvoiceCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    invoice = Invoice(**body.model_dump())
    session.add(invoice)
    await session.commit()
    await session.refresh(invoice)
    return InvoiceResponse.model_validate(invoice)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: uuid.UUID,
    body: InvoiceUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(invoice, key, value)

    session.add(invoice)
    await session.commit()
    await session.refresh(invoice)
    return InvoiceResponse.model_validate(invoice)


@router.post("/{invoice_id}/items", response_model=InvoiceItemResponse, status_code=201)
async def add_invoice_item(
    invoice_id: uuid.UUID,
    body: InvoiceItemCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice not found")

    total_price = body.quantity * body.unit_price
    item = InvoiceItem(
        invoice_id=invoice_id,
        description=body.description,
        quantity=body.quantity,
        unit_price=body.unit_price,
        total_price=total_price,
        notes=body.notes,
    )

    invoice.total_amount += total_price
    session.add(item)
    session.add(invoice)
    await session.commit()
    await session.refresh(item)
    return InvoiceItemResponse.model_validate(item)


@router.post("/{invoice_id}/pay", response_model=InvoiceResponse)
async def pay_invoice(
    invoice_id: uuid.UUID,
    body: InvoiceUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice not found")

    if invoice.status == InvoiceStatus.PAID:
        raise BadRequestError("Invoice is already paid")

    from datetime import datetime, timezone

    invoice.status = InvoiceStatus.PAID
    invoice.paid_amount = invoice.total_amount
    invoice.paid_at = datetime.now(timezone.utc)
    if body.payment_method:
        invoice.payment_method = body.payment_method

    session.add(invoice)
    await session.commit()
    await session.refresh(invoice)
    return InvoiceResponse.model_validate(invoice)

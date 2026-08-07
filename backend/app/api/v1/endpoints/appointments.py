import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.realtime import manager
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_item import InvoiceItem
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
)
from app.schemas.invoice import InvoiceWithItemsResponse, InvoiceItemResponse
from pydantic import BaseModel

router = APIRouter(prefix="/appointments", tags=["appointments"])

class EmergencyIntakePayload(BaseModel):
    pet_id: uuid.UUID
    owner_id: uuid.UUID
    vet_id: uuid.UUID | None = None
    reason: str | None = None
    notes: str | None = None


@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    vet_id: uuid.UUID | None = None,
    room_id: uuid.UUID | None = None,
    status: AppointmentStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    query = select(Appointment)
    if vet_id:
        query = query.where(Appointment.vet_id == vet_id)
    if room_id:
        query = query.where(Appointment.room_id == room_id)
    if status:
        query = query.where(Appointment.status == status)
    if date_from:
        query = query.where(Appointment.start_time >= date_from)
    if date_to:
        query = query.where(Appointment.end_time <= date_to)

    query = query.order_by(Appointment.start_time.asc()).offset(skip).limit(limit)
    result = await session.execute(query)
    appointments = result.scalars().all()
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.get("/today", response_model=list[AppointmentResponse])
async def get_today_appointments(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from datetime import timezone, timedelta

    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    query = (
        select(Appointment)
        .where(Appointment.start_time >= start_of_day)
        .where(Appointment.start_time < end_of_day)
        .order_by(Appointment.start_time.asc())
    )
    result = await session.execute(query)
    appointments = result.scalars().all()
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.get("/pending-checkout", response_model=list[AppointmentResponse])
async def pending_checkout(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Completed visits that still need payment: either no invoice yet, or an
    # invoice that is pending / partially paid.
    subquery = select(Invoice.appointment_id).where(
        Invoice.appointment_id.isnot(None),
        Invoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]),
    )
    result = await session.execute(
        select(Appointment)
        .where(Appointment.status == AppointmentStatus.COMPLETED)
        .where(Appointment.id.notin_(subquery))
        .order_by(Appointment.end_time.desc())
    )
    appointments = result.scalars().all()
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")
    return AppointmentResponse.model_validate(appointment)


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    body: AppointmentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if body.start_time >= body.end_time:
        raise BadRequestError("Start time must be before end time")

    appointment = Appointment(**body.model_dump())
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return AppointmentResponse.model_validate(appointment)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: uuid.UUID,
    body: AppointmentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")

    update_data = body.model_dump(exclude_unset=True)
    if "start_time" in update_data and "end_time" in update_data:
        start = update_data.get("start_time", appointment.start_time)
        end = update_data.get("end_time", appointment.end_time)
        if start >= end:
            raise BadRequestError("Start time must be before end time")

    for key, value in update_data.items():
        setattr(appointment, key, value)

    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return AppointmentResponse.model_validate(appointment)


@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")

    await session.delete(appointment)
    await session.commit()
    return {"message": "Appointment deleted"}


@router.post("/{appointment_id}/check-in", response_model=AppointmentResponse)
async def check_in_appointment(
    appointment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")

    appointment.status = AppointmentStatus.CHECKED_IN
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    await manager.broadcast({"type": "appointment.checked_in", "appointment_id": str(appointment.id)})
    return AppointmentResponse.model_validate(appointment)


@router.post("/{appointment_id}/check-out", response_model=AppointmentResponse)
async def check_out_appointment(
    appointment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")

    appointment.status = AppointmentStatus.COMPLETED
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return AppointmentResponse.model_validate(appointment)


@router.post("/emergency", response_model=AppointmentResponse, status_code=201)
async def emergency_intake(
    body: EmergencyIntakePayload,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    appointment = Appointment(
        pet_id=body.pet_id,
        owner_id=body.owner_id,
        vet_id=body.vet_id,
        start_time=now,
        end_time=now,
        status=AppointmentStatus.CHECKED_IN,
        reason=body.reason or "Emergency intake",
        notes=body.notes,
        is_urgent=True,
    )
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return AppointmentResponse.model_validate(appointment)


@router.post("/{appointment_id}/start", response_model=AppointmentResponse)
async def start_appointment(
    appointment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")
    appointment.status = AppointmentStatus.IN_PROGRESS
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    await manager.broadcast({"type": "appointment.started", "appointment_id": str(appointment.id)})
    return AppointmentResponse.model_validate(appointment)


@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")
    appointment.status = AppointmentStatus.COMPLETED
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    await manager.broadcast({"type": "appointment.completed", "appointment_id": str(appointment.id)})
    return AppointmentResponse.model_validate(appointment)


class InvoiceItemPayload(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float


class CreateInvoicePayload(BaseModel):
    items: list[InvoiceItemPayload] | None = None


class FollowupPayload(BaseModel):
    appointment_id: uuid.UUID
    days: int = 7


@router.post("/followup", response_model=AppointmentResponse, status_code=201)
async def schedule_followup_appointment(
    body: FollowupPayload,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a follow-up appointment in `days` days from a completed visit.

    Idempotent: if a future follow-up already exists for the pet it is returned
    instead of creating a duplicate (safe to call on pipeline re-runs).
    """
    src = await session.get(Appointment, body.appointment_id)
    if not src:
        raise NotFoundError("Appointment not found")
    if not src.vet_id:
        raise BadRequestError("Source appointment has no assigned veterinarian")

    existing_result = await session.execute(
        select(Appointment)
        .where(Appointment.pet_id == src.pet_id)
        .where(Appointment.status == AppointmentStatus.SCHEDULED)
        .where(Appointment.reason.ilike("Follow-up%"))
        .where(Appointment.start_time > datetime.now(timezone.utc))
        .order_by(Appointment.start_time.desc())
        .limit(1)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        return AppointmentResponse.model_validate(existing)

    from app.services.scheduling import schedule_followup

    follow = await schedule_followup(
        session,
        src.pet_id,
        src.owner_id,
        src.vet_id,
        body.days,
        reason="Follow-up visit",
        notes="Auto-scheduled follow-up from AI visit summary",
    )
    await session.commit()
    await session.refresh(follow)
    await manager.broadcast({
        "type": "appointment.created",
        "appointment_id": str(follow.id),
        "pet_id": str(follow.pet_id),
    })
    return AppointmentResponse.model_validate(follow)


@router.post("/{appointment_id}/create-invoice", response_model=InvoiceWithItemsResponse)
async def create_invoice_for_appointment(
    appointment_id: uuid.UUID,
    body: CreateInvoicePayload | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise NotFoundError("Appointment not found")

    existing = await session.execute(
        select(Invoice).where(Invoice.appointment_id == appointment_id)
    )
    if existing.scalar_one_or_none():
        raise BadRequestError("Invoice already exists for this appointment")

    from datetime import date
    invoice = Invoice(
        appointment_id=appointment_id,
        owner_id=appointment.owner_id,
        pet_id=appointment.pet_id,
        total_amount=0,
        paid_amount=0,
        status=InvoiceStatus.PENDING,
        due_date=date.today() + timedelta(days=30),
    )
    session.add(invoice)
    await session.flush()

    if body and body.items:
        default_items = [item.model_dump() for item in body.items]
    else:
        default_items = [
            {"description": "Consultation Fee", "quantity": 1, "unit_price": 45.00},
            {"description": "Examination Fee", "quantity": 1, "unit_price": 35.00},
        ]
        if appointment.is_urgent:
            default_items.append({"description": "Emergency Surcharge", "quantity": 1, "unit_price": 50.00})

    total = 0
    items = []
    for item_data in default_items:
        line_total = item_data["quantity"] * item_data["unit_price"]
        total += line_total
        item = InvoiceItem(
            invoice_id=invoice.id,
            **item_data,
            total_price=line_total,
        )
        items.append(item)
        session.add(item)

    invoice.total_amount = total
    session.add(invoice)
    await session.commit()
    await session.refresh(invoice)

    await manager.broadcast({
        "type": "invoice.created",
        "appointment_id": str(invoice.appointment_id),
        "invoice_id": str(invoice.id),
        "total_amount": invoice.total_amount,
    })

    resp = InvoiceWithItemsResponse(
        id=invoice.id,
        appointment_id=invoice.appointment_id,
        owner_id=invoice.owner_id,
        pet_id=invoice.pet_id,
        total_amount=invoice.total_amount,
        paid_amount=invoice.paid_amount,
        status=invoice.status,
        payment_method=invoice.payment_method,
        paid_at=invoice.paid_at,
        due_date=invoice.due_date,
        notes=invoice.notes,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        items=[InvoiceItemResponse.model_validate(i) for i in items],
    )
    return resp

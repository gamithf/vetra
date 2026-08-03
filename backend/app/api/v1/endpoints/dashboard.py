from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from app.database import get_session
from app.api.deps import get_current_user
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.inventory import Inventory
from app.models.clinical_note import ClinicalNote, ClinicalNoteStatus
from pydantic import BaseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class VetDashboardResponse(BaseModel):
    today_appointments: int
    pending_notes: int
    checked_in_patients: int
    urgent_cases: int


class StaffDashboardResponse(BaseModel):
    today_appointments: int
    low_stock_items: int
    pending_invoices: int
    checked_in_patients: int


@router.get("/vet", response_model=VetDashboardResponse)
async def vet_dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    today_count = await session.execute(
        select(func.count(Appointment.id))
        .where(Appointment.start_time >= start_of_day)
        .where(Appointment.start_time < end_of_day)
        .where(Appointment.vet_id == current_user.id)
    )

    pending_notes = await session.execute(
        select(func.count(ClinicalNote.id))
        .where(ClinicalNote.vet_id == current_user.id)
        .where(ClinicalNote.status.in_([ClinicalNoteStatus.DRAFT, ClinicalNoteStatus.PENDING]))
    )

    checked_in = await session.execute(
        select(func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.CHECKED_IN
        )
    )

    urgent = await session.execute(
        select(func.count(Appointment.id))
        .where(Appointment.start_time >= start_of_day)
        .where(Appointment.start_time < end_of_day)
        .where(Appointment.is_urgent == True)
    )

    return VetDashboardResponse(
        today_appointments=today_count.scalar() or 0,
        pending_notes=pending_notes.scalar() or 0,
        checked_in_patients=checked_in.scalar() or 0,
        urgent_cases=urgent.scalar() or 0,
    )


@router.get("/staff", response_model=StaffDashboardResponse)
async def staff_dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    today_count = await session.execute(
        select(func.count(Appointment.id))
        .where(Appointment.start_time >= start_of_day)
        .where(Appointment.start_time < end_of_day)
    )

    low_stock = await session.execute(
        select(func.count(Inventory.id))
        .where(Inventory.is_active == True)
        .where(Inventory.quantity <= Inventory.min_quantity)
    )

    from app.models.invoice import Invoice, InvoiceStatus
    pending_inv = await session.execute(
        select(func.count(Invoice.id)).where(
            Invoice.status == InvoiceStatus.PENDING
        )
    )

    checked_in = await session.execute(
        select(func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.CHECKED_IN
        )
    )

    return StaffDashboardResponse(
        today_appointments=today_count.scalar() or 0,
        low_stock_items=low_stock.scalar() or 0,
        pending_invoices=pending_inv.scalar() or 0,
        checked_in_patients=checked_in.scalar() or 0,
    )

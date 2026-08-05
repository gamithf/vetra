"""Notification endpoints — currently WhatsApp owner notifications.

`POST /notifications/visit-summary` is called by the agent pipeline right after a
visit is finalized. It builds the owner WhatsApp message (visit id, reason,
diagnosis/treatment, bill total + magic link) and sends it via the Meta Cloud API.
"""

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.models.pet import Pet
from app.models.owner import Owner
from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.services.whatsapp import send_visit_summary

router = APIRouter(prefix="/notifications", tags=["notifications"])


class VisitSummaryRequest(BaseModel):
    appointment_id: uuid.UUID
    diagnosis: str | None = None
    treatment: str | None = None


@router.post("/visit-summary")
async def notify_visit_summary(
    body: VisitSummaryRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    appointment = await session.get(Appointment, body.appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")

    pet = await session.get(Pet, appointment.pet_id)
    owner = await session.get(Owner, appointment.owner_id) if appointment.owner_id else None

    inv_result = await session.execute(
        select(Invoice).where(Invoice.appointment_id == appointment.id)
    )
    invoice = inv_result.scalar_one_or_none()

    items = []
    if invoice:
        item_result = await session.execute(
            select(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id)
        )
        items = item_result.scalars().all()

    result = await send_visit_summary(
        appointment,
        pet,
        owner,
        invoice,
        items,
        diagnosis=body.diagnosis,
        treatment=body.treatment,
    )
    return result

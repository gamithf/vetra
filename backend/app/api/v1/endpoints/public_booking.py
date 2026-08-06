"""Public, token-authenticated booking endpoints for the magic-link portal.

The magic-link token identifies one pet; it also grants access to the rest of
that owner's pets and appointments (the token itself is the credential).

Endpoints:
  GET    /public/portal/{token}                owner + pets + all appointments
  GET    /public/slots/{token}/{vet_id}/{date} free 30-min slots for a vet/date
  POST   /public/appointments                  create a booking
  PATCH  /public/appointments/{appointment_id} reschedule a future booking
"""

import uuid
from datetime import datetime, date, timezone, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.core.exceptions import NotFoundError, BadRequestError, UnauthorizedError
from app.enums import AppointmentStatus
from app.models.appointment import Appointment
from app.models.owner import Owner
from app.models.pet import Pet
from app.models.user import User
from app.realtime import manager
from app.services.magic_link import verify_pet_token
from app.services.scheduling import (
    SLOT_MINUTES,
    free_slots,
    resolve_primary_vet,
)

router = APIRouter(prefix="/public", tags=["public-booking"])


async def _owner_from_token(session: AsyncSession, token: str) -> Owner:
    pet_id = verify_pet_token(token)
    if pet_id is None:
        raise UnauthorizedError("Invalid or expired link")
    pet = await session.get(Pet, pet_id)
    if not pet or not pet.owner_id:
        raise NotFoundError("Pet not found")
    owner = await session.get(Owner, pet.owner_id)
    if not owner:
        raise NotFoundError("Owner not found")
    return owner


async def _require_owner_pet(session: AsyncSession, owner: Owner, pet_id: uuid.UUID) -> Pet:
    pet = await session.get(Pet, pet_id)
    if not pet or pet.owner_id != owner.id:
        raise BadRequestError("Pet does not belong to this owner")
    return pet


async def _resolve_vet(session: AsyncSession, vet_id: uuid.UUID | None, pet_id: uuid.UUID) -> uuid.UUID:
    if vet_id is None:
        return await resolve_primary_vet(session, pet_id)
    vet = await session.get(User, vet_id)
    if not vet or vet.role.value != "vet":
        raise BadRequestError("Veterinarian not found")
    return vet_id


def _validate_free_slot(session, free: list[datetime], start_time: datetime) -> datetime:
    """Return start_time if it is exactly one of the free slots, else 400."""
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if any(s == start_time for s in free):
        return start_time
    raise BadRequestError("Selected time slot is no longer available")


def _appt_to_dict(appt: Appointment, pet_name: str, vet_name: str | None) -> dict:
    return {
        "id": str(appt.id),
        "pet_id": str(appt.pet_id),
        "pet_name": pet_name,
        "vet_id": str(appt.vet_id) if appt.vet_id else None,
        "vet_name": vet_name,
        "reason": appt.reason,
        "start_time": appt.start_time.isoformat(),
        "end_time": appt.end_time.isoformat(),
        "status": appt.status.value,
    }


# ── Portal ──────────────────────────────────────────────────

@router.get("/portal/{token}")
async def public_portal(token: str, session: AsyncSession = Depends(get_session)):
    owner = await _owner_from_token(session, token)

    pets_result = await session.execute(
        select(Pet).where(Pet.owner_id == owner.id).order_by(Pet.name.asc())
    )
    pets = pets_result.scalars().all()

    pet_list = []
    for p in pets:
        vet_id = None
        try:
            vet_id = await resolve_primary_vet(session, p.id)
        except NotFoundError:
            vet_id = None
        vet_name = None
        if vet_id:
            vet = await session.get(User, vet_id)
            vet_name = vet.full_name if vet else None
        pet_list.append({
            "id": str(p.id),
            "name": p.name,
            "species": p.species.value,
            "breed": p.breed,
            "photo_url": p.photo_url,
            "primary_vet_id": str(vet_id) if vet_id else None,
            "primary_vet_name": vet_name,
        })

    appts_result = await session.execute(
        select(Appointment)
        .where(Appointment.owner_id == owner.id)
        .order_by(Appointment.start_time.desc())
        .limit(200)
    )
    appts = appts_result.scalars().all()

    pet_names = {p.id: p.name for p in pets}
    vet_names: dict[uuid.UUID, str] = {}
    for a in appts:
        if a.vet_id and a.vet_id not in vet_names:
            vet = await session.get(User, a.vet_id)
            vet_names[a.vet_id] = vet.full_name if vet else "Vet"

    return {
        "owner": {"first_name": owner.first_name, "last_name": owner.last_name},
        "pets": pet_list,
        "appointments": [
            _appt_to_dict(
                a,
                pet_names.get(a.pet_id, "Pet"),
                vet_names.get(a.vet_id) if a.vet_id else None,
            )
            for a in appts
        ],
    }


# ── Availability ────────────────────────────────────────────

@router.get("/slots/{token}/{vet_id}/{slot_date}")
async def public_slots(
    token: str,
    vet_id: uuid.UUID,
    slot_date: date,
    session: AsyncSession = Depends(get_session),
):
    await _owner_from_token(session, token)
    free = await free_slots(session, vet_id, slot_date)
    return {
        "date": slot_date.isoformat(),
        "slots": [s.isoformat() for s in free],
    }


# ── Booking ─────────────────────────────────────────────────

class PublicBookingCreate(BaseModel):
    pet_id: uuid.UUID
    vet_id: uuid.UUID | None = None
    start_time: datetime
    reason: str | None = None


@router.post("/appointments", status_code=201)
async def public_create_booking(
    token: str,
    body: PublicBookingCreate,
    session: AsyncSession = Depends(get_session),
):
    owner = await _owner_from_token(session, token)
    pet = await _require_owner_pet(session, owner, body.pet_id)
    vet_id = await _resolve_vet(session, body.vet_id, pet.id)

    if body.start_time.date() < date.today():
        raise BadRequestError("Cannot book an appointment in the past")
    if body.start_time <= datetime.now(timezone.utc):
        raise BadRequestError("Cannot book a slot that has already started")

    free = await free_slots(session, vet_id, body.start_time.date())
    start = _validate_free_slot(session, free, body.start_time)

    appointment = Appointment(
        pet_id=pet.id,
        owner_id=owner.id,
        vet_id=vet_id,
        start_time=start,
        end_time=start + timedelta(minutes=SLOT_MINUTES),
        status=AppointmentStatus.SCHEDULED,
        reason=body.reason or "Online booking",
        notes="Booked via the owner magic link",
    )
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    vet = await session.get(User, vet_id)
    await manager.broadcast({
        "type": "appointment.created",
        "appointment_id": str(appointment.id),
        "pet_id": str(pet.id),
    })

    return _appt_to_dict(appointment, pet.name, vet.full_name if vet else None)


class PublicBookingUpdate(BaseModel):
    vet_id: uuid.UUID | None = None
    start_time: datetime
    reason: str | None = None


@router.patch("/appointments/{appointment_id}")
async def public_update_booking(
    token: str,
    appointment_id: uuid.UUID,
    body: PublicBookingUpdate,
    session: AsyncSession = Depends(get_session),
):
    owner = await _owner_from_token(session, token)
    appointment = await session.get(Appointment, appointment_id)
    if not appointment or appointment.owner_id != owner.id:
        raise NotFoundError("Appointment not found")
    if appointment.status != AppointmentStatus.SCHEDULED:
        raise BadRequestError("Only scheduled appointments can be rescheduled")
    if appointment.start_time <= datetime.now(timezone.utc):
        raise BadRequestError("Only future appointments can be rescheduled")

    vet_id = body.vet_id or appointment.vet_id
    if vet_id is None:
        raise BadRequestError("Appointment has no assigned veterinarian")

    if body.start_time.date() < date.today():
        raise BadRequestError("Cannot book an appointment in the past")

    free = await free_slots(
        session, vet_id, body.start_time.date(), exclude_appointment_id=appointment.id
    )
    start = _validate_free_slot(session, free, body.start_time)

    appointment.start_time = start
    appointment.end_time = start + timedelta(minutes=SLOT_MINUTES)
    if vet_id != appointment.vet_id:
        appointment.vet_id = vet_id
    if body.reason is not None:
        appointment.reason = body.reason
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    pet = await session.get(Pet, appointment.pet_id)
    vet = await session.get(User, appointment.vet_id)
    await manager.broadcast({
        "type": "appointment.updated",
        "appointment_id": str(appointment.id),
    })

    return _appt_to_dict(
        appointment,
        pet.name if pet else "Pet",
        vet.full_name if vet else None,
    )

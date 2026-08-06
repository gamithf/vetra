"""Clinic scheduling — clinic hours, free-slot computation and follow-up booking.

Hours are treated as UTC wall-clock (consistent with how the seed data and the
rest of the app store appointment times) so booked slots never collide with
existing appointments.

Clinic hours:
  - Weekdays (Mon–Fri): 09:00–17:00
  - Weekends (Sat–Sun): 09:00–12:00
"""

import uuid
from datetime import datetime, date, time, timezone, timedelta

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.exceptions import BadRequestError, NotFoundError
from app.enums import UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User

SLOT_MINUTES = 30

ACTIVE_STATUSES = (
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.CHECKED_IN,
    AppointmentStatus.IN_PROGRESS,
)


def clinic_open_range(d: date) -> tuple[time, time]:
    """Return (open_time, close_time) for a calendar date (weekends shorter)."""
    if d.weekday() >= 5:
        return time(9, 0), time(12, 0)
    return time(9, 0), time(17, 0)


def iter_slot_starts(d: date) -> list[datetime]:
    """All candidate 30-minute slot start datetimes for a date (within clinic hours)."""
    open_at, close_at = clinic_open_range(d)
    start = datetime.combine(d, open_at, tzinfo=timezone.utc)
    end = datetime.combine(d, close_at, tzinfo=timezone.utc)
    slots: list[datetime] = []
    cur = start
    while cur + timedelta(minutes=SLOT_MINUTES) <= end:
        slots.append(cur)
        cur += timedelta(minutes=SLOT_MINUTES)
    return slots


def _overlaps(existing_start: datetime, existing_end: datetime, slot_start: datetime) -> bool:
    slot_end = slot_start + timedelta(minutes=SLOT_MINUTES)
    return slot_start < existing_end and existing_start < slot_end


async def free_slots(
    session: AsyncSession,
    vet_id: uuid.UUID | None,
    d: date,
    exclude_appointment_id: uuid.UUID | None = None,
) -> list[datetime]:
    """Free slot start datetimes for a vet on a date (future slots only)."""
    all_slots = iter_slot_starts(d)
    if not all_slots:
        return []

    now = datetime.now(timezone.utc)
    day_start = datetime.combine(d, time(0, 0), tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    query = (
        select(Appointment)
        .where(Appointment.start_time >= day_start)
        .where(Appointment.start_time < day_end)
        .where(Appointment.status.in_(ACTIVE_STATUSES))
    )
    if vet_id is not None:
        query = query.where(Appointment.vet_id == vet_id)
    existing = (await session.execute(query)).scalars().all()

    free: list[datetime] = []
    for s in all_slots:
        if s <= now:
            continue
        conflict = any(
            _overlaps(e.start_time, e.end_time, s)
            for e in existing
            if e.id != exclude_appointment_id
        )
        if not conflict:
            free.append(s)
    return free


async def resolve_primary_vet(session: AsyncSession, pet_id: uuid.UUID) -> uuid.UUID:
    """The vet who most recently treated the pet, falling back to the first active vet."""
    result = await session.execute(
        select(Appointment)
        .where(Appointment.pet_id == pet_id)
        .where(Appointment.vet_id.isnot(None))
        .order_by(Appointment.start_time.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if latest and latest.vet_id:
        return latest.vet_id

    result = await session.execute(
        select(User)
        .where(User.role == UserRole.VET)
        .where(User.is_active.is_(True))
        .order_by(User.created_at.asc())
        .limit(1)
    )
    fallback = result.scalar_one_or_none()
    if not fallback:
        raise NotFoundError("No veterinarian is available for scheduling")
    return fallback.id


async def schedule_followup(
    session: AsyncSession,
    pet_id: uuid.UUID,
    owner_id: uuid.UUID,
    vet_id: uuid.UUID,
    in_days: int,
    reason: str = "Follow-up visit",
    notes: str | None = None,
) -> Appointment:
    """Create a follow-up appointment in_days from now at the first free slot.

    Searches forward up to 14 days from the target date if that day is fully
    booked, so it never fails on a busy day.
    """
    if in_days < 0:
        raise BadRequestError("Follow-up days cannot be negative")

    target = (datetime.now(timezone.utc) + timedelta(days=in_days)).date()
    for offset in range(0, 15):
        d = target + timedelta(days=offset)
        slots = await free_slots(session, vet_id, d)
        if slots:
            start = slots[0]
            appointment = Appointment(
                pet_id=pet_id,
                owner_id=owner_id,
                vet_id=vet_id,
                start_time=start,
                end_time=start + timedelta(minutes=SLOT_MINUTES),
                status=AppointmentStatus.SCHEDULED,
                reason=reason,
                notes=notes,
            )
            session.add(appointment)
            await session.flush()
            return appointment

    raise BadRequestError("No free slots found within the next 14 days for a follow-up")

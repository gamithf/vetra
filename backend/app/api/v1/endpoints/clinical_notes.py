import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.clinical_note import ClinicalNote, ClinicalNoteStatus
from app.models.appointment import Appointment
from app.models.user import User
from app.schemas.clinical_note import (
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
    ClinicalNoteResponse,
)
from pydantic import BaseModel

router = APIRouter(prefix="/clinical-notes", tags=["clinical-notes"])


class SubmitNoteResponse(BaseModel):
    note: ClinicalNoteResponse
    message: str


@router.get("/", response_model=list[ClinicalNoteResponse])
async def list_clinical_notes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    pet_id: uuid.UUID | None = None,
    status: ClinicalNoteStatus | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(ClinicalNote)
    if pet_id:
        query = query.where(ClinicalNote.pet_id == pet_id)
    if status:
        query = query.where(ClinicalNote.status == status)
    query = query.order_by(ClinicalNote.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    notes = result.scalars().all()
    return [ClinicalNoteResponse.model_validate(n) for n in notes]


@router.get("/{note_id}", response_model=ClinicalNoteResponse)
async def get_clinical_note(
    note_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(ClinicalNote).where(ClinicalNote.id == note_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise NotFoundError("Clinical note not found")
    return ClinicalNoteResponse.model_validate(note)


@router.post("/", response_model=SubmitNoteResponse, status_code=201)
async def create_clinical_note(
    body: ClinicalNoteCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not body.appointment_id:
        raise BadRequestError("appointment_id is required")

    appointment = await session.get(Appointment, body.appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")

    note = ClinicalNote(
        pet_id=body.pet_id,
        appointment_id=body.appointment_id,
        raw_transcript=body.raw_transcript,
        vet_id=current_user.id,
        structured_note=body.structured_note,
        ai_model_version=body.ai_model_version or "manual-entry",
        status=body.status or ClinicalNoteStatus.COMPLETED,
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)

    return SubmitNoteResponse(
        note=ClinicalNoteResponse.model_validate(note),
        message="Clinical note saved.",
    )


@router.put("/{note_id}", response_model=ClinicalNoteResponse)
async def update_clinical_note(
    note_id: uuid.UUID,
    body: ClinicalNoteUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(ClinicalNote).where(ClinicalNote.id == note_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise NotFoundError("Clinical note not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)

    session.add(note)
    await session.commit()
    await session.refresh(note)
    return ClinicalNoteResponse.model_validate(note)

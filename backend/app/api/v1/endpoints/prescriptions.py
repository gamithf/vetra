import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.prescription import Prescription
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
)

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.get("/", response_model=list[PrescriptionResponse])
async def list_prescriptions(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    pet_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Prescription)
    if pet_id:
        query = query.where(Prescription.pet_id == pet_id)
    query = query.order_by(Prescription.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    prescriptions = result.scalars().all()
    return [PrescriptionResponse.model_validate(p) for p in prescriptions]


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Prescription).where(Prescription.id == prescription_id)
    )
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise NotFoundError("Prescription not found")
    return PrescriptionResponse.model_validate(prescription)


@router.post("/", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(
    body: PrescriptionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    prescription = Prescription(**body.model_dump())
    session.add(prescription)
    await session.commit()
    await session.refresh(prescription)
    return PrescriptionResponse.model_validate(prescription)


@router.put("/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription(
    prescription_id: uuid.UUID,
    body: PrescriptionUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Prescription).where(Prescription.id == prescription_id)
    )
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise NotFoundError("Prescription not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prescription, key, value)

    session.add(prescription)
    await session.commit()
    await session.refresh(prescription)
    return PrescriptionResponse.model_validate(prescription)

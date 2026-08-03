import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.medical_record import MedicalRecord
from app.models.user import User
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
)

router = APIRouter(prefix="/medical-records", tags=["medical-records"])


@router.get("/", response_model=list[MedicalRecordResponse])
async def list_medical_records(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    pet_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(MedicalRecord)
    if pet_id:
        query = query.where(MedicalRecord.pet_id == pet_id)
    query = query.order_by(MedicalRecord.recorded_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    records = result.scalars().all()
    return [MedicalRecordResponse.model_validate(r) for r in records]


@router.get("/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(MedicalRecord).where(MedicalRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundError("Medical record not found")
    return MedicalRecordResponse.model_validate(record)


@router.post("/", response_model=MedicalRecordResponse, status_code=201)
async def create_medical_record(
    body: MedicalRecordCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    record = MedicalRecord(**body.model_dump())
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return MedicalRecordResponse.model_validate(record)


@router.put("/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: uuid.UUID,
    body: MedicalRecordUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(MedicalRecord).where(MedicalRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundError("Medical record not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    session.add(record)
    await session.commit()
    await session.refresh(record)
    return MedicalRecordResponse.model_validate(record)

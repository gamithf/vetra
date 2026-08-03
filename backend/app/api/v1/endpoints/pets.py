import uuid
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.pet import Pet
from app.models.user import User
from app.models.owner import Owner
from app.models.medical_record import MedicalRecord
from app.models.vaccination import Vaccination
from app.models.lab_result import LabResult
from app.models.weight_record import WeightRecord
from app.schemas.pet import PetCreate, PetUpdate, PetResponse
from app.schemas.medical_record import MedicalRecordResponse
from app.schemas.vaccination import VaccinationResponse
from app.schemas.lab_result import LabResultResponse
from app.schemas.weight_record import WeightRecordResponse

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("/", response_model=list[PetResponse])
async def list_pets(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    owner_id: uuid.UUID | None = None,
    species: str | None = None,
    search: str | None = None,
):
    query = select(Pet)
    if owner_id:
        query = query.where(Pet.owner_id == owner_id)
    if species:
        query = query.where(Pet.species == species)
    if search:
        query = query.where(
            Pet.name.ilike(f"%{search}%")
            | Pet.microchip_id.ilike(f"%{search}%")
        )
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    pets = result.scalars().all()
    return [PetResponse.model_validate(p) for p in pets]


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise NotFoundError("Pet not found")
    return PetResponse.model_validate(pet)


@router.post("/", response_model=PetResponse, status_code=201)
async def create_pet(
    body: PetCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    owner = await session.execute(select(Owner).where(Owner.id == body.owner_id))
    if not owner.scalar_one_or_none():
        raise NotFoundError("Owner not found")

    pet = Pet(**body.model_dump())
    session.add(pet)
    await session.commit()
    await session.refresh(pet)
    return PetResponse.model_validate(pet)


@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: uuid.UUID,
    body: PetUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise NotFoundError("Pet not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pet, key, value)

    session.add(pet)
    await session.commit()
    await session.refresh(pet)
    return PetResponse.model_validate(pet)


@router.delete("/{pet_id}", response_model=dict)
async def delete_pet(
    pet_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise NotFoundError("Pet not found")

    pet.is_active = False
    session.add(pet)
    await session.commit()
    return {"message": "Pet deactivated"}


@router.get("/{pet_id}/medical-records", response_model=list[MedicalRecordResponse])
async def get_pet_medical_records(
    pet_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(MedicalRecord)
        .where(MedicalRecord.pet_id == pet_id)
        .order_by(MedicalRecord.recorded_at.desc())
    )
    records = result.scalars().all()
    return [MedicalRecordResponse.model_validate(r) for r in records]


@router.get("/{pet_id}/vaccinations", response_model=list[VaccinationResponse])
async def get_pet_vaccinations(
    pet_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Vaccination)
        .where(Vaccination.pet_id == pet_id)
        .order_by(Vaccination.administered_date.desc())
    )
    vaccinations = result.scalars().all()
    return [VaccinationResponse.model_validate(v) for v in vaccinations]


@router.get("/{pet_id}/lab-results", response_model=list[LabResultResponse])
async def get_pet_lab_results(
    pet_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(LabResult)
        .where(LabResult.pet_id == pet_id)
        .order_by(LabResult.result_date.desc())
    )
    lab_results = result.scalars().all()
    return [LabResultResponse.model_validate(l) for l in lab_results]


@router.get("/{pet_id}/weight-history", response_model=list[WeightRecordResponse])
async def get_pet_weight_history(
    pet_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(WeightRecord)
        .where(WeightRecord.pet_id == pet_id)
        .order_by(WeightRecord.recorded_at.desc())
    )
    records = result.scalars().all()
    return [WeightRecordResponse.model_validate(r) for r in records]

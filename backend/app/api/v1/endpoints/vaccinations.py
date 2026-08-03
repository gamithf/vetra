import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.vaccination import Vaccination
from app.models.user import User
from app.schemas.vaccination import (
    VaccinationCreate,
    VaccinationUpdate,
    VaccinationResponse,
)

router = APIRouter(prefix="/vaccinations", tags=["vaccinations"])


@router.get("/", response_model=list[VaccinationResponse])
async def list_vaccinations(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    pet_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Vaccination)
    if pet_id:
        query = query.where(Vaccination.pet_id == pet_id)
    query = query.order_by(Vaccination.administered_date.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    vaccinations = result.scalars().all()
    return [VaccinationResponse.model_validate(v) for v in vaccinations]


@router.get("/{vaccination_id}", response_model=VaccinationResponse)
async def get_vaccination(
    vaccination_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Vaccination).where(Vaccination.id == vaccination_id)
    )
    vaccination = result.scalar_one_or_none()
    if not vaccination:
        raise NotFoundError("Vaccination not found")
    return VaccinationResponse.model_validate(vaccination)


@router.post("/", response_model=VaccinationResponse, status_code=201)
async def create_vaccination(
    body: VaccinationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vaccination = Vaccination(**body.model_dump())
    session.add(vaccination)
    await session.commit()
    await session.refresh(vaccination)
    return VaccinationResponse.model_validate(vaccination)


@router.put("/{vaccination_id}", response_model=VaccinationResponse)
async def update_vaccination(
    vaccination_id: uuid.UUID,
    body: VaccinationUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Vaccination).where(Vaccination.id == vaccination_id)
    )
    vaccination = result.scalar_one_or_none()
    if not vaccination:
        raise NotFoundError("Vaccination not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vaccination, key, value)

    session.add(vaccination)
    await session.commit()
    await session.refresh(vaccination)
    return VaccinationResponse.model_validate(vaccination)

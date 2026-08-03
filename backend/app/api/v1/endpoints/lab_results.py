import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.lab_result import LabResult
from app.models.user import User
from app.schemas.lab_result import LabResultCreate, LabResultUpdate, LabResultResponse

router = APIRouter(prefix="/lab-results", tags=["lab-results"])


@router.get("/", response_model=list[LabResultResponse])
async def list_lab_results(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    pet_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(LabResult)
    if pet_id:
        query = query.where(LabResult.pet_id == pet_id)
    query = query.order_by(LabResult.result_date.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    lab_results = result.scalars().all()
    return [LabResultResponse.model_validate(l) for l in lab_results]


@router.get("/{lab_result_id}", response_model=LabResultResponse)
async def get_lab_result(
    lab_result_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(LabResult).where(LabResult.id == lab_result_id)
    )
    lab_result = result.scalar_one_or_none()
    if not lab_result:
        raise NotFoundError("Lab result not found")
    return LabResultResponse.model_validate(lab_result)


@router.post("/", response_model=LabResultResponse, status_code=201)
async def create_lab_result(
    body: LabResultCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    lab_result = LabResult(**body.model_dump())
    session.add(lab_result)
    await session.commit()
    await session.refresh(lab_result)
    return LabResultResponse.model_validate(lab_result)


@router.put("/{lab_result_id}", response_model=LabResultResponse)
async def update_lab_result(
    lab_result_id: uuid.UUID,
    body: LabResultUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(LabResult).where(LabResult.id == lab_result_id)
    )
    lab_result = result.scalar_one_or_none()
    if not lab_result:
        raise NotFoundError("Lab result not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lab_result, key, value)

    session.add(lab_result)
    await session.commit()
    await session.refresh(lab_result)
    return LabResultResponse.model_validate(lab_result)

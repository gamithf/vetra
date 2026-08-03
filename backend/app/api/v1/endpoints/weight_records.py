import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.models.weight_record import WeightRecord
from app.models.user import User
from app.schemas.weight_record import WeightRecordCreate, WeightRecordResponse

router = APIRouter(prefix="/weight-records", tags=["weight-records"])


@router.post("/", response_model=WeightRecordResponse, status_code=201)
async def create_weight_record(
    body: WeightRecordCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    record = WeightRecord(
        pet_id=body.pet_id,
        weight_kg=body.weight_kg,
        recorded_by=current_user.id,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return WeightRecordResponse.model_validate(record)

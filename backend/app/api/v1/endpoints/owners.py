import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.models.owner import Owner
from app.models.user import User
from app.schemas.owner import OwnerCreate, OwnerUpdate, OwnerResponse

router = APIRouter(prefix="/owners", tags=["owners"])


@router.get("/", response_model=list[OwnerResponse])
async def list_owners(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    query = select(Owner)
    if search:
        query = query.where(
            Owner.first_name.ilike(f"%{search}%")
            | Owner.last_name.ilike(f"%{search}%")
            | Owner.email.ilike(f"%{search}%")
            | Owner.phone.ilike(f"%{search}%")
        )
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    owners = result.scalars().all()
    return [OwnerResponse.model_validate(o) for o in owners]


@router.get("/{owner_id}", response_model=OwnerResponse)
async def get_owner(
    owner_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Owner).where(Owner.id == owner_id))
    owner = result.scalar_one_or_none()
    if not owner:
        raise NotFoundError("Owner not found")
    return OwnerResponse.model_validate(owner)


@router.post("/", response_model=OwnerResponse, status_code=201)
async def create_owner(
    body: OwnerCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    owner = Owner(**body.model_dump())
    session.add(owner)
    await session.commit()
    await session.refresh(owner)
    return OwnerResponse.model_validate(owner)


@router.put("/{owner_id}", response_model=OwnerResponse)
async def update_owner(
    owner_id: uuid.UUID,
    body: OwnerUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Owner).where(Owner.id == owner_id))
    owner = result.scalar_one_or_none()
    if not owner:
        raise NotFoundError("Owner not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(owner, key, value)

    session.add(owner)
    await session.commit()
    await session.refresh(owner)
    return OwnerResponse.model_validate(owner)


@router.delete("/{owner_id}", response_model=dict)
async def delete_owner(
    owner_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Owner).where(Owner.id == owner_id))
    owner = result.scalar_one_or_none()
    if not owner:
        raise NotFoundError("Owner not found")

    owner.is_active = False
    session.add(owner)
    await session.commit()
    return {"message": "Owner deactivated"}

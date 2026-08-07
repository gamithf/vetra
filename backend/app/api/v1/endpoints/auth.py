from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database import get_session
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import UnauthorizedError, ConflictError
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    body: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    existing = await session.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise ConflictError("Email already registered")

    user = User(
        email=body.email,
        password_hash=get_password_hash(body.password),
        full_name=body.full_name,
        role=body.role,
        phone=body.phone,
        photo_url=body.photo_url,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

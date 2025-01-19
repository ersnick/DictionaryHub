from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user
from db.database import get_db
from schemas.users import UserCreate, UserResponse
from services.users import UserService


router = APIRouter(prefix="/user", tags=["User"])
user_service = UserService()


@router.post("/", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Эндпоинт для регистрации нового пользователя"""
    created_user = await user_service.register_user(db, user_data)
    return created_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
        fullname: str | None,
        bio: str | None = None,
        photo: UploadFile = File(None),  # Фото пользователя (опционально)
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    """Редактирование профиля с загрузкой фото"""
    user = await user_service.update_profile(
        db=db,
        current_user=current_user,
        fullname=fullname,
        bio=bio,
        photo=photo
    )
    return user

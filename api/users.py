from pathlib import Path
from fastapi import Depends, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.auth import get_current_user
from db.database import get_db
from schemas.users import UserCreate, UserResponse, UserPublicData
from services.users import UserService


router = APIRouter(prefix="/user", tags=["User"])
user_service = UserService()


@router.post("/", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Эндпоинт для регистрации нового пользователя"""
    created_user = await user_service.register_user(db, user_data)
    return created_user


@router.get("/dictionaries")
async def get_owners_dictionaries(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Получить все словари владельца"""
    try:
        dictionaries = await user_service.get_all_owners_dictionaries(db, current_user['sub'])
        return dictionaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=UserResponse)
async def update_profile(
        fullname: str | None = None,
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


@router.get("/profile", response_model=UserResponse)
async def get_user_data(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Получить всю информацию о своем профиле"""
    return await user_service.get_user_by_username(db, current_user['sub'])


@router.get("/photo/{username}")
async def get_user_photo(username: str, db: AsyncSession = Depends(get_db)):
    """Получить фото пользователя"""
    photo_path = await user_service.get_user_photo(db, username)

    if photo_path:
        # Проверка существования файла
        file_path = Path(photo_path)
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found on server.")

        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=file_path.name
        )
    else:
        raise HTTPException(status_code=404, detail="User has not photo.")


@router.get("/profile/{username}", response_model=UserPublicData)
async def get_public_user_data(username: str, db: AsyncSession = Depends(get_db)):
    """Просмотреть публичные данные пользователя"""
    user = UserPublicData
    user.fullname, user.username, user.bio = await user_service.get_public_user_data(db, username)
    return user

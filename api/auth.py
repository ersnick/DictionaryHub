from datetime import timedelta
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core.auth import create_access_token, create_refresh_token, verify_password
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.users import UserCreate, UserResponse
from services.users import UserService
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])
user_service = UserService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.post("/token/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Создать новые токены
        access_token = create_access_token({"sub": user_id}, expires_delta=timedelta(minutes=999))
        new_refresh_token = create_refresh_token({"sub": user_id})
        return {"access_token": access_token, "refresh_token": new_refresh_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/token", response_model=dict)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """Эндпоинт для авторизации пользователя"""
    user = await user_service.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Создать access- и refresh-токены
    access_token = create_access_token({"sub": user.username}, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token({"sub": user.username})

    return {"access_token": access_token, "refresh_token": refresh_token}

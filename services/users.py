from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException

from repositories.dictionaries import DictionaryRepository
from repositories.users import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserCreate, UserResponse


class UserService:
    def __init__(self):
        self.userRepository = UserRepository()
        self.dictionaryRepository = DictionaryRepository()
        self.UPLOAD_DIR = Path("uploads/users_photo")
        self.UPLOAD_DIR.mkdir(exist_ok=True)

    async def register_user(self, db: AsyncSession, user_data: UserCreate):
        """Регистрация нового пользователя"""
        return await self.userRepository.create_user(db, user_data)

    async def update_profile(
            self,
            db: AsyncSession,
            current_user: dict,
            fullname: str | None = None,
            bio: str | None = None,
            photo: UploadFile | None = None,
    ) -> UserResponse:
        """Обновляет информацию в профиле с сохранением фото пользователя"""

        # Обработка фото
        if photo:
            if not photo.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Uploaded file must be an image")

            # Генерируем уникальное имя для файла
            file_extension = photo.filename.split(".")[-1]
            file_name = f"{current_user['sub']}_{int(datetime.utcnow().timestamp())}.{file_extension}"
            file_path = self.UPLOAD_DIR / file_name

            # Сохраняем файл
            with open(file_path, "wb") as f:
                content = await photo.read()
                f.write(content)

            return await self.userRepository.update_user_data(
                db, current_user['sub'], fullname, bio, str(file_path)
            )
        else:
            return await self.userRepository.update_user_data(db, current_user['sub'], fullname, bio, None)

    async def get_user_by_username(self, db: AsyncSession, username):
        """Возвращает все данные о пользователе"""
        return await self.userRepository.get_user_by_username(db, username)

    async def get_public_user_data(self, db: AsyncSession, username):
        """Возвращает публичные данные пользователя"""
        return await self.userRepository.get_public_user_data(db, username)

    async def get_user_photo(self, db: AsyncSession, username):
        """Возвращает фото пользователя"""
        return await self.userRepository.get_user_photo(db, username)

    async def get_all_owners_dictionaries(self, db: AsyncSession, username):
        try:
            user = await self.userRepository.get_user_by_username(db, username)
            return await self.dictionaryRepository.get_all_owners_dictionaries(db, user.id)
        except Exception as e:
            raise Exception(f"Error retrieving dictionaries: {e}")

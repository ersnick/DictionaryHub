import shutil
import logging

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from repositories.dictionaries import DictionaryRepository
from repositories.users import UserRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DictionaryService:
    def __init__(self):
        self.dictionaryRepository = DictionaryRepository()
        self.userRepository = UserRepository()
        self.UPLOAD_DIR = Path("uploads/dictionaries")
        self.UPLOAD_DIR.mkdir(exist_ok=True)

    async def create_dictionary(
            self,
            db: AsyncSession,
            name: str,
            lang_chain: str,
            description: str,
            file: UploadFile,
            is_private: bool,
            username,
    ):
        """
        Создаёт новый словарь с сохранением файла.
        """
        try:
            user = await self.userRepository.get_user_by_username(db, username)

            # Сохранение файла на диск
            file.filename = f"{user.id}_" + file.filename
            file_path = self.UPLOAD_DIR / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Создание записи в базе данных
            dictionary = await self.dictionaryRepository.create_dictionary(
                db,
                name=name,
                lang_chain=lang_chain,
                description=description,
                rating=5.0,
                path=str(file_path),
                owner_id=user.id,
                is_private=is_private,
            )
            return dictionary
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {e}")
        except Exception as e:
            raise Exception(f"Error saving dictionary: {e}")

    async def get_all_dictionaries(self, db: AsyncSession):
        """
        Возвращает список всех словарей.
        """
        try:
            return await self.dictionaryRepository.get_all_dictionaries(db)
        except Exception as e:
            raise Exception(f"Error retrieving dictionaries: {e}")

    async def get_dictionary_by_id(self, db: AsyncSession, dictionary_id: int):
        """
        Возвращает словарь по ID.
        """
        try:
            dictionary = await self.dictionaryRepository.get_dictionary_by_id(db, dictionary_id)
            if not dictionary:
                raise Exception(f"Dictionary with ID {dictionary_id} not found.")
            return dictionary
        except Exception as e:
            raise Exception(f"Error retrieving dictionary by ID: {e}")

    async def get_all_users_dictionaries(self, db, username):
        """
        Возвращает список всех словарей пользователя.
        """
        try:
            user = await self.userRepository.get_user_by_username(db, username)
            return await self.dictionaryRepository.get_all_users_dictionaries(db, user.id)
        except Exception as e:
            raise Exception(f"Error retrieving dictionaries: {e}")

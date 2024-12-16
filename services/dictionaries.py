import shutil
import logging

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from repositories.dictionaries import DictionaryRepository


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DictionaryService:
    def __init__(self):
        self.repository = DictionaryRepository()
        self.UPLOAD_DIR = Path("uploads")
        self.UPLOAD_DIR.mkdir(exist_ok=True)

    async def create_dictionary(self, db: AsyncSession, name: str, lang_chain: str, description: str, file: UploadFile):
        """
        Создаёт новый словарь с сохранением файла.
        """
        try:
            # Сохранение файла на диск
            file_path = self.UPLOAD_DIR / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Создание записи в базе данных
            dictionary = await self.repository.create_dictionary(
                db,
                name=name,
                lang_chain=lang_chain,
                description=description,
                rating=5.0,
                path=str(file_path),
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
            return await self.repository.get_all_dictionaries(db)
        except Exception as e:
            raise Exception(f"Error retrieving dictionaries: {e}")

    async def get_dictionary_by_id(self, db: AsyncSession, dictionary_id: int):
        """
        Возвращает словарь по ID.
        """
        try:
            dictionary = await self.repository.get_dictionary_by_id(db, dictionary_id)
            if not dictionary:
                raise Exception(f"Dictionary with ID {dictionary_id} not found.")
            return dictionary
        except Exception as e:
            raise Exception(f"Error retrieving dictionary by ID: {e}")

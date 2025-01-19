from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import delete, update
from models.dictionaries import Dictionary  # Импортируй свою модель


class DictionaryRepository:
    async def get_all_dictionaries(self, db: AsyncSession):
        """Получить все записи из таблицы dictionaries."""
        try:
            query = select(Dictionary).where(Dictionary.is_private == False)
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving all dictionaries: {e}")

    async def get_dictionary_by_id(self, db: AsyncSession, dictionary_id: int):
        """Получить запись по id."""
        try:
            query = select(Dictionary).where(Dictionary.id == dictionary_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving dictionary by id: {e}")

    async def create_dictionary(
            self,
            db: AsyncSession,
            name: str,
            lang_chain: str,
            description: str,
            rating: float,
            path: str,
            owner_id: int,
            is_private: bool
    ):
        """Создать новую запись."""
        try:
            new_dictionary = Dictionary(
                name=name,
                lang_chain=lang_chain,
                description=description,
                rating=rating,
                path=path,
                owner_id=owner_id,
                is_private=is_private
            )
            db.add(new_dictionary)
            await db.commit()
            await db.refresh(new_dictionary)
            return new_dictionary
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error creating dictionary: {e}")

    async def update_dictionary(self, db: AsyncSession, dictionary_id: int, **kwargs):
        """Обновить запись."""
        try:
            query = update(Dictionary).where(Dictionary.id == dictionary_id).values(**kwargs).execution_options(synchronize_session="fetch")
            await db.execute(query)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error updating dictionary: {e}")

    async def delete_dictionary(self, db: AsyncSession, dictionary_id: int):
        """Удалить запись."""
        try:
            query = delete(Dictionary).where(Dictionary.id == dictionary_id)
            await db.execute(query)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Error deleting dictionary: {e}")

    async def get_all_users_dictionaries(self, db, user_id):
        """Получить все записи пользователя из таблицы dictionaries."""
        try:
            query = select(Dictionary).where(Dictionary.is_private == False and Dictionary.owner_id == user_id)
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving all dictionaries: {e}")

    async def get_all_owners_dictionaries(self, db, owner_id):
        """Получить все записи владельца из таблицы dictionaries."""
        try:
            query = select(Dictionary).where(Dictionary.owner_id == owner_id)
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving all dictionaries: {e}")

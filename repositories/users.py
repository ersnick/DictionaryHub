from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from models.users import User
from core.auth import hash_password
from schemas.users import UserCreate


class UserRepository:
    async def get_user_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Ищет пользователя по имени пользователя"""
        try:
            result = await db.execute(select(User).filter(User.username == username))
            return result.scalars().first()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving user by username: {e}")

    async def get_user_by_mail(self, db: AsyncSession, email: str) -> User | None:
        """Ищет пользователя по электронной почте"""
        try:
            result = await db.execute(select(User).filter(User.email == email))
            return result.scalars().first()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving user by username: {e}")

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Создает нового пользователя"""
        try:
            hashed_pwd = hash_password(user_data.password)
            new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_pwd)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            raise Exception(f"Error creating new user: {e}")

    async def update_user_data(
            self,
            db: AsyncSession,
            username,
            fullname: str | None = None,
            bio: str | None = None,
            photo_path: str | None = None):
        """Обновляет информацию о пользователе в базе"""
        try:
            user = await self.get_user_by_username(db, username)

            if bio is not None:
                user.bio = bio
            if fullname is not None:
                user.fullname = fullname
            if photo_path is not None:
                user.photo_path = photo_path
            await db.commit()
            await db.refresh(user)
            return user
        except SQLAlchemyError as e:
            raise Exception(f"Error updating user data: {e}")

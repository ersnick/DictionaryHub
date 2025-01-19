from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    fullname = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    is_email_confirmed = Column(Boolean, default=False)

    dictionaries = relationship("Dictionary", back_populates="owner")

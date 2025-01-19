from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DECIMAL, DateTime, Float
from datetime import datetime

from sqlalchemy.orm import relationship

from db.database import BaseModel


# Модель словаря
class Dictionary(BaseModel):
    __tablename__ = "dictionaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    lang_chain = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    path = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="dictionaries")

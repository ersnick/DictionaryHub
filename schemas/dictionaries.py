from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlalchemy import Float


# Pydantic модель для отображения информации о словаре


class DictionaryView(BaseModel):
    id: int
    lang_chain: Optional[str]
    description: Optional[str]
    rating: Float
    path: str

    class Config:
        orm_mode = True

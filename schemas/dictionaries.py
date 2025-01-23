from typing import Optional
from sqlalchemy import Float


class DictionaryView(dict):
    id: int
    name: str
    lang_chain: Optional[str]
    description: Optional[str]
    rating: Float
    owner: str

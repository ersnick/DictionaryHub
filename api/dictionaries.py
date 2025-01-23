from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from db.database import get_db
from services.dictionaries import DictionaryService
from pathlib import Path
from fastapi.responses import FileResponse
from core.auth import get_current_user


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dictionaries", tags=["Dictionaries"])
dictionary_service = DictionaryService()


@router.post("/")
async def create_dictionary(
    file: UploadFile,
    name: str = Form(...),
    lang_chain: str = Form(...),
    description: str = Form(...),
    is_private: bool = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        dictionary = await dictionary_service.create_dictionary(
            db,
            name,
            lang_chain,
            description,
            file,
            is_private,
            current_user['sub']
        )
        return JSONResponse(
            content={
                "id": dictionary.id,
                "name": dictionary.name,
                "lang_chain": dictionary.lang_chain,
                "description": dictionary.description,
                "path": dictionary.path,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_public_dictionaries(db: AsyncSession = Depends(get_db)):
    try:
        dictionaries = await dictionary_service.get_public_dictionaries(db)
        return dictionaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{username}")
async def get_all_users_dictionaries(username: str, db: AsyncSession = Depends(get_db)):
    try:
        dictionaries = await dictionary_service.get_all_users_dictionaries(db, username)
        return dictionaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dictionary_id}")
async def get_dictionary(dictionary_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает файл словаря для скачивания.
    """
    try:
        dictionary = await dictionary_service.get_dictionary_by_id(db, dictionary_id)
        if not dictionary or not dictionary.path:
            raise HTTPException(status_code=404, detail="Dictionary not found or file is missing.")

        # Проверка существования файла
        file_path = Path(dictionary.path)
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found on server.")

        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=file_path.name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

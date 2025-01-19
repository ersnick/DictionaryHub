from api import dictionaries as dictionaries_api
from api import auth as auth_api
from api import users as users_api
from models import dictionaries
from db import database
from fastapi import FastAPI


app = FastAPI()

# Подключение маршрутов
app.include_router(dictionaries_api.router)
app.include_router(auth_api.router)
app.include_router(users_api.router)


# Асинхронная функция для инициализации базы данных
async def init_db():
    async with database.engine.begin() as conn:
        # Создание таблиц, если их нет
        await conn.run_sync(dictionaries.BaseModel.metadata.create_all)


# Запуск инициализации базы данных при старте приложения
@app.on_event("startup")
async def startup_event():
    await init_db()

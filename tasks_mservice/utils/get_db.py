from typing import AsyncGenerator

from config import get_settings
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

settings = get_settings()


async def get_db() -> AsyncGenerator[AsyncDatabase, None]:
    client = AsyncMongoClient(settings.database_host, settings.database_port)
    db = client.get_database(settings.database_name.get_secret_value())
    try:
        yield db
    finally:
        await client.close()

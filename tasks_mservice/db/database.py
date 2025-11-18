import motor.motor_asyncio
from config import get_settings
from pymongo.asynchronous.database import AsyncDatabase

settings = get_settings()


class DBMManager:
    """
    Менеджер-сінглтон, який тримає ОДИН клієнт
    для всього життєвого циклу додатку.
    """

    client: motor.motor_asyncio.AsyncIOMotorClient = None
    db: AsyncDatabase = None


db_manager = DBMManager()


async def connect_to_mongo():
    """Викликається ОДИН РАЗ при старті FastAPI."""
    print("Connecting to MongoDB...")
    db_manager.client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.database_host, settings.database_port
    )
    db_manager.db = db_manager.client.get_database(
        settings.database_name.get_secret_value()
    )
    print("Connected to MongoDB!")


async def close_mongo_connection():
    """Викликається ОДИН РАЗ при зупинці FastAPI."""
    print("Closing MongoDB connection...")
    db_manager.client.close()
    print("Connection closed.")


def get_database() -> AsyncDatabase:
    """
    Це залежність, яка просто повертає
    вже існуючий об'єкт 'db' з менеджера.
    """
    return db_manager.db

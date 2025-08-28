from config import DATABASE_HOST, DATABASE_NAME, DATABASE_PORT
from pymongo import AsyncMongoClient


async def get_db():
    client = AsyncMongoClient(DATABASE_HOST, DATABASE_PORT)
    db = client.get_database(DATABASE_NAME)
    try:
        yield db
    finally:
        await client.close()

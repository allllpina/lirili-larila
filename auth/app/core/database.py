from app.core.config import DATABASE_URL
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(DATABASE_URL, future=True, echo=True)


SessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    async def save(self, db: AsyncSession):
        """
        :param db:
        :return:
        """
        try:
            db.add(self)
            return await db.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    @classmethod
    async def find_by_id(cls, db: AsyncSession, id: str):
        query = select(cls).where(cls.id == id)
        result = await db.execute(query)
        return result.scalars().first()

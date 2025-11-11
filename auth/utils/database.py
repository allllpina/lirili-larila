from datetime import datetime
from typing import AsyncGenerator

from config import get_settings
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import declarative_base, sessionmaker

settings = get_settings()

Base = declarative_base()

# Асинхронний URL для SQLAlchemy
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user.get_secret_value()}:"
    f"{settings.postgres_password.get_secret_value()}@"
    f"{settings.postgres_host}:{settings.postgres_port}/"
    f"{settings.postgres_db.get_secret_value()}"
)

# Асинхронний engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронна сесія
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Залежність для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


class ToDictMixin:
    def to_dict(self, columns: list[str] | None = None) -> dict:
        """Повертає словник з вибраними або всіма колонками."""
        mapper = inspect(self).mapper
        data = {}

        for c in mapper.column_attrs:
            key = c.key
            if columns is None or key in columns:
                data[key] = getattr(self, key)
        return data


# ORM-модель
class User(Base, ToDictMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)  # виправив sername -> username
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=True)
    is_oauth_user = Column(Boolean, default=False)
    oauth_provider = Column(String, nullable=True)
    oauth_sub = Column(String, nullable=True)
    refresh_token = Column(Text, nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

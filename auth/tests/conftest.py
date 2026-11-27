"""Shared fixtures for auth service tests.

Important: Environment variables must be set BEFORE importing `main`/`utils.database`,
because `get_settings()` is called during module import.
Assign them directly (rather than using `setdefault`) so that tests never pick up real
secrets from your local `.env`: environment variables take precedence over `.env`.
"""

import os

os.environ.update(
    {
        "GOOGLE_CLIENT_ID": "test-client-id",
        "GOOGLE_CLIENT_SECRET": "test-client-secret",
        "JWT_KEY": "test-jwt-key-not-a-real-secret-0123456789",
        "SESSION_MIDDLEWARE_SECRET": "test-session-secret",
        "FRONTEND_URL": "http://localhost:3000",
        "POSTGRES_USER": "test",
        "POSTGRES_PASSWORD": "test",
        "POSTGRES_DB": "test",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
    }
)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool
from utils.database import Base, get_db


@pytest_asyncio.fixture
async def session_maker():
    """A separate in-memory SQLite database for each test (fast, no Docker required).

    StaticPool is needed so that all connections access the same in-memory database.
    Limitation: SQLite ≠ Postgres. This can be replaced with a Postgres service in CI later on.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_maker):
    """An HTTP client that connects directly to an ASGI application with a spoofed database."""

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def user_payload() -> dict[str, str]:
    return {
        "email": "alice@example.com",
        "username": "alice",
        "password": "s3cret-pass",
    }

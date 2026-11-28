"""Shared fixtures for the projects service (tasks_mservice) tests.

Environment variables must be set BEFORE the app is imported, because settings
are read at import time. Plain assignment (not setdefault) guarantees that the
tests never pick up real secrets from a local .env file.

The tests need a real MongoDB:
    docker run --rm -p 27017:27017 mongo:7
Set REQUIRE_MONGO=1 (CI does) to fail instead of skip when Mongo is unreachable,
so a broken service container can never produce a silently green build.
"""

import os

from tests.helpers import JWT_KEY

MONGO_HOST = os.environ.get("TEST_MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("TEST_MONGO_PORT", "27017"))
TEST_DB_NAME = "tasks_service_test"

os.environ.update(
    {
        "DATABASE_HOST": MONGO_HOST,
        "DATABASE_PORT": str(MONGO_PORT),
        "DATABASE_NAME": TEST_DB_NAME,
        "FRONTEND_URL": "http://localhost:3000",
        "JWT_KEY": JWT_KEY,
        "GOOGLE_AI_API_KEY": "test-not-a-real-key",
        "GOOGLE_MODEL": "test-model",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from pymongo import MongoClient  # noqa: E402
from pymongo.errors import PyMongoError  # noqa: E402

from tests.helpers import ALICE, BOB, auth_headers, make_token  # noqa: E402


@pytest.fixture(scope="session")
def mongo_client():
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        client.close()
        message = f"MongoDB is not reachable at {MONGO_HOST}:{MONGO_PORT}"
        if os.environ.get("REQUIRE_MONGO") == "1":
            pytest.fail(message)
        pytest.skip(f"{message} (docker run --rm -p 27017:27017 mongo:7)")
    yield client
    client.close()


@pytest.fixture
def mongo_db(mongo_client):
    """A clean test database for every test (dropped before and after)."""
    assert TEST_DB_NAME.endswith("_test")  # never drop a real database
    mongo_client.drop_database(TEST_DB_NAME)
    yield mongo_client[TEST_DB_NAME]
    mongo_client.drop_database(TEST_DB_NAME)


@pytest.fixture
def client(mongo_db):
    """Sync TestClient. Entering the context manager runs the app lifespan
    (Mongo connection + WSHub) inside the client's own event loop, which is
    also what makes WebSocket tests possible."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def alice():
    return auth_headers(ALICE)


@pytest.fixture
def bob():
    return auth_headers(BOB)


@pytest.fixture
def alice_token():
    return make_token(ALICE, "alice")


@pytest.fixture
def bob_token():
    return make_token(BOB, "bob")

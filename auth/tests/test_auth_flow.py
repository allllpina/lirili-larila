import hashlib

import pytest
from sqlalchemy import select
from utils.database import User


async def test_register_login_and_get_current_user(client, user_payload):
    """The Golden Path: registration -> login -> secure endpoint."""
    # 1. Registration instantly returns JWT (JSON string)
    resp = await client.post("/register", json=user_payload)
    assert resp.status_code == 200, resp.text
    register_token = resp.json()
    assert isinstance(register_token, str) and register_token

    # 2. Login using email
    resp = await client.post(
        "/token",
        json={"login": user_payload["email"], "password": user_payload["password"]},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()

    # 3. Login using username
    resp = await client.post(
        "/token",
        json={"login": user_payload["username"], "password": user_payload["password"]},
    )
    assert resp.status_code == 200, resp.text

    # 4. Token allows usage of the secured endpoint
    resp = await client.get(
        "/get_current_user", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["email"] == user_payload["email"]
    assert body["username"] == user_payload["username"]
    assert "password_hash" not in body
    assert "refresh_token" not in body


async def test_register_duplicate_email_returns_409(client, user_payload):
    first = await client.post("/register", json=user_payload)
    assert first.status_code == 200

    second = await client.post("/register", json=user_payload)
    assert second.status_code == 409


async def test_login_with_wrong_password_returns_401(client, user_payload):
    await client.post("/register", json=user_payload)

    resp = await client.post(
        "/token",
        json={"login": user_payload["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_login_unknown_user_returns_401(client):
    resp = await client.post(
        "/token", json={"login": "nobody@example.com", "password": "whatever1"}
    )
    assert resp.status_code == 401


async def test_protected_endpoint_without_token_is_rejected(client):
    resp = await client.get("/get_current_user")
    assert resp.status_code in (401, 403)


async def test_protected_endpoint_with_garbage_token_returns_401(client):
    resp = await client.get(
        "/get_current_user", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert resp.status_code == 401


@pytest.mark.xfail(
    strict=True,
    reason="Phase 0.4: passwords are currently hashed with plain SHA-256. This test "
    "will start passing after transitioning to bcrypt/argon2 — remove xfail afterwards",
)
async def test_password_is_not_stored_as_plain_sha256(
    client, session_maker, user_payload
):
    await client.post("/register", json=user_payload)

    async with session_maker() as session:
        user = (
            await session.execute(
                select(User).where(User.email == user_payload["email"])
            )
        ).scalar_one()

    plain_sha256 = hashlib.sha256(user_payload["password"].encode()).hexdigest()
    assert user.password_hash != plain_sha256

"""Small helpers shared by the tests (token minting and entity builders)."""

from datetime import UTC, datetime, timedelta

from jose import jwt

JWT_KEY = "test-jwt-key-not-a-real-secret-0123456789"
ALGORITHM = "HS256"

ALICE = 1
BOB = 2


def make_token(user_id: int, username: str = "user") -> str:
    """Mint a JWT with the same payload shape the auth service produces."""
    payload = {
        "sub": username,
        "user_data": {"id": user_id, "username": username},
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_KEY, algorithm=ALGORITHM)


def auth_headers(user_id: int) -> dict:
    return {"Authorization": f"Bearer {make_token(user_id)}"}


def collaborator(user_id: int, salary: float = 10.0, role: str = "developer") -> dict:
    return {"usr_id": user_id, "role": role, "salary": salary}


# NOTE: HTTP responses use the "_id" alias (FastAPI serializes by alias),
# while WebSocket messages use model_dump() and therefore carry "id".


def create_project(client, headers, name="Project", admin_id=ALICE, collaborators=None):
    resp = client.post(
        "/projects/create_project",
        headers=headers,
        json={
            "admin_id": admin_id,
            "name": name,
            "collaborators": collaborators or [],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def create_page(client, headers, project_id, name="Page"):
    resp = client.post(
        "/pages/create_page",
        headers=headers,
        params={"project_id": project_id},
        json={"name": name},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def create_board(client, headers, page_id, name="Board"):
    resp = client.post(
        "/boards/create_board",
        headers=headers,
        params={"page_id": page_id},
        json={"name": name},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def create_task(client, headers, board_id, name="Task", **extra):
    resp = client.post(
        "/tasks/create_task",
        headers=headers,
        params={"board_id": board_id},
        json={"name": name, **extra},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()

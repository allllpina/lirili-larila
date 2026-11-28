import uuid

import pytest

from tests.helpers import BOB, collaborator, create_project


def test_project_crud_lifecycle(client, alice):
    project = create_project(client, alice, name="Roadmap")
    project_id = project["_id"]
    assert project["name"] == "Roadmap"
    assert project["page_ids"] == []

    resp = client.get(f"/projects/get_project/{project_id}", headers=alice)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Roadmap"

    resp = client.get("/projects/my_projects", headers=alice)
    assert resp.status_code == 200
    assert project_id in [p["_id"] for p in resp.json()]

    resp = client.put(
        "/projects/edit_project",
        headers=alice,
        params={"project_id": project_id},
        json={"name": "Renamed"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"

    resp = client.delete(f"/projects/delete_project/{project_id}", headers=alice)
    assert resp.status_code == 200
    assert resp.json()["deleted_project"] == project_id

    resp = client.get(f"/projects/get_project/{project_id}", headers=alice)
    assert resp.status_code == 404


def test_project_is_forbidden_for_a_stranger(client, alice, bob):
    project = create_project(client, alice)

    resp = client.get(f"/projects/get_project/{project['_id']}", headers=bob)
    assert resp.status_code == 403


def test_collaborator_can_read_the_project(client, alice, bob):
    project = create_project(client, alice, collaborators=[collaborator(BOB)])

    resp = client.get(f"/projects/get_project/{project['_id']}", headers=bob)
    assert resp.status_code == 200


def test_endpoints_require_authentication(client):
    resp = client.get("/projects/my_projects")
    # FastAPI 0.116 answers 403 for a missing bearer header, newer versions 401.
    assert resp.status_code in (401, 403)


def test_any_collaborator_can_delete_the_project(client, alice, bob):
    """Characterization test: documents CURRENT behaviour.

    Roadmap 0.6 introduces owner/editor/viewer roles; once only the owner may
    delete a project, flip this assertion to 403.
    """
    project = create_project(client, alice, collaborators=[collaborator(BOB)])

    resp = client.delete(f"/projects/delete_project/{project['_id']}", headers=bob)
    assert resp.status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="Roadmap 0.7: decode_jwt_token raises ValueError, but get_user_data only "
    "catches JWTError, so a garbage token currently produces a 500. "
    "Remove the marker once it returns 401.",
)
def test_garbage_token_returns_401(client):
    resp = client.get(
        "/projects/my_projects", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert resp.status_code == 401


@pytest.mark.xfail(
    strict=True,
    reason="Roadmap 0.7: UsersRepository.check_access does record['users'] on None, "
    "so an unknown project currently produces a 500. Expected: 404.",
)
def test_unknown_project_returns_404(client, alice):
    resp = client.get(f"/projects/get_project/{uuid.uuid4()}", headers=alice)
    assert resp.status_code == 404


@pytest.mark.xfail(
    strict=True,
    reason="Roadmap 0.5: deleting a project leaves its record in the 'users' "
    "collection behind. Remove the marker once it is cleaned up.",
)
def test_delete_project_removes_the_access_record(client, alice, mongo_db):
    project = create_project(client, alice)
    client.delete(f"/projects/delete_project/{project['_id']}", headers=alice)

    assert mongo_db["users"].find_one({"_id": project["_id"]}) is None

import pytest
from starlette.websockets import WebSocketDisconnect

from tests.helpers import create_page, create_project

POLICY_VIOLATION = 1008


def ws_url(project_id, token=None):
    url = f"/projects/ws/{project_id}"
    return f"{url}?token={token}" if token else url


def test_ws_rejects_a_missing_token(client, alice):
    project = create_project(client, alice)

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(ws_url(project["_id"])):
            pass
    assert exc_info.value.code == POLICY_VIOLATION


def test_ws_rejects_an_invalid_token(client, alice):
    project = create_project(client, alice)

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(ws_url(project["_id"], "not-a-jwt")):
            pass
    assert exc_info.value.code == POLICY_VIOLATION


def test_ws_rejects_a_user_without_access(client, alice, bob_token):
    project = create_project(client, alice)

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(ws_url(project["_id"], bob_token)):
            pass
    assert exc_info.value.code == POLICY_VIOLATION


def test_ws_receives_a_broadcast_when_a_page_is_created(client, alice, alice_token):
    project = create_project(client, alice)

    with client.websocket_connect(ws_url(project["_id"], alice_token)) as ws:
        page = create_page(client, alice, project["_id"], name="Live page")
        message = ws.receive_json()

    assert message["category"] == "pages"
    assert message["operation"] == "create"
    # WebSocket payloads come from model_dump(), so the key is "id" (HTTP uses "_id").
    assert message["content"]["id"] == page["_id"]
    assert message["content"]["name"] == "Live page"

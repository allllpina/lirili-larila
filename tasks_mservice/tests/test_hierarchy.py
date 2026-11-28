"""Project -> page -> board -> task: creation, editing, moving and cascade deletes."""

from tests.helpers import (
    ALICE,
    collaborator,
    create_board,
    create_page,
    create_project,
    create_task,
)


def build_tree(client, headers):
    project = create_project(client, headers)
    page = create_page(client, headers, project["_id"])
    board = create_board(client, headers, page["_id"])
    task = create_task(client, headers, board["_id"])
    return project, page, board, task


def test_creating_the_full_hierarchy_links_every_level(client, alice):
    project, page, board, task = build_tree(client, alice)

    assert task["board_id"] == board["_id"]
    assert task["project_id"] == project["_id"]
    # Defaults of TaskCreate
    assert task["priority"] == "None"
    assert task["status"] == "not done"

    resp = client.get(f"/projects/get_project/{project['_id']}", headers=alice)
    assert resp.json()["page_ids"] == [page["_id"]]

    resp = client.get(f"/pages/get_page/{page['_id']}", headers=alice)
    assert resp.json()["board_ids"] == [board["_id"]]

    resp = client.get(f"/boards/get_board/{board['_id']}", headers=alice)
    assert resp.json()["task_ids"] == [task["_id"]]


def test_edit_page_board_and_task(client, alice):
    _, page, board, task = build_tree(client, alice)

    resp = client.put(
        "/pages/edit_page",
        headers=alice,
        params={"page_id": page["_id"]},
        json={"name": "New page name"},
    )
    assert resp.status_code == 200 and resp.json()["name"] == "New page name"

    resp = client.put(
        "/boards/edit_board",
        headers=alice,
        params={"board_id": board["_id"]},
        json={"name": "New board name"},
    )
    assert resp.status_code == 200 and resp.json()["name"] == "New board name"

    resp = client.put(
        "/tasks/edit_task",
        headers=alice,
        params={"task_id": task["_id"]},
        json={"priority": "high", "tags": ["backend"]},
    )
    assert resp.status_code == 200
    assert resp.json()["priority"] == "high"
    assert resp.json()["tags"] == ["backend"]


def test_move_task_between_boards(client, alice):
    _, page, board_a, task = build_tree(client, alice)
    board_b = create_board(client, alice, page["_id"], name="Done")

    resp = client.put(
        "/tasks/move_task",
        headers=alice,
        json={
            "taskId": task["_id"],
            "boardGiverId": board_a["_id"],
            "boardReceiverId": board_b["_id"],
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    giver = client.get(f"/boards/get_board/{board_a['_id']}", headers=alice).json()
    receiver = client.get(f"/boards/get_board/{board_b['_id']}", headers=alice).json()
    assert giver["task_ids"] == []
    assert receiver["task_ids"] == [task["_id"]]

    moved = client.get(f"/tasks/get_task/{task['_id']}", headers=alice).json()
    assert moved["board_id"] == board_b["_id"]


def test_move_task_to_a_board_of_another_project_is_rejected(client, alice):
    _, _, board_a, task = build_tree(client, alice)
    other_project = create_project(client, alice, name="Other")
    other_page = create_page(client, alice, other_project["_id"])
    foreign_board = create_board(client, alice, other_page["_id"])

    resp = client.put(
        "/tasks/move_task",
        headers=alice,
        json={
            "taskId": task["_id"],
            "boardGiverId": board_a["_id"],
            "boardReceiverId": foreign_board["_id"],
        },
    )
    assert resp.status_code == 400


def test_delete_task_unlinks_it_from_the_board(client, alice):
    _, _, board, task = build_tree(client, alice)

    resp = client.delete(f"/tasks/delete_task/{task['_id']}", headers=alice)
    assert resp.status_code == 200

    assert (
        client.get(f"/tasks/get_task/{task['_id']}", headers=alice).status_code == 404
    )
    board_now = client.get(f"/boards/get_board/{board['_id']}", headers=alice).json()
    assert board_now["task_ids"] == []


def test_delete_page_cascades_to_boards_and_tasks(client, alice):
    _, page, board, task = build_tree(client, alice)

    resp = client.delete(f"/pages/delete_page/{page['_id']}", headers=alice)
    assert resp.status_code == 200
    assert resp.json()["deleted_boards"] == 1
    assert resp.json()["deleted_tasks"] == 1

    assert (
        client.get(f"/boards/get_board/{board['_id']}", headers=alice).status_code
        == 404
    )
    assert (
        client.get(f"/tasks/get_task/{task['_id']}", headers=alice).status_code == 404
    )


def test_delete_project_cascades_to_everything_below(client, alice):
    project, page, board, task = build_tree(client, alice)

    resp = client.delete(f"/projects/delete_project/{project['_id']}", headers=alice)
    assert resp.status_code == 200
    body = resp.json()
    assert (body["deleted_pages"], body["deleted_boards"], body["deleted_tasks"]) == (
        1,
        1,
        1,
    )

    assert (
        client.get(f"/pages/get_page/{page['_id']}", headers=alice).status_code == 404
    )
    assert (
        client.get(f"/tasks/get_task/{task['_id']}", headers=alice).status_code == 404
    )


def test_cost_report_sums_completed_tasks(client, alice):
    project, _, _, task = build_tree(client, alice)

    resp = client.put(
        "/tasks/edit_task",
        headers=alice,
        params={"task_id": task["_id"]},
        json={
            "status": "complete",
            "time_to_complete": 2.0,
            "collaborators": [collaborator(ALICE, salary=10.0)],
        },
    )
    assert resp.status_code == 200, resp.text

    resp = client.get(f"/projects/get_cost_evaluation/{project['_id']}", headers=alice)
    assert resp.status_code == 200, resp.text
    assert resp.json()["overall"] == 20.0  # 10.0 per hour * 2.0 hours

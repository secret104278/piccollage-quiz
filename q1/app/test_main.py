from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

# TODO: database setup and teardown
# TODO: add more tests

def test_search_stickers():
    response = client.get("/sticker/search", params={"search_term": "a cat in park"})
    assert response.status_code == 200

    sticker_ids = response.json()["sticker_ids"]
    assert isinstance(sticker_ids, list) and len(sticker_ids) == 10
    assert all(isinstance(item, int) for item in sticker_ids)


def test_report_stickers():
    response = client.post(
        "/sticker/report", json={"search_term": "hello world", "sticker_ids": [1, 2, 5]}
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_get_feedback():

    response = client.get("/sticker/feedback", params={"window_hour": 10})

    assert response.status_code == 200

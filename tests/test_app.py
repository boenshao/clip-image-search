from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


def test_search(client: TestClient) -> None:
    response = client.get("/search", params={"query": "double-decker bus"})
    assert response.status_code == 200
    content = response.json()
    assert content["image_url"] == "COCO_val2014_000000001584.jpg"
    assert content.get("search_log_id") is not None

    response = client.get("/search", params={"query": "a child and lots of suitcases"})
    assert response.status_code == 200
    content = response.json()
    assert content["image_url"] == "COCO_val2014_000000004243.jpg"
    assert content.get("search_log_id") is not None

    response = client.get("/search", params={"query": "two black birds"})
    assert response.status_code == 200
    content = response.json()
    assert content["image_url"] == "COCO_val2014_000000004283.jpg"
    assert content.get("search_log_id") is not None


def test_search_and_rating(client: TestClient) -> None:
    response = client.get("/search", params={"query": "double-decker bus"})
    assert response.status_code == 200
    content = response.json()
    assert content["image_url"] == "COCO_val2014_000000001584.jpg"
    assert content["search_log_id"] is not None

    response = client.patch(f'/rating/{content["search_log_id"]}', params={"score": -1})
    assert response.status_code == 422
    response = client.patch(f'/rating/{content["search_log_id"]}', params={"score": 2})
    assert response.status_code == 422
    response = client.patch(f'/rating/{content["search_log_id"]}', params={"score": 0})
    assert response.status_code == 204
    response = client.patch(f'/rating/{content["search_log_id"]}', params={"score": 1})
    assert response.status_code == 204

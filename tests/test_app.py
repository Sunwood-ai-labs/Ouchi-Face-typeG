from __future__ import annotations

import importlib
from typing import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("OUCHI_FACE_DB_PATH", str(db_path))

    from ouchi_face import database, repositories, main

    importlib.reload(database)
    database.ensure_database()
    importlib.reload(repositories)
    importlib.reload(main)

    test_app = main.app
    with TestClient(test_app) as client:
        yield client


def test_create_and_list_resource(client: TestClient) -> None:
    response = client.post(
        "/resources",
        data={
            "name": "Stable Diffusion WebUI",
            "resource_type": "app",
            "description": "ローカルで画像生成する推しUI",
            "link_url": "http://localhost:7860",
            "location": "nas://ml/apps/sd-webui",
            "icon_url": "https://example.com/icon.png",
            "repo_url": "https://github.com/AUTOMATIC1111/stable-diffusion-webui",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    api_response = client.get("/api/resources")
    assert api_response.status_code == 200
    payload = api_response.json()
    assert len(payload) == 1
    resource = payload[0]
    assert resource["name"] == "Stable Diffusion WebUI"
    assert resource["resource_type"] == "app"

    page = client.get("/")
    assert "Stable Diffusion WebUI" in page.text


def test_resource_detail_not_found(client: TestClient) -> None:
    response = client.get("/resources/999")
    assert response.status_code == 404


def test_search_filters_resources(client: TestClient) -> None:
    client.post(
        "/resources",
        data={
            "name": "Local Dataset",
            "resource_type": "dataset",
            "description": "社内学習用コーパス",
        },
        follow_redirects=False,
    )
    client.post(
        "/resources",
        data={
            "name": "Forgejo Repo",
            "resource_type": "repository",
            "description": "社内コード置き場",
        },
        follow_redirects=False,
    )

    response = client.get("/?q=Forgejo")
    assert response.status_code == 200
    assert "Forgejo Repo" in response.text
    assert "Local Dataset" not in response.text

    api_response = client.get("/api/resources", params={"resource_type": "dataset"})
    assert api_response.status_code == 200
    data = api_response.json()
    assert len(data) == 1
    assert data[0]["resource_type"] == "dataset"

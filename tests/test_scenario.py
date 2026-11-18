"""Shallow scenario smoke tests — intentionally weak."""

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def setup_module() -> None:
    seed(reset=True)


def test_health_ok():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["scenario"] == "research-plat"


def test_login_admin():
    with TestClient(app) as client:
        r = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin-dev"},
        )
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "admin"
        assert "password" not in r.json()["user"]
        assert "password_hash" not in r.json()["user"]


def test_list_authors_and_publications():
    with TestClient(app) as client:
        r = client.get("/api/authors")
        assert r.status_code == 200
        assert len(r.json()["authors"]) >= 4
        r = client.get("/api/publications")
        assert r.status_code == 200
        assert len(r.json()["publications"]) >= 4


def test_publication_tree_smoke():
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin-dev"},
        )
        uid = login.json()["user"]["id"]
        authors = client.get("/api/authors").json()["authors"]
        root_id = authors[0]["id"]
        r = client.get(
            f"/api/authors/{root_id}/publication-tree",
            params={"max_depth": 3},
            headers={"X-User-Id": str(uid)},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert "tree" in body

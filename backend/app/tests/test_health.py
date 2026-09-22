from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_system_info() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/system/info")
        assert response.status_code == 200
        body = response.json()
        assert body["product"] == "PlantGuard AI"


def test_register_login_and_me() -> None:
    with TestClient(app) as client:
        email = "tester_unique@example.com"
        password = "SecurePass123!"
        reg = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Test User"},
        )
        assert reg.status_code == 200, reg.text
        assert reg.json()["success"] is True
        token = reg.json()["data"]["tokens"]["access_token"]
        me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["data"]["email"] == email


def test_diseases_list() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/diseases")
        assert res.status_code == 200
        assert res.json()["success"] is True
        assert len(res.json()["data"]) >= 1

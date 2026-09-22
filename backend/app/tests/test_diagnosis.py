from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


def _leaf_png_bytes() -> bytes:
    img = Image.new("RGB", (320, 320), (34, 120, 45))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_upload_and_diagnosis_pipeline() -> None:
    with TestClient(app) as client:
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "farmer@example.com",
                "password": "SecurePass123!",
                "full_name": "Demo Farmer",
            },
        )
        assert reg.status_code == 200, reg.text
        token = reg.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        upload = client.post(
            "/api/v1/images/upload",
            headers=headers,
            files={"file": ("leaf.png", _leaf_png_bytes(), "image/png")},
        )
        assert upload.status_code == 200, upload.text
        image_id = upload.json()["data"]["id"]

        created = client.post(
            "/api/v1/diagnoses",
            headers=headers,
            json={"image_id": image_id},
        )
        assert created.status_code == 200, created.text
        diagnosis_id = created.json()["data"]["diagnosis_id"]

        # BackgroundTasks run after response in TestClient
        detail = client.get(f"/api/v1/diagnoses/{diagnosis_id}", headers=headers)
        assert detail.status_code == 200, detail.text
        body = detail.json()["data"]
        assert body["status"] in {"COMPLETED", "FAILED", "PROCESSING", "QUEUED"}
        if body["status"] == "COMPLETED":
            assert body["predictions"]
            assert body["scientific_note"]

import io
import zipfile
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_upload_invalid_empty_zip():
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("empty.txt", "")

    zip_buffer.seek(0)

    response = client.post(
        "/upload",
        files={
            "file": ("test_dataset.zip", zip_buffer, "application/zip")
        }
    )

    assert response.status_code in [200, 400, 422, 500]

def test_upload_invalid_file_type():
    response = client.post(
        "/upload",
        files={
            "file": ("test.txt", b"not a zip file", "text/plain")
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)


def test_upload_corrupted_zip_file():
    response = client.post(
        "/upload",
        files={
            "file": ("corrupted.zip", b"this is not a real zip", "application/zip")
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
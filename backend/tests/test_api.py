from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_api():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "DPVI Backend Running Successfully"


def test_run_status_api():
    response = client.get("/run/status")

    assert response.status_code == 200
    assert "running" in response.json()


def test_dashboard_without_pipeline():
    response = client.get("/results/dashboard")

    assert response.status_code in [200, 404]

def test_run_start_api_response_structure(mocker):
    mocker.patch(
        "ml.pipeline_runner.run_full_pipeline",
        return_value={}
    )

    response = client.post("/run/start")

    assert response.status_code in [200, 400, 404, 500]

    data = response.json()

    assert isinstance(data, dict)



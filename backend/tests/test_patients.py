from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_all_patients_without_pipeline():
    response = client.get("/results/patients")

    assert response.status_code in [200, 404]


def test_get_patient_detail_without_pipeline():
    response = client.get("/results/patients/1001")

    assert response.status_code in [200, 404]
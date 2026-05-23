from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_results_dashboard_api():
    response = client.get("/results/dashboard")

    assert response.status_code in [200, 404]


def test_results_graphs_api():
    response = client.get("/results/graphs")

    assert response.status_code in [200, 404]


def test_results_metrics_api():
    response = client.get("/results/metrics")

    assert response.status_code in [200, 404]


def test_results_ledger_api():
    response = client.get("/results/ledger")

    assert response.status_code in [200, 404]
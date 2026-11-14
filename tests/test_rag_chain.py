from fastapi.testclient import TestClient

from reviewer import app


def test_cites_sample_policy():
    response = TestClient(app).post("/query", json={"question": "What is AC-2?"})
    assert response.status_code == 200
    assert "reviewed quarterly" in response.json()["answer"]
    assert response.json()["sources"] == ["sample_data/sample_policy.txt"]


def test_abstains_without_matching_control():
    response = TestClient(app).post("/query", json={"question": "What is AC-3?"})
    assert response.json() == {"answer": None, "sources": []}

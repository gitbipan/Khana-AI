"""
Tests for PoshanAI FastAPI Server and REST APIs.
"""

from fastapi.testclient import TestClient
import pytest
from server import app

client = TestClient(app)


def test_index_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "PoshanAI" in response.text
    assert "पोषण AI" in response.text


def test_login_and_bmr_calculation():
    payload = {
        "name": "Baibhav",
        "age_years": 24,
        "sex": "male",
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "activity_level": "moderate",
        "goal": "maintain",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user_name"] == "Baibhav"
    assert "bmr_kcal" in data["assessment"]
    assert "tdee_kcal" in data["assessment"]
    assert data["assessment"]["bmr_kcal"] > 1600


def test_foods_api():
    response = client.get("/api/foods")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] >= 20

    # Search filter
    search_res = client.get("/api/foods?query=dhindo")
    assert search_res.status_code == 200
    assert search_res.json()["count"] >= 1


def test_samples_api():
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["samples"]) >= 4


def test_analyze_sample():
    payload = {
        "sample_filename": "dal_bhat_tarkari.jpg",
        "custom_profile": {
            "age_years": 24,
            "sex": "male",
            "height_cm": 170.0,
            "weight_kg": 62.0,
            "activity_level": "moderate",
            "goal": "maintain",
        },
    }
    response = client.post("/api/analyze/sample", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "recognition" in data
    assert "meal" in data
    assert "evaluation" in data
    assert data["meal"]["totals"]["calories"] > 0
    assert data["evaluation"]["score_out_of_10"] > 0


def test_chat_api():
    payload = {
        "message": "मेरो BMR कति छ र यो खाना ठीक छ?",
        "language": "ne",
        "profile": {
            "age_years": 24,
            "sex": "male",
            "height_cm": 170.0,
            "weight_kg": 62.0,
            "activity_level": "moderate",
            "goal": "maintain",
        },
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["reply"]) > 10
    assert "क्यालोरी" in data["reply"] or "BMR" in data["reply"]
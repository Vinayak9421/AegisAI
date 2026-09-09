import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from fastapi.testclient import TestClient
from demo_target.local_model_api import app

client = TestClient(app)

def test_chat_success():
    response = client.post("/chat", json={
        "request_id": "req-123",
        "message": "Hello",
        "model_key": "small_instruct_local_v1"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "Mock response" in data["reply"] or "Simulation" in data["reply"]
    assert data["request_id"] == "req-123"
    assert "model" in data

def test_chat_empty_message():
    response = client.post("/chat", json={
        "request_id": "req-123",
        "message": "   ",
        "model_key": "small_instruct_local_v1"
    })
    assert response.status_code == 400
    assert "Empty message" in response.json()["detail"]

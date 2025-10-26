import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
import src.app as app_module

@pytest.fixture(autouse=True)
def client():
    # Provide a fresh, minimal activities set for each test to avoid cross-test pollution
    base_activities = {
        "Test Club": {
            "description": "A test activity",
            "schedule": "Now",
            "max_participants": 5,
            "participants": []
        }
    }
    app_module.activities = deepcopy(base_activities)
    client = TestClient(app_module.app)
    yield client

def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Test Club" in data
    assert data["Test Club"]["participants"] == []

def test_signup_and_duplicate(client):
    email = "alice@test.edu"
    # sign up
    resp = client.post("/activities/Test Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities["Test Club"]["participants"]

    # duplicate signup should fail
    resp2 = client.post("/activities/Test Club/signup", params={"email": email})
    assert resp2.status_code == 400

def test_remove_participant(client):
    email = "bob@test.edu"
    # sign up first
    resp = client.post("/activities/Test Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities["Test Club"]["participants"]

    # remove participant
    del_resp = client.delete("/activities/Test Club/participants", params={"email": email})
    assert del_resp.status_code == 200
    assert email not in app_module.activities["Test Club"]["participants"]

    # removing again should return 404
    del_resp2 = client.delete("/activities/Test Club/participants", params={"email": email})
    assert del_resp2.status_code == 404

from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


_original_participants = {k: v["participants"][:] for k, v in activities.items()}


def teardown_function(fn):
    # Restore participants to original state after each test
    for k in activities:
        activities[k]["participants"] = _original_participants[k][:]


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity names
    assert "Chess Club" in data


def test_signup_success():
    activity = "Basketball Team"
    email = "tester@mergington.edu"
    url = f"/activities/{quote(activity)}/signup"
    resp = client.post(url, params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_duplicate():
    activity = "Basketball Team"
    email = "repeat@mergington.edu"
    url = f"/activities/{quote(activity)}/signup"
    # First signup should succeed
    r1 = client.post(url, params={"email": email})
    assert r1.status_code == 200
    # Second signup should fail with 400
    r2 = client.post(url, params={"email": email})
    assert r2.status_code == 400
    assert "already" in r2.json().get("detail", "").lower()


def test_remove_participant_success():
    activity = "Chess Club"
    email = "remove-me@mergington.edu"
    # Ensure participant exists
    activities[activity]["participants"].append(email)

    url = f"/activities/{quote(activity)}/participants"
    resp = client.delete(url, params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
    assert "Removed" in resp.json().get("message", "")


def test_remove_nonexistent_participant():
    activity = "Chess Club"
    email = "not-present@mergington.edu"
    url = f"/activities/{quote(activity)}/participants"
    resp = client.delete(url, params={"email": email})
    assert resp.status_code == 404

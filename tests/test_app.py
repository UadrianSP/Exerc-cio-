import copy
import sys
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_signup_for_activity_success():
    client = TestClient(app)
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{quote('Chess Club')}/signup?email={email}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity():
    client = TestClient(app)

    response = client.post(
        "/activities/Unknown%20Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_email_is_rejected():
    client = TestClient(app)
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{quote('Chess Club')}/signup?email={email}"
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}


def test_get_activities_lists_registered_students():
    client = TestClient(app)

    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

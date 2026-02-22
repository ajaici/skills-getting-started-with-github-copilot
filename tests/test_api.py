from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)

def reset_activities():
    """Arrange: save and restore the in-memory activities dict between tests"""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange
    # (state is already default via fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    email = "dup@mergington.edu"
    activity = "Chess Club"
    # sign up once
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_full():
    # Arrange
    activity = "Chess Club"
    # make it full
    activities[activity]["participants"] = [f"x{i}@test" for i in range(activities[activity]["max_participants"])]
    email = "latecomer@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


def test_remove_participant_success():
    # Arrange
    activity = "Chess Club"
    email = "removable@mergington.edu"
    activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_enrolled():
    # Arrange
    activity = "Chess Club"
    email = "ghost@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not enrolled" in response.json()["detail"].lower()


def test_remove_participant_activity_not_found():
    # Arrange
    activity = "Nonexistent"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "activity not found" in response.json()["detail"].lower()


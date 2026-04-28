import copy

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
original_activities = copy.deepcopy(app_module.activities)


def reset_activities():
    app_module.activities = copy.deepcopy(original_activities)


def test_get_activities_returns_all_activities():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()
    assert response.json()["Chess Club"]["max_participants"] == 12


def test_signup_adds_participant_to_activity():
    reset_activities()

    email = "teststudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    reset_activities()

    email = "emma@mergington.edu"
    response = client.post(f"/activities/Programming%20Class/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities["Programming Class"]["participants"].count(email) == 1


def test_delete_participant_removes_student():
    reset_activities()

    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant_returns_400():
    reset_activities()

    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants/{email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_for_invalid_activity_returns_404():
    reset_activities()

    email = "student@mergington.edu"
    response = client.post(f"/activities/Unknown%20Club/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_from_invalid_activity_returns_404():
    reset_activities()

    email = "student@mergington.edu"
    response = client.delete(f"/activities/Unknown%20Club/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

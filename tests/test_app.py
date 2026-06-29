from src.app import activities


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"

    data = response.json()
    assert set(data.keys()) == set(activities.keys())
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_activity_rejects_duplicate_participant(client):
    email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_for_activity_rejects_full_activity(client):
    activity = activities["Chess Club"]
    activity["max_participants"] = len(activity["participants"])

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "full.activity@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_unregister_from_activity_removes_participant(client):
    email = activities["Chess Club"]["participants"][0]

    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_from_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_returns_404_for_missing_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missing.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}

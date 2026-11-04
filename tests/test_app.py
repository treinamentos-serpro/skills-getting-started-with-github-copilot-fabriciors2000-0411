"""Tests for the Mergington High School activities API."""

from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert data.keys() == activities.keys()

    def test_activity_has_expected_fields(self, client):
        data = client.get("/activities").json()
        chess = data["Chess Club"]
        assert chess["description"]
        assert chess["schedule"]
        assert chess["max_participants"] == 12
        assert "michael@mergington.edu" in chess["participants"]


class TestSignup:
    def test_signup_success(self, client):
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup", params={"email": email}
        )
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for Chess Club"}
        assert email in activities["Chess Club"]["participants"]

    def test_signup_unknown_activity_returns_404(self, client):
        response = client.post(
            "/activities/Knitting Club/signup",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_returns_400(self, client):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Student already signed up for this activity"
        )

    def test_signup_requires_email(self, client):
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_success(self, client):
        email = "michael@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister", params={"email": email}
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from Chess Club"
        }
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_unknown_activity_returns_404(self, client):
        response = client.delete(
            "/activities/Knitting Club/unregister",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_signed_up_returns_400(self, client):
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "ghost@mergington.edu"},
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Student is not signed up for this activity"
        )


class TestSignupUnregisterFlow:
    def test_signup_then_unregister_round_trip(self, client):
        email = "roundtrip@mergington.edu"
        assert (
            client.post(
                "/activities/Art Club/signup", params={"email": email}
            ).status_code
            == 200
        )
        assert email in activities["Art Club"]["participants"]
        assert (
            client.delete(
                "/activities/Art Club/unregister", params={"email": email}
            ).status_code
            == 200
        )
        assert email not in activities["Art Club"]["participants"]

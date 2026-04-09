"""
Unit and integration tests for FastAPI endpoints.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from starlette.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / redirect endpoint."""

    def test_root_redirects_to_static_index(self, client, reset_activities):
        """
        Test that root path redirects to static/index.html.
        
        AAA Pattern:
        - Arrange: TestClient is ready
        - Act: GET request to /
        - Assert: Response redirects to /static/index.html
        """
        # Arrange: Nothing special needed, client fixture is ready

        # Act: Make GET request to root
        response = client.get("/", follow_redirects=False)

        # Assert: Verify redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_returns_dict(self, client, reset_activities):
        """
        Test that /activities endpoint returns all activities as a dictionary.
        
        AAA Pattern:
        - Arrange: Activities are initialized in app
        - Act: GET /activities
        - Assert: Response contains dict with activity names as keys
        """
        # Arrange: Activities are pre-loaded in the app

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Verify response structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activity_has_required_fields(self, client, reset_activities):
        """
        Test that each activity has required fields: description, schedule, 
        max_participants, participants.
        
        AAA Pattern:
        - Arrange: GET /activities endpoint
        - Act: Retrieve activities and check first activity
        - Assert: Verify all required fields exist
        """
        # Arrange: Make request and get activities
        response = client.get("/activities")
        data = response.json()

        # Act: Get first activity
        first_activity = next(iter(data.values()))

        # Assert: Check all required fields are present
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_activities_contain_expected_names(self, client, reset_activities):
        """
        Test that certain standard activities are present in the list.
        
        AAA Pattern:
        - Arrange: Sample activity names to verify
        - Act: GET /activities and check names
        - Assert: Verify expected activities exist
        """
        # Arrange: List of expected activities
        expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]

        # Act: Get all activities
        response = client.get("/activities")
        data = response.json()
        activity_names = list(data.keys())

        # Assert: Verify expected activities are present
        for activity in expected_activities:
            assert activity in activity_names


class TestSignupEndpoint:
    """Tests for POST /activities/{activity}/signup endpoint."""

    def test_signup_new_participant_success(self, client, reset_activities, sample_activity, sample_new_email):
        """
        Test successful signup of a new participant for an activity.
        
        AAA Pattern:
        - Arrange: Get current participant count
        - Act: POST signup request with new email
        - Assert: Verify success response and participant added
        """
        # Arrange: Get initial participant count
        activities_response = client.get("/activities")
        initial_participants = len(activities_response.json()[sample_activity]["participants"])

        # Act: Send signup request
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_new_email}
        )

        # Assert: Verify response and participant count increased
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        new_participant_count = len(activities_response.json()[sample_activity]["participants"])
        assert new_participant_count == initial_participants + 1
        assert sample_new_email in activities_response.json()[sample_activity]["participants"]

    def test_signup_duplicate_participant_fails(self, client, reset_activities, sample_activity):
        """
        Test that signup fails when participant is already enrolled.
        
        AAA Pattern:
        - Arrange: Get existing participant email from activity
        - Act: Try to signup same participant again
        - Assert: Verify error response
        """
        # Arrange: Get an existing participant
        activities_response = client.get("/activities")
        existing_participant = activities_response.json()[sample_activity]["participants"][0]

        # Act: Try to signup existing participant
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": existing_participant}
        )

        # Assert: Verify error response
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities, sample_new_email):
        """
        Test that signup fails when activity doesn't exist.
        
        AAA Pattern:
        - Arrange: Use a non-existent activity name
        - Act: POST signup request for non-existent activity
        - Assert: Verify 404 error response
        """
        # Arrange: Non-existent activity name
        fake_activity = "Nonexistent Activity XYZ"

        # Act: Try to signup for non-existent activity
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": sample_new_email}
        )

        # Assert: Verify 404 not found error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

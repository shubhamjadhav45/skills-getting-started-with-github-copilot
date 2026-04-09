"""
Validation tests for edge cases and input handling.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


class TestSignupValidation:
    """Tests for signup endpoint validation logic."""

    def test_signup_with_special_characters_in_email(self, client, reset_activities, sample_activity):
        """
        Test that email with special characters is handled correctly.
        
        AAA Pattern:
        - Arrange: Email with special characters
        - Act: POST signup with special char email
        - Assert: Verify request is processed
        """
        # Arrange: Email with special characters
        special_email = "test.student+tag@mergington.edu"

        # Act: Signup with special character email
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": special_email}
        )

        # Assert: Verify signup succeeds (email is valid)
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert special_email in activities_response.json()[sample_activity]["participants"]

    def test_signup_preserves_case_sensitive_emails(self, client, reset_activities, sample_activity):
        """
        Test that email addresses preserve case sensitivity (as per email standards).
        
        AAA Pattern:
        - Arrange: Two emails that differ only in case
        - Act: Signup with both emails
        - Assert: Both should be treated as different emails (case-sensitive)
        """
        # Arrange: Two emails differing only in case
        email_lowercase = "test.student@mergington.edu"
        email_uppercase = "Test.Student@mergington.edu"

        # Act: Signup first email
        response1 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email_lowercase}
        )

        # Act: Try to signup second email (different case)
        response2 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email_uppercase}
        )

        # Assert: Both signups should succeed (case-sensitive)
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both participants are listed
        activities_response = client.get("/activities")
        participants = activities_response.json()[sample_activity]["participants"]
        assert email_lowercase in participants
        assert email_uppercase in participants

    def test_signup_activity_name_case_matters(self, client, reset_activities, sample_new_email):
        """
        Test that activity name lookup is case-sensitive.
        
        AAA Pattern:
        - Arrange: Activity name with different case
        - Act: POST signup with different case activity name
        - Assert: Verify 404 error for mismatched case
        """
        # Arrange: Correct activity name: "Chess Club"
        wrong_case_activity = "chess club"  # lowercase

        # Act: Try to signup with wrong case
        response = client.post(
            f"/activities/{wrong_case_activity}/signup",
            params={"email": sample_new_email}
        )

        # Assert: Verify activity not found (case-sensitive)
        assert response.status_code == 404

    def test_multiple_signups_to_different_activities_allowed(self, client, reset_activities, sample_new_email):
        """
        Test that a student can signup for multiple different activities.
        
        AAA Pattern:
        - Arrange: Get two different activities
        - Act: Signup same student to both activities
        - Assert: Both signups succeed
        """
        # Arrange: Get list of activities
        activities_response = client.get("/activities")
        activity_names = list(activities_response.json().keys())
        first_activity = activity_names[0]
        second_activity = activity_names[1]

        # Act: Signup to first activity
        response1 = client.post(
            f"/activities/{first_activity}/signup",
            params={"email": sample_new_email}
        )

        # Act: Signup to second activity
        response2 = client.post(
            f"/activities/{second_activity}/signup",
            params={"email": sample_new_email}
        )

        # Assert: Both signups should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert sample_new_email in data[first_activity]["participants"]
        assert sample_new_email in data[second_activity]["participants"]

    def test_activity_response_message_contains_email_and_activity(self, client, reset_activities, sample_activity, sample_new_email):
        """
        Test that signup response includes both email and activity name.
        
        AAA Pattern:
        - Arrange: Prepare signup request
        - Act: POST signup request
        - Assert: Verify response message format
        """
        # Arrange: Signup data ready

        # Act: Send signup request
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_new_email}
        )

        # Assert: Response message includes email and activity
        assert response.status_code == 200
        message = response.json()["message"]
        assert sample_new_email in message
        assert sample_activity in message

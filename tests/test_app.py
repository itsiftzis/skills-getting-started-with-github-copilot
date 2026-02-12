"""
Tests for the Mergington High School API
"""

import pytest


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check that key activities exist
    assert "Basketball" in activities
    assert "Tennis" in activities
    assert "Drama Club" in activities
    
    # Check structure of an activity
    basketball = activities["Basketball"]
    assert "type" in basketball
    assert "description" in basketball
    assert "schedule" in basketball
    assert "max_participants" in basketball
    assert "participants" in basketball
    assert isinstance(basketball["participants"], list)


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    email = "test@mergington.edu"
    activity = "Basketball"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity in result["message"]


def test_signup_duplicate(client):
    """Test that signing up twice fails"""
    email = "test2@mergington.edu"
    activity = "Basketball"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    result = response2.json()
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"]


def test_unregister_from_activity(client):
    """Test unregistering from an activity"""
    email = "test3@mergington.edu"
    activity = "Tennis"
    
    # First signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"]


def test_unregister_not_registered(client):
    """Test unregistering when not registered for the activity"""
    email = "not-registered@mergington.edu"
    activity = "Drama Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unregister_removes_participant(client):
    """Test that unregistering actually removes the participant"""
    email = "test4@mergington.edu"
    activity = "Art Studio"
    
    # Signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Verify participant was added
    response_before = client.get("/activities")
    participants_before = response_before.json()[activity]["participants"]
    assert email in participants_before
    
    # Unregister
    client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    # Verify participant was removed
    response_after = client.get("/activities")
    participants_after = response_after.json()[activity]["participants"]
    assert email not in participants_after


def test_signup_affects_availability(client):
    """Test that signup reduces available spots"""
    email = "test5@mergington.edu"
    activity = "Robotics Club"
    
    # Get initial availability
    response_before = client.get("/activities")
    participants_before = len(response_before.json()[activity]["participants"])
    max_participants = response_before.json()[activity]["max_participants"]
    spots_before = max_participants - participants_before
    
    # Signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Get updated availability
    response_after = client.get("/activities")
    participants_after = len(response_after.json()[activity]["participants"])
    spots_after = max_participants - participants_after
    
    # Spots should decrease by 1
    assert spots_after == spots_before - 1
    assert participants_after == participants_before + 1

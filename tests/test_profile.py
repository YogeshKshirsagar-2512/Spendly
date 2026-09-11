"""
Tests for Profile Page & Account Management (Step 4).
Validates view rendering with hardcoded presentation data,
immediate redirection after login, and update form handling.
"""
import pytest


def test_profile_requires_login(client):
    """Test that unauthenticated visitors attempting to access /profile are redirected to /login."""
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"] in ["/login?next=/profile", "/login?next=%2Fprofile"]


def test_profile_authenticated_view(client):
    """Test that an authenticated user can view their profile with complete hardcoded data."""
    # Authenticate user session
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Nitish Kumar"
        sess["user_email"] = "nitish@example.com"

    response = client.get("/profile")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Check key page elements and headers
    assert "Personal Profile" in html
    assert "Active Member" in html
    assert "NK" in html  # Initials avatar
    assert "Nitish Kumar" in html
    assert "nitish@example.com" in html
    assert "Member since September 2026" in html
    assert "INR (₹)" in html
    assert "+91 98765 43210" in html

    # Check hardcoded financial overview cards
    assert "₹14,250.00" in html  # Total spent
    assert "₹20,750.00" in html  # Monthly budget remaining
    assert "28" in html          # Total transactions count
    assert "6" in html           # Active categories count

    # Check settings form fields
    assert 'name="name"' in html
    assert 'name="email"' in html
    assert 'name="current_password"' in html
    assert 'name="new_password"' in html
    assert 'name="confirm_password"' in html


def test_login_redirects_immediately_to_profile(client):
    """Test that submitting login credentials immediately redirects the user to /profile."""
    # Register a user first
    client.post(
        "/register",
        data={"name": "Aarav Gupta", "email": "aarav@example.com", "password": "password123"},
    )

    # Log in without specifying a next_url
    response = client.post(
        "/login",
        data={"email": "aarav@example.com", "password": "password123"},
        follow_redirects=False,
    )

    # Must redirect immediately to /profile
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"

    # Follow redirect and verify destination is profile
    follow_resp = client.get("/profile")
    assert follow_resp.status_code == 200
    assert "Personal Profile" in follow_resp.get_data(as_text=True)


def test_profile_update_success(client):
    """Test successful update of display name and email via POST /profile/update."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Initial Name"
        sess["user_email"] = "initial@example.com"

    response = client.post(
        "/profile/update",
        data={"name": "Vikram Seth", "email": "vikram@example.com"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"

    # Verify session reflects updated data
    with client.session_transaction() as sess:
        assert sess["user_name"] == "Vikram Seth"
        assert sess["user_email"] == "vikram@example.com"

    # Follow redirect and verify message and new initials
    follow_resp = client.get("/profile")
    html = follow_resp.get_data(as_text=True)
    assert "Profile updated successfully." in html
    assert "VS" in html  # Updated initials avatar


def test_profile_update_missing_fields(client):
    """Test that updating profile with empty name or email triggers warning."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/profile/update",
        data={"name": "", "email": "test@example.com"},
        follow_redirects=True,
    )
    assert "Please provide both name and email." in response.get_data(as_text=True)


def test_profile_update_invalid_email(client):
    """Test that updating profile with malformed email triggers warning."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/profile/update",
        data={"name": "Valid Name", "email": "not-an-email"},
        follow_redirects=True,
    )
    assert "Please enter a valid email address." in response.get_data(as_text=True)


def test_profile_password_success(client):
    """Test successful password update via POST /profile/password."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/profile/password",
        data={
            "current_password": "currentPassword123",
            "new_password": "newSecurePassword456",
            "confirm_password": "newSecurePassword456",
        },
        follow_redirects=True,
    )
    assert "Password updated successfully." in response.get_data(as_text=True)


def test_profile_password_missing_fields(client):
    """Test that submitting password form with missing fields triggers warning."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/profile/password",
        data={"current_password": "", "new_password": "newPassword123", "confirm_password": "newPassword123"},
        follow_redirects=True,
    )
    assert "All password fields are required." in response.get_data(as_text=True)


def test_profile_password_mismatch(client):
    """Test that mismatched new password and confirmation trigger warning."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/profile/password",
        data={
            "current_password": "password123",
            "new_password": "newPassword123",
            "confirm_password": "differingPassword123",
        },
        follow_redirects=True,
    )
    assert "New passwords do not match." in response.get_data(as_text=True)


def test_profile_password_too_short(client):
    """Test that new password shorter than 8 characters is rejected."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/profile/password",
        data={
            "current_password": "password123",
            "new_password": "short",
            "confirm_password": "short",
        },
        follow_redirects=True,
    )
    assert "New password must be at least 8 characters long." in response.get_data(as_text=True)

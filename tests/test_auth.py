from werkzeug.security import check_password_hash


def test_register_page_loads(client):
    """Test that the registration page loads with form elements."""
    response = client.get("/register")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Create your account" in html
    assert 'name="name"' in html
    assert 'name="email"' in html
    assert 'name="password"' in html


def test_register_success(client, db):
    """Test successful user registration flow."""
    response = client.post(
        "/register",
        data={
            "name": "Priya Sharma",
            "email": "priya@example.com",
            "password": "strongPassword123",
        },
        follow_redirects=False,
    )
    # Should redirect to /login
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    # Verify user exists in database
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", ("priya@example.com",)
    ).fetchone()
    assert user is not None
    assert user["name"] == "Priya Sharma"
    assert user["email"] == "priya@example.com"
    # Ensure password is not plain text
    assert user["password_hash"] != "strongPassword123"
    assert check_password_hash(user["password_hash"], "strongPassword123")

    # Following redirect should show success flash message
    follow_resp = client.get("/login")
    assert "Account created successfully! Please sign in." in follow_resp.get_data(as_text=True)


def test_register_duplicate_email(client):
    """Test that duplicate email registration is rejected."""
    # First registration
    client.post(
        "/register",
        data={
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )

    # Attempt to register again with same email (case-insensitive)
    response = client.post(
        "/register",
        data={
            "name": "User Two",
            "email": "DUPLICATE@example.com",
            "password": "password456",
        },
    )
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "An account with this email already exists." in html
    assert 'value="User Two"' in html
    assert 'value="duplicate@example.com"' in html


def test_register_short_password(client):
    """Test that password shorter than 8 characters is rejected."""
    response = client.post(
        "/register",
        data={
            "name": "Aarav Gupta",
            "email": "aarav@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Password must be at least 8 characters long." in html
    assert 'value="Aarav Gupta"' in html


def test_register_missing_fields(client):
    """Test registration with missing or whitespace-only inputs."""
    # Empty name
    res1 = client.post(
        "/register",
        data={"name": "   ", "email": "test@example.com", "password": "password123"},
    )
    assert res1.status_code == 400
    assert "All fields are required." in res1.get_data(as_text=True)

    # Empty email
    res2 = client.post(
        "/register",
        data={"name": "Test User", "email": "   ", "password": "password123"},
    )
    assert res2.status_code == 400
    assert "All fields are required." in res2.get_data(as_text=True)

    # Empty password
    res3 = client.post(
        "/register",
        data={"name": "Test User", "email": "test@example.com", "password": ""},
    )
    assert res3.status_code == 400
    assert "All fields are required." in res3.get_data(as_text=True)


def test_register_invalid_email(client):
    """Test registration with malformed email."""
    response = client.post(
        "/register",
        data={
            "name": "Invalid Email User",
            "email": "not-an-email",
            "password": "validPassword123",
        },
    )
    assert response.status_code == 400
    assert "Please enter a valid email address." in response.get_data(as_text=True)


def test_register_redirect_when_logged_in(client):
    """Test that authenticated users are redirected away from /register."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/register")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

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


# ------------------------------------------------------------------ #
# Login & Session Management Tests (Step 3)                          #
# ------------------------------------------------------------------ #

def test_login_page_loads(client):
    """Test that the login page loads with required form fields."""
    response = client.get("/login")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Welcome back" in html
    assert 'name="email"' in html
    assert 'name="password"' in html


def test_login_success(client):
    """Test successful login sets session and redirects."""
    # Register user
    client.post(
        "/register",
        data={"name": "Karan Johar", "email": "karan@example.com", "password": "password123"},
    )

    # Login
    response = client.post(
        "/login",
        data={"email": "karan@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Verify session values
    with client.session_transaction() as sess:
        assert sess["user_id"] is not None
        assert sess["user_name"] == "Karan Johar"
        assert sess["user_email"] == "karan@example.com"

    # Follow redirect
    follow_resp = client.get("/")
    assert "Welcome back, Karan Johar!" in follow_resp.get_data(as_text=True)


def test_login_invalid_password(client):
    """Test login with incorrect password returns 401."""
    client.post(
        "/register",
        data={"name": "Rohan Mehra", "email": "rohan@example.com", "password": "correctPassword123"},
    )

    response = client.post(
        "/login",
        data={"email": "rohan@example.com", "password": "wrongPassword"},
    )
    assert response.status_code == 401
    html = response.get_data(as_text=True)
    assert "Invalid email address or password." in html
    assert 'value="rohan@example.com"' in html


def test_login_nonexistent_email(client):
    """Test login with non-existent user returns 401 with generic error."""
    response = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "anyPassword123"},
    )
    assert response.status_code == 401
    assert "Invalid email address or password." in response.get_data(as_text=True)


def test_login_missing_fields(client):
    """Test login with missing email or password returns 400."""
    res1 = client.post("/login", data={"email": "", "password": "password123"})
    assert res1.status_code == 400
    assert "Please provide both email and password." in res1.get_data(as_text=True)

    res2 = client.post("/login", data={"email": "user@example.com", "password": ""})
    assert res2.status_code == 400
    assert "Please provide both email and password." in res2.get_data(as_text=True)


def test_login_safe_next_redirect(client):
    """Test login respects safe internal next URL parameter."""
    client.post(
        "/register",
        data={"name": "Ananya Roy", "email": "ananya@example.com", "password": "password123"},
    )

    response = client.post(
        "/login?next=/profile",
        data={"email": "ananya@example.com", "password": "password123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"


def test_login_open_redirect_mitigated(client):
    """Test open redirect vulnerability is mitigated by defaulting to landing page."""
    client.post(
        "/register",
        data={"name": "Safe User", "email": "safe@example.com", "password": "password123"},
    )

    # Malicious external URL
    response = client.post(
        "/login?next=https://malicious-phishing.com",
        data={"email": "safe@example.com", "password": "password123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Protocol-relative URL
    response2 = client.post(
        "/login?next=//malicious-phishing.com",
        data={"email": "safe@example.com", "password": "password123"},
    )
    assert response2.status_code == 302
    assert response2.headers["Location"] == "/"


def test_logout(client):
    """Test logout clears session and redirects to login with flash notice."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Logged In User"

    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    # Verify session cleared
    with client.session_transaction() as sess:
        assert "user_id" not in sess

    # Follow redirect
    follow_resp = client.get("/login")
    assert "You have been signed out." in follow_resp.get_data(as_text=True)


def test_login_required_protection(client):
    """Test accessing protected route without session redirects to login with next param."""
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"] in ["/login?next=/profile", "/login?next=%2Fprofile"]

    # Flash warning visible on login page
    follow_resp = client.get("/login")
    assert "Please sign in to access this page." in follow_resp.get_data(as_text=True)


def test_navbar_rendering_authenticated(client):
    """Test dynamic navbar display for guest vs authenticated states."""
    # Guest view
    guest_resp = client.get("/")
    guest_html = guest_resp.get_data(as_text=True)
    assert "Sign in" in guest_html
    assert "Get started" in guest_html
    assert "Sign out" not in guest_html

    # Authenticated view
    with client.session_transaction() as sess:
        sess["user_id"] = 42
        sess["user_name"] = "Vikram Aditya"

    auth_resp = client.get("/")
    auth_html = auth_resp.get_data(as_text=True)
    assert "Hi, Vikram" in auth_html
    assert "Profile" in auth_html
    assert "Sign out" in auth_html
    assert "Get started" not in auth_html

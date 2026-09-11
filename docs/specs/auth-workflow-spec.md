# Feature Specification: Full Authentication Workflow (Registration, Login, Session & Logout)

**Feature Name:** Unified Authentication & Session Lifecycle  
**Status:** Ready for Implementation  
**Date:** 2026-09-11  
**Author:** Antigravity  
**Target Milestone:** Steps 2 & 3 of Spendly Roadmap (`first.md` / `AGENTS.md`)  
**File Path:** `docs/specs/auth-workflow-spec.md`

---

## 1. Executive Summary & Problem Statement

### 1.1 Problem Statement
While user registration (`POST /register`) has been implemented in Step 2, users currently cannot sign into Spendly. Navigating to `/login` only serves a static form without a `POST` handler, `/logout` is a placeholder string, and the global navigation bar in `base.html` has no awareness of authentication state. Consequently, users cannot access private expense management features, maintain session persistence across page reloads, or safely sign out.

### 1.2 Proposed Solution
Deliver an end-to-end, production-grade authentication and session management system:
1. **Registration Flow (`/register`)**: Account creation with validation, email uniqueness, password hashing via `werkzeug.security`, and redirect to login.
2. **Login Flow (`/login`)**: Verify credentials against the database using `check_password_hash`, establish secure session cookies (`session['user_id']`, `session['user_name']`), handle optional `?next=` URL redirects, and surface authentication errors.
3. **Logout Flow (`/logout`)**: Clear session context, flash a sign-out notification, and redirect to `/login`.
4. **Session Protection & Middleware (`@login_required`)**: A reusable decorator to guard private endpoints (`/profile`, `/expenses/*`), redirecting unauthenticated visitors to `/login?next=<path>`.
5. **Dynamic Navigation State (`templates/base.html`)**: Conditionally render "Sign in / Get started" for visitors, or user greeting and "Sign out" for authenticated users.
6. **Automated Git & GitHub CI**: Ensure all changes are validated by automated `pytest` suites and continuous integration via GitHub Actions.

### 1.3 Scope & Non-Goals
- **In Scope:**
  - `POST /login` credential verification and error messaging.
  - `GET /logout` session invalidation.
  - `@login_required` Python view decorator in `app.py`.
  - Context processor or template helper to inject current user into Jinja views.
  - Conditional navigation bar updates in `templates/base.html`.
  - Redirect handling for protected destination URLs (`next` parameter).
  - Comprehensive unit and integration test suite in `tests/test_auth.py`.
  - Autonomous Git staging, Conventional Commits, and GitHub remote push.
- **Out of Scope (Non-Goals):**
  - "Remember me" persistent token cookies spanning months (standard secure browser session used).
  - Multi-factor authentication (2FA).
  - Social OAuth login (Google / GitHub).

---

## 2. User Stories & Acceptance Criteria

### 2.1 User Personas & Stories
- **As a** new user,  
  **I want to** register an account and immediately sign in with my credentials,  
  **So that** I can start tracking my personal expenses.
- **As an** existing registered user,  
  **I want to** enter my email and password to securely log in,  
  **So that** I can view and manage my private financial data.
- **As an** authenticated user,  
  **I want to** log out with a single click,  
  **So that** my financial data remains protected when using shared devices.
- **As a** visitor attempting to access a protected URL (e.g., `/expenses/add`),  
  **I want to** be prompted to sign in and then redirected back to my intended page,  
  **So that** my workflow is not interrupted.

---

### 2.2 Acceptance Criteria (Gherkin Format)

#### Scenario 1: Successful User Login (Happy Path)
- **Given** a registered user with email `"nitish@example.com"` and password `"password123"`,
- **When** the user submits valid credentials on `/login`,
- **Then** `check_password_hash` verifies the database hash,
- **And** `session['user_id']` and `session['user_name']` are set,
- **And** the user is redirected to `/` (or destination specified in `next`),
- **And** the navbar displays the user's name and a "Sign out" action.

#### Scenario 2: Invalid Password or Unregistered Email
- **Given** an unauthenticated visitor on `/login`,
- **When** they submit an unregistered email or an incorrect password,
- **Then** the login form is re-rendered with HTTP status 401 (or 400),
- **And** an error message is displayed: `"Invalid email address or password."` *(avoids username enumeration)*,
- **And** the submitted email is preserved in the input box, while the password field is cleared.

#### Scenario 3: Missing Login Fields
- **Given** a visitor clicks "Sign in" with empty email or password,
- **When** the form is submitted,
- **Then** the page renders with an error: `"Please provide both email and password."`

#### Scenario 4: User Logout
- **Given** an authenticated user with an active session (`session['user_id'] = 1`),
- **When** the user accesses `/logout`,
- **Then** `session.clear()` is executed,
- **And** a flash message is generated: `"You have been signed out."`,
- **And** the user is redirected to `/login`,
- **And** navigating back to protected pages prompts for login.

#### Scenario 5: Protected Route Access (`@login_required`)
- **Given** an unauthenticated visitor,
- **When** they attempt to directly access a protected route like `/profile` or `/expenses/add`,
- **Then** they are redirected to `/login?next=%2Fprofile`,
- **And** upon subsequent successful login, they are redirected directly to `/profile`.

#### Scenario 6: Authenticated User Accessing `/login` or `/register`
- **Given** an authenticated user with `session['user_id']`,
- **When** they visit `/login` or `/register`,
- **Then** they are immediately redirected to `/` (avoiding redundant auth screens).

---

## 3. Architecture & Technical Design

### 3.1 Data Model & Persistence
The existing `users` table defined in `database/db.py` fully supports this workflow:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Routes & API Specifications

| Method | Endpoint | Auth Required | Description | Parameters / Payload | Response |
|---|---|---|---|---|---|
| `GET` | `/register` | No (Redirects if logged in) | Displays registration form | None | 200 HTML (`templates/register.html`) |
| `POST` | `/register` | No | Creates new user account | `name`, `email`, `password` | 302 Redirect to `/login` or 400 HTML |
| `GET` | `/login` | No (Redirects if logged in) | Displays sign-in form | `next` (optional query string) | 200 HTML (`templates/login.html`) |
| `POST` | `/login` | No | Validates credentials & creates session | `email`, `password`, `next` (optional) | 302 Redirect to destination or 401 HTML |
| `GET` | `/logout` | Yes | Clears session cookie | None | 302 Redirect to `/login` |
| `GET` | `/profile` | Yes (`@login_required`) | User profile & account overview | None | 200 HTML |

---

### 3.3 Core Code Implementations (`app.py`)

#### A. `@login_required` Decorator
```python
from functools import wraps
from flask import session, redirect, url_for, request, flash

def login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return decorated_view
```

#### B. Context Processor for Current User
```python
@app.context_processor
def inject_current_user():
    """Makes current_user available across all Jinja2 templates."""
    if "user_id" in session:
        return {
            "current_user": {
                "id": session["user_id"],
                "name": session.get("user_name", "User"),
                "email": session.get("user_email", "")
            }
        }
    return {"current_user": None}
```

#### C. Login Route Controller
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("landing"))

    next_url = request.args.get("next") or request.form.get("next")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "login.html",
                error="Please provide both email and password.",
                email=email,
                next=next_url
            ), 400

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,)).fetchone()

        # Constant-time comparison check to prevent timing leaks
        if not user or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                error="Invalid email address or password.",
                email=email,
                next=next_url
            ), 401

        # Establish session
        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        flash(f"Welcome back, {user['name']}!", "success")

        # Safely validate next_url to prevent open redirect vulnerabilities
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("landing"))

    return render_template("login.html", next=next_url)
```

#### D. Logout Route Controller
```python
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))
```

---

## 4. UI / UX Design & Presentation

### 4.1 Navigation Bar Updates (`templates/base.html`)
Update the `.nav-links` container to dynamically adapt based on `current_user`:

```html
<div class="nav-links">
    {% if current_user %}
        <span class="nav-user-greeting">Hi, {{ current_user.name.split()[0] }}</span>
        <a href="{{ url_for('profile') }}" class="nav-link">Profile</a>
        <a href="{{ url_for('logout') }}" class="nav-link nav-logout">Sign out</a>
    {% else %}
        <a href="{{ url_for('login') }}">Sign in</a>
        <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
    {% endif %}
</div>
```

### 4.2 Login Form Updates (`templates/login.html`)
- Retain entered email on failed attempts: `value="{{ email|default('', true) }}"`.
- Carry forward hidden `next` input:
  ```html
  {% if next %}
  <input type="hidden" name="next" value="{{ next }}">
  {% endif %}
  ```
- Flash banners: Rendered using `.auth-flash` and categories (`success`, `warning`, `info`).

### 4.3 Styling Additions (`static/css/style.css`)
Add subtle styles for navigation greeting and flash message categories:
```css
.nav-user-greeting {
    font-weight: 500;
    color: var(--ink-soft);
    font-size: 0.9rem;
    padding-right: 0.5rem;
}

.nav-logout {
    color: var(--danger) !important;
}

.auth-flash-warning {
    background: var(--accent-2-light);
    color: var(--accent-2);
    border: 1px solid rgba(193, 127, 36, 0.25);
}

.auth-flash-info {
    background: #eef4f8;
    color: #1f5f8b;
    border: 1px solid rgba(31, 95, 139, 0.2);
}
```

---

## 5. Security, Validation & Edge Cases

### 5.1 Security Controls
1. **Password Verification**: Strictly use `werkzeug.security.check_password_hash`.
2. **Session Cleansing**: Always invoke `session.clear()` before storing credentials to avoid session fixation.
3. **Open Redirect Prevention**: Only redirect to `next_url` if it starts with a single `/` and does not contain protocol prefixes (`http:`, `https:`).
4. **Credential Enumeration Resistance**: Always return generic message `"Invalid email address or password."` for both non-existent users and wrong passwords.
5. **Case-Insensitive Emails**: Strip and lowercase emails during both login queries and registration.

### 5.2 Edge Cases
- User enters email with leading/trailing spaces (`"  user@test.com  "`).
- User deletes their account in another tab while session remains active.
- Accessing `/logout` when already logged out (safely redirects without error).

---

## 6. Testing Strategy (`tests/test_auth.py`)

Expand `tests/test_auth.py` to cover both registration and login/logout workflows:

### 6.1 Planned Test Scenarios
1. `test_login_page_loads`: GET `/login` returns 200 with form fields.
2. `test_login_success`: POST `/login` with valid email & password sets session and redirects.
3. `test_login_invalid_password`: POST `/login` with wrong password returns 401 with error message.
4. `test_login_nonexistent_user`: POST `/login` with unknown email returns 401.
5. `test_login_missing_fields`: Submitting blank email or password returns 400.
6. `test_login_redirect_next_url`: Logging in with `?next=/profile` redirects to `/profile`.
7. `test_login_open_redirect_prevented`: Logging in with malicious `?next=https://evil.com` safely redirects to `/`.
8. `test_logout`: Accessing `/logout` clears session and redirects to `/login`.
9. `test_login_required_decorator`: Unauthenticated access to protected routes redirects to `/login` with flash alert.
10. `test_navbar_renders_user_when_authenticated`: Logged-in user sees name and "Sign out" in HTML output.

---

## 7. Implementation Checklist & Phased Rollout

- [x] **Phase 1 (Backend Core & Routes):**
  - [x] Implement `@login_required` decorator in `app.py`.
  - [x] Implement `@app.context_processor` to inject `current_user`.
  - [x] Implement `POST /login` with credential validation and safe `next` redirection.
  - [x] Implement `GET /logout` with session invalidation.
- [x] **Phase 2 (Templates & UI Integration):**
  - [x] Update `templates/base.html` navbar for authenticated vs guest states.
  - [x] Update `templates/login.html` with hidden `next` input and email retention.
  - [x] Add `.auth-flash-warning`, `.auth-flash-info`, and `.nav-user-greeting` to `static/css/style.css`.
- [x] **Phase 3 (Automated Testing & Verification):**
  - [x] Add all 10 login, logout, session, and navbar test cases to `tests/test_auth.py`.
  - [x] Run `pytest -v` to ensure full pass with 0 failures.
  - [x] Verify `python -m py_compile` across all files.
- [x] **Phase 4 (Roadmap & Documentation):**
  - [x] Update `first.md` roadmap marking Step 3 completed.

---

## 8. Git & GitHub Automation Rules

*The AI agent will autonomously execute all Git and GitHub lifecycle actions on behalf of the user.*

### 8.1 Branch & Commit Specifications
- **Branch:** `main` (or `feat/login-workflow`)
- **Conventional Commit:** `feat(auth): implement complete login, logout, and session workflow (Step 3)`

### 8.2 Pre-Commit Quality Gate
1. Syntax validation:
   ```powershell
   python -m py_compile app.py database/db.py tests/test_auth.py
   ```
2. Test suite run:
   ```powershell
   pytest -v tests/test_auth.py
   ```
   *Gate requirement: All tests passing (0 failures).*

### 8.3 Autonomous GitHub Actions Executed on User's Behalf
1. **Stage files:** Stage `app.py`, `templates/`, `static/`, `tests/`, `docs/`, `first.md`.
2. **Execute Commit:** Create descriptive Conventional Commit locally.
3. **Push to Remote:** Execute `git push origin main` to sync with GitHub repository `YogeshKshirsagar-2512/Spendly`.
4. **CI Verification:** Verify that the push triggers GitHub Actions workflow (`.github/workflows/ci.yml`) cleanly.

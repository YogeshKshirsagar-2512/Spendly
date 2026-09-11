# Feature Specification: User Registration & Password Hashing

**Feature Name:** User Registration & Account Creation  
**Status:** Ready for Implementation  
**Date:** 2026-09-11  
**Author:** Antigravity  
**Target Milestone:** Step 2 of Spendly Roadmap (`first.md` / `AGENTS.md`)  
**File Path:** `docs/specs/user-registration-spec.md`

---

## 1. Executive Summary & Problem Statement

### 1.1 Problem Statement
Currently, Spendly only renders a static GET view for `/register`. Submitting the registration form produces an HTTP `405 Method Not Allowed` error because the POST method handler is not yet implemented. Users cannot create an account to start tracking expenses, and passwords cannot be securely stored.

### 1.2 Proposed Solution
Implement the full user registration lifecycle:
- Support `POST /register` with server-side validation (name presence, valid email format, minimum 8-character password length).
- Enforce unique email constraints at both the database and application levels.
- Hash passwords using `werkzeug.security.generate_password_hash` before database storage.
- Surface contextual error messages within `templates/register.html` using the existing `.auth-error` styling.
- Upon successful registration, redirect to `/login` with a success flash message informing the user they can now sign in.

### 1.3 Scope & Non-Goals
- **In Scope:**
  - `POST` handling on `/register` in `app.py`.
  - Server-side validation and sanitization (strip whitespace, lowercase email).
  - Password hashing with Werkzeug's default recommended method (scrypt / pbkdf2:sha256).
  - Database insertion with parameterized queries into the existing `users` table in `expense_tracker.db`.
  - Duplicate email collision detection and friendly user feedback.
  - Flash/query messaging on successful redirect to `/login`.
  - Comprehensive unit and integration test suite in `tests/test_auth.py`.
- **Out of Scope (Non-Goals):**
  - Email verification links / SMTP email sending (future enhancement).
  - Third-party OAuth (Google, GitHub, etc.).
  - Password recovery / "Forgot Password" flow (scheduled for later milestone).
  - Immediate auto-login into session upon registration (login is explicitly decoupled and implemented in Step 3).

---

## 2. User Stories & Acceptance Criteria

### 2.1 User Personas & Stories
- **As a** new Spendly user,
- **I want to** sign up with my full name, email address, and a secure password,
- **So that** I have a private, secure personal account to track my income and expenses in INR.

### 2.2 Acceptance Criteria (Given - When - Then)

#### Scenario 1: Successful Registration (Happy Path)
- **Given** an unauthenticated visitor is on the `/register` page,
- **When** they fill in valid details ("Nitish Kumar", "nitish@example.com", "SecurePass123!") and click "Create account",
- **Then** a new record is inserted into the `users` table with a hashed password,
- **And** the user is redirected to `/login`,
- **And** a success flash message is displayed: `"Account created successfully! Please sign in."`

#### Scenario 2: Duplicate Email Submission
- **Given** an existing registered user with email `"nitish@example.com"`,
- **When** a visitor attempts to register with the same email `"nitish@example.com"`,
- **Then** no new database record is created,
- **And** the `/register` template is re-rendered with HTTP status 400 (or 200 with error feedback),
- **And** the error banner displays: `"An account with this email already exists."`,
- **And** the `name` and `email` fields retain the submitted values so the user does not have to retype them.

#### Scenario 3: Short or Weak Password
- **Given** a visitor fills in their name and email,
- **When** they submit a password shorter than 8 characters (e.g. `"12345"`),
- **Then** the form rejects submission,
- **And** the error banner displays: `"Password must be at least 8 characters long."`,
- **And** the password input is cleared for security.

#### Scenario 4: Missing or Whitespace-Only Fields
- **Given** a visitor submits empty or whitespace-only values for name, email, or password,
- **When** the form is submitted,
- **Then** the error banner displays: `"All fields are required."`

---

## 3. Architecture & Technical Design

### 3.1 Data Model & Persistence
The database table `users` is already defined in `database/db.py` as:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Query Implementation Pattern:**
```python
# Check for existing email (case-insensitive)
db.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,)).fetchone()

# Insert new user record
db.execute(
    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
    (name, email, password_hash)
)
db.commit()
```

### 3.2 Routes & API Endpoints

| Method | Endpoint | Auth Required | Description | Request Payload / Params | Response |
|---|---|---|---|---|---|
| `GET` | `/register` | No | Render registration form | None | 200 HTML (`templates/register.html`) |
| `POST` | `/register` | No | Process account creation | Form data: `name`, `email`, `password` | 302 Redirect to `/login` (Success) or 400 HTML (`templates/register.html` with `error`) |

### 3.3 Controller Logic (`app.py`)

```python
@app.route("/register", methods=["GET", "POST"])
def register():
    # If user is already logged in, redirect them to dashboard
    if "user_id" in session:
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # 1. Validation
        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.", name=name, email=email), 400

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters long.",
                name=name,
                email=email
            ), 400

        # Basic email format check
        if "@" not in email or "." not in email.split("@")[-1]:
            return render_template("register.html", error="Please enter a valid email address.", name=name, email=email), 400

        # 2. Duplicate Check
        db = get_db()
        existing_user = db.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing_user:
            return render_template(
                "register.html",
                error="An account with this email already exists.",
                name=name,
                email=email
            ), 400

        # 3. Secure Hash & Insert
        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        db.commit()

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")
```

---

## 4. UI / UX Design & Presentation

### 4.1 Template Structure & Retained State
In `templates/register.html`:
- Ensure values entered by the user are preserved on validation errors using `value="{{ name|default('', true) }}"` and `value="{{ email|default('', true) }}"`.
- Display `.auth-error` banner when `error` context variable is provided.
- Maintain existing typography tokens (`var(--font-display)` for titles, `var(--font-body)` for inputs) and styling classes (`.auth-section`, `.auth-card`, `.form-input`, `.btn-submit`).

### 4.2 Login Flash Message Integration
In `templates/login.html`:
- Ensure flash messages (e.g. category `"success"`) are rendered above the login card:
```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="auth-flash auth-flash-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

### 4.3 Styling Additions (`static/css/style.css`)
Add flash alert styling that aligns with the existing design tokens:
```css
.auth-flash {
    padding: 0.75rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    margin-bottom: 1.25rem;
    line-height: 1.4;
}

.auth-flash-success {
    background-color: rgba(26, 71, 42, 0.1);
    color: var(--accent);
    border: 1px solid rgba(26, 71, 42, 0.25);
}
```

---

## 5. Security, Validation & Edge Cases

### 5.1 Security Measures
- **Password Storage**: Passwords must **never** be saved in plain text. Always use `werkzeug.security.generate_password_hash`.
- **SQL Injection Prevention**: Parameterized SQLite queries (`?`) for all queries without exception.
- **Email Normalization**: Lowercase and strip email to prevent case-sensitive bypass (`Test@Domain.com` vs `test@domain.com`).
- **Timing / Enumeration Considerations**: Informative feedback without leaking extraneous sensitive infrastructure details.

### 5.2 Edge Cases Handled
- Whitespace inputs: Name or email containing only spaces.
- Very long strings: Handled gracefully by SQLite dynamic typing.
- Database locks or integrity collisions: Captured via SQLite `sqlite3.IntegrityError` fallback.
- User already authenticated: Redirect straight away if active session exists.

---

## 6. Testing Strategy (`tests/test_auth.py`)

Using `pytest` and `pytest-flask` as established in `requirements.txt` and `AGENTS.md`:

### 6.1 Test Scenarios
1. `test_register_page_loads`: `GET /register` returns 200 and contains the registration form.
2. `test_register_success`: `POST /register` with valid credentials redirects to `/login` (302) and user exists in database with hashed password.
3. `test_register_duplicate_email`: Submitting an already registered email returns 400 and does not duplicate the record.
4. `test_register_password_too_short`: Passwords under 8 characters return 400 and display error message.
5. `test_register_missing_fields`: Empty fields return 400 with `"All fields are required."`
6. `test_register_invalid_email`: Submitting malformed email returns 400.
7. `test_password_is_hashed`: Verify that database `password_hash` != raw submitted password and `check_password_hash` succeeds.

---

## 7. Implementation Checklist & Phased Rollout

- [x] **Phase 1 (Route & Backend Logic):**
  - [x] Import `request`, `redirect`, `url_for`, `flash`, `session` in `app.py`.
  - [x] Import `get_db` from `database.db` and `generate_password_hash` from `werkzeug.security`.
  - [x] Update `/register` route to accept `methods=["GET", "POST"]`.
  - [x] Implement input validation, database uniqueness lookup, hashing, and user insert.
- [x] **Phase 2 (Templates & UI Polish):**
  - [x] Update `templates/register.html` to preserve submitted `name` and `email` values on error.
  - [x] Update `templates/login.html` to display Flask flash messages.
  - [x] Add `.auth-flash` and `.auth-flash-success` styles to `static/css/style.css`.
- [x] **Phase 3 (Automated Tests):**
  - [x] Create `tests/conftest.py` with an isolated temporary/in-memory test database fixture.
  - [x] Create `tests/test_auth.py` covering the 7 test scenarios.
  - [x] Run `pytest` to ensure all tests pass cleanly.

---

## 8. Git & GitHub Automation Rules

*The AI agent autonomously executes all Git and GitHub lifecycle actions on behalf of the user.*

### 8.1 Branching Strategy
- **Base Branch:** `main`
- **Target Branch:** `main` (or `feat/user-registration`)

### 8.2 Pre-Commit Verification Gate
1. Syntax validation:
   ```powershell
   python -m py_compile app.py database/db.py tests/conftest.py tests/test_auth.py
   ```
2. Test suite run:
   ```powershell
   pytest -v tests/test_auth.py
   ```
   *Gate requirement: 7/7 tests passing (0 failures).*

### 8.3 Conventional Commits
- **Format:** `feat(auth): implement user registration with password hashing`
- **Commit Details:**
  ```text
  feat(auth): implement user registration with password hashing (Step 2)

  - Add POST /register handler with server-side validation
  - Hash passwords via werkzeug.security before SQLite insertion
  - Retain form inputs on validation errors in register.html
  - Add flash notification rendering in login.html
  - Add pytest suite with 7 test cases in tests/test_auth.py
  - Add GitHub Actions CI workflow in .github/workflows/ci.yml
  ```

### 8.4 Autonomous GitHub Actions Executed on User's Behalf
1. **Stage files:** Stage `app.py`, `database/db.py`, `templates/`, `static/`, `tests/`, `.github/`, `docs/`, `.agents/`, `.gitignore`.
2. **Execute Commit:** Create the commit locally with verified quality gates.
3. **Push to Remote:** Execute `git push origin main` to deploy changes to GitHub repository `YogeshKshirsagar-2512/Spendly`.
4. **CI Trigger:** Trigger and verify GitHub Actions automated test workflow.


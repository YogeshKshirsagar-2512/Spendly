# AGENTS.md — Repository Guide & Coding Instructions

Welcome to the **Spendly** repository. This document serves as the single source of truth for AI agents (Antigravity, Gemini, Claude, etc.) and human contributors working within this codebase. Always consult this document before writing, refactoring, or testing code.

---

## 1. Project Overview & Exact Tech Stack

**Spendly** is a full-stack personal finance and expense tracker built with Python and Flask. The app tracks income, daily expenses, and category metrics in Indian Rupees (**₹ / INR**).

### Exact Tech Stack & Versions

| Layer | Technology | Version | Notes |
|---|---|---|---|
| **Language & Runtime** | Python | `3.13+` | Standard library utilized for SQLite3, hashing utilities, and date handling |
| **Web Framework** | Flask | `3.1.3` | WSGI routing, request context, session management, template rendering |
| **WSGI / Security Utility** | Werkzeug | `3.1.6` | HTTP internals, password hashing (`generate_password_hash`, `check_password_hash`) |
| **Database** | SQLite3 | Built-in | Single-file DB `expense_tracker.db` with `PRAGMA foreign_keys = ON;` and `sqlite3.Row` factory |
| **Templating Engine** | Jinja2 | `3.1.6` | Bundled with Flask; template inheritance extending `templates/base.html` |
| **Testing Framework** | pytest | `8.3.5` | Test suite runner, fixtures, assertions |
| **Flask Test Helpers** | pytest-flask | `1.3.0` | Client fixtures, app context hooks |
| **Frontend Styling** | Vanilla CSS3 | Standard | Custom CSS variables / design tokens (`style.css`, `landing.css`), modern CSS Grid & Flexbox, no CSS frameworks |
| **Typography** | Google Fonts | Web | *DM Serif Display* (headlines/numbers) & *DM Sans* (body/UI) |
| **Frontend Scripting** | Vanilla JS (ES6+) | Standard | `static/js/main.js`, modular, unobtrusive DOM scripting, no bundler/Node toolchain required |

---

## 2. Build, Run, Test & Lint Commands

The project does not require complex compile or build steps. Use Python's built-in tools and `venv`.

### 2.1 Virtual Environment Setup

**Windows PowerShell:**
```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

**macOS / Linux / Bash:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.2 Dependency Installation
```powershell
pip install -r requirements.txt
```

### 2.3 Running the Application

**Direct Python Execution:**
```powershell
python app.py
```
* The development server starts at: `http://127.0.0.1:5001` (configured with `port=5001`, `debug=True`).

**Via Flask CLI:**
```powershell
$env:FLASK_APP = "app.py"
$env:FLASK_DEBUG = "1"
flask run -p 5001
```

### 2.4 Database Initialization
```powershell
python -c "from database.db import init_db, seed_db; init_db(); seed_db()"
```

### 2.5 Testing Commands

Tests are authored with `pytest` and `pytest-flask`:
```powershell
# Run the entire test suite
pytest

# Run tests with verbose output
pytest -v

# Run tests showing standard output / print statements
pytest -s

# Run a specific test file or directory
pytest tests/
pytest tests/test_auth.py
```

### 2.6 Linting & Formatting Commands
When running quality checks or formatting, follow PEP 8 standards:
```powershell
# Check code with flake8 (if installed)
flake8 app.py database/

# Format code with black (if installed)
black app.py database/

# Quick syntax verification
python -m py_compile app.py database/*.py
```

---

## 3. Directory Architecture Overview

```text
expense-tracker/
├── app.py                      # Core Flask application, route controllers, session handling
├── requirements.txt            # Pinned dependencies (Flask, Werkzeug, pytest, pytest-flask)
├── .gitignore                  # Excluded patterns (venv, database files, __pycache__, .env)
├── first.md                    # Project roadmap and student guide
├── AGENTS.md                   # AI Agent and developer guidelines (this file)
│
├── database/                   # Database access & persistence layer
│   ├── __init__.py             # Marks database as a Python package
│   └── db.py                   # DB connection provider, schema definitions & seed routines
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout (Head, Navbar, Flash messages, Footer)
│   ├── landing.html            # Public marketing homepage & hero dashboard preview
│   ├── login.html              # Sign-in form template
│   ├── register.html           # Account creation template
│   ├── terms.html              # Terms and Conditions static page
│   └── privacy.html            # Privacy Policy static page
│
├── static/                     # Frontend static assets
│   ├── css/
│   │   ├── style.css           # Global design tokens, resets, buttons, cards, forms, footer
│   │   └── landing.css         # Landing-page hero visual, mock stats, bar indicators
│   └── js/
│       └── main.js             # Client-side interactions and dynamic UI logic
│
└── venv/                       # Local Python virtual environment (ignored by git)
```

### Architecture Flow

1. **Client Request**: Browser sends HTTP request to Flask routes defined in `app.py`.
2. **Controller Logic**: `app.py` extracts parameters, verifies authentication via Flask `session`, and calls database helper methods in `database/db.py`.
3. **Database Layer**: `database/db.py` uses parameterized SQLite queries (`sqlite3.Row`) to fetch or mutate data in `expense_tracker.db`.
4. **View Presentation**: `app.py` passes data context to Jinja2 templates (`templates/*.html`), which inherit from `templates/base.html` and link to `static/css/style.css` and `static/js/main.js`.
5. **Response**: Flask serves complete server-rendered HTML back to the client.

---

## 4. Core Coding Conventions & Patterns

### 4.1 Python & Flask Guidelines
- **PEP 8 Compliance**: Use 4 spaces for indentation, `snake_case` for functions and variables, and `UPPER_SNAKE_CASE` for constants.
- **Route Naming**:
  - Use lowercase, RESTful URI paths: `/login`, `/register`, `/logout`, `/profile`, `/expenses/add`, `/expenses/<int:id>/edit`, `/expenses/<int:id>/delete`.
  - Always specify HTTP methods explicitly when accepting POST data: `@app.route('/login', methods=['GET', 'POST'])`.
  - Prefer `url_for('function_name')` over hardcoded URLs in both Python redirects and Jinja templates.
- **Session & Security**:
  - Always hash passwords using `werkzeug.security.generate_password_hash(password)` before saving to the database.
  - Always verify passwords using `werkzeug.security.check_password_hash(stored_hash, password)`.
  - Store authenticated user identifiers in `session['user_id']`.
  - Protect private routes by verifying `if 'user_id' not in session:` and redirecting to `url_for('login')` with an appropriate message.
  - Set a secure fallback for `app.secret_key` (load from environment variables when available: `os.environ.get('SECRET_KEY', 'dev-key-change-in-production')`).

### 4.2 Database Conventions (`database/db.py`)
- **Connection Management**:
  - Use Flask's `g` application context to store the active connection per request (`g.db`), closing it with a `@app.teardown_appcontext` hook.
  - Always set `conn.row_factory = sqlite3.Row` so column values can be accessed both by name (`row['email']`) and index.
  - Always enable foreign key constraints on every connection: `conn.execute("PRAGMA foreign_keys = ON;")`.
- **SQL Best Practices**:
  - **Never format or concatenate raw strings into SQL statements.** Always use parameterized queries with `?` placeholders to prevent SQL injection.
  - Schema tables must use `CREATE TABLE IF NOT EXISTS`.
  - Key tables:
    - `users`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `name TEXT NOT NULL`, `email TEXT UNIQUE NOT NULL`, `password_hash TEXT NOT NULL`, `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
    - `expenses`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `user_id INTEGER NOT NULL`, `category TEXT NOT NULL`, `amount REAL NOT NULL`, `date TEXT NOT NULL`, `description TEXT`, `FOREIGN KEY (user_id) REFERENCES users (id)`

### 4.3 Template & Jinja2 Guidelines
- **Inheritance**: All HTML pages must extend `"base.html"`:
  ```html
  {% extends "base.html" %}
  {% block title %}Page Title — Spendly{% endblock %}
  {% block content %}
    <!-- Content goes here -->
  {% endblock %}
  ```
- **Error & Flash Messaging**: Display feedback cards inside templates using the `.auth-error` or flash message container.
- **Currency Presentation**: Always prefix monetary amounts with the Indian Rupee symbol: `₹{{ amount }}` or `₹{{ "%.2f"|format(amount) }}`.

### 4.4 CSS & Frontend Design Tokens
Stick strictly to the design system established in `static/css/style.css`:
- **Colors**:
  - Primary Background: `var(--paper)` (`#f7f6f3`)
  - Warm Alt Background: `var(--paper-warm)` (`#f0ede6`)
  - Card Surfaces: `var(--paper-card)` (`#ffffff`)
  - Typography: `var(--ink)` (`#0f0f0f`), `var(--ink-soft)` (`#2d2d2d`), `var(--ink-muted)` (`#6b6b6b`)
  - Accents: `var(--accent)` (`#1a472a` deep forest green), `var(--accent-2)` (`#c17f24` amber gold)
  - Danger / Deletion: `var(--danger)` (`#c0392b`)
  - Borders: `var(--border)` (`#e4e1da`)
- **Fonts**:
  - Display / Numbers / Headers: `var(--font-display)` (`'DM Serif Display', Georgia, serif`)
  - Body / Form Inputs / UI: `var(--font-body)` (`'DM Sans', system-ui, sans-serif`)
- **Component Classes**: Reuse `.btn-primary`, `.btn-ghost`, `.btn-submit`, `.form-group`, `.form-input`, `.auth-card`, `.mock-card`. Avoid introducing ad-hoc utility classes or inline styles unless dynamically calculated (e.g. progress bar `width: 71%`).

### 4.5 Testing Conventions (`tests/`)
- Organize tests in `tests/` matching functional domains (`test_auth.py`, `test_expenses.py`).
- Implement pytest fixtures in `conftest.py` that configure an in-memory SQLite database (`:memory:`) or temporary database file with isolated test data.
- Ensure all route handlers are covered for both success and error paths (invalid credentials, missing form fields, unauthenticated access redirects).

### 4.6 Git & GitHub Automation Conventions
- **Autonomous Operations**: Agents should autonomously manage the Git lifecycle on behalf of the user when completing features or specs:
  - Run pre-commit quality checks (`pytest` and `py_compile`).
  - Stage only intended files (`git add`), strictly avoiding `.env`, `*.db`, `.pytest_cache/`, or `venv/`.
  - Write Conventional Commits: `feat(...)`, `fix(...)`, `test(...)`, `docs(...)`, `refactor(...)`.
  - Push to the remote repository (`git push origin <branch>`).
- **CI/CD Integration**: Maintain `.github/workflows/ci.yml` so automated tests run on GitHub on every push and pull request.

---

## 5. Development Roadmap Reference

When picking up development tasks, align with the 10-step milestones in `first.md`:
1. **Step 1**: SQLite connection, schema creation, and seed data in `database/db.py`.
2. **Step 2**: User registration route (`/register`) with input validation and password hashing.
3. **Step 3**: User login & session management (`/login`, `/logout`).
4. **Step 4**: User profile view and update endpoint (`/profile`).
5. **Step 5**: Expense listing & monthly total calculations (`/expenses` / dashboard).
6. **Step 6**: Category breakdown analytics (Food, Bills, Transport, Health, Entertainment, etc.).
7. **Step 7**: Expense creation endpoint (`/expenses/add`).
8. **Step 8**: Expense edit endpoint (`/expenses/<id>/edit`).
9. **Step 9**: Expense delete endpoint (`/expenses/<id>/delete`).
10. **Step 10**: Automated unit & integration test suite with `pytest`.

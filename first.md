# Spendly — Project Documentation & Setup Guide

## 1. Project Overview

**Spendly** is a lightweight, full-stack personal finance and expense tracking web application built with Python and Flask. Its goal is to help users track their day-to-day spending (in ₹ / INR), analyze financial patterns across categories, and take control of their personal finances.

### Core Features
- **User Authentication**: User registration, login, session persistence, and secure password hashing.
- **Expense Management (CRUD)**: Log, edit, view, and delete daily expenses with category, date, amount, and description.
- **Visual Analytics**: Monthly totals, category breakdowns (Food, Bills, Transport, Health, etc.), and period filters.
- **Responsive UI**: Polished layout using custom CSS variables, serif display typography, and modern cards.

---

## 2. Tech Stack & Dependencies

All dependencies are defined in `requirements.txt`:

| Package | Version | Purpose |
|---|---|---|
| **Flask** | `3.1.3` | Core WSGI web application framework and routing |
| **Werkzeug** | `3.1.6` | Underlying WSGI utility library, HTTP handling, and password hashing |
| **pytest** | `8.3.5` | Test runner and testing framework |
| **pytest-flask** | `1.3.0` | Pytest fixtures and helpers for testing Flask apps |

### Additional Technologies:
- **Database**: SQLite3 (via Python's standard library `sqlite3`)
- **Templating**: Jinja2 (bundled with Flask)
- **Styling & Client Scripts**: Vanilla CSS3 and JavaScript

---

## 3. Project Structure

```text
expense-tracker/
├── app.py                  # Main Flask application & route controllers
├── requirements.txt        # Project dependencies (Flask, Pytest, etc.)
├── .gitignore              # Ignored files (venv, __pycache__, .db, etc.)
├── first.md                # Project documentation and setup guide
│
├── database/               # Database layer
│   ├── __init__.py         # Makes 'database' an importable package
│   └── db.py               # SQLite connection, schema definition & seed data
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout template (Navbar, Head, Footer)
│   ├── landing.html        # Public homepage & hero section
│   ├── login.html          # User sign-in page
│   └── register.html       # User sign-up page
│
├── static/                 # Static frontend assets
│   ├── css/
│   │   └── style.css       # Design system, theme variables, typography
│   └── js/
│       └── main.js         # Client-side interactivity
│
└── venv/                   # Python virtual environment (local only)
```

---

## 4. Setup & Running Instructions

### Step 1: Create Virtual Environment
```powershell
python -m venv venv
```

### Step 2: Activate the Virtual Environment (Windows PowerShell)
If running scripts is restricted, permit process execution first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```
*(You will see `(venv)` at the beginning of your prompt)*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
```powershell
python app.py
```
* Access the app in your browser at: **http://127.0.0.1:5001**

---

## 5. Git & GitHub Setup

```powershell
# Stage and commit initial codebase
git add .
git commit -m 'ready to build'

# Set primary branch to main
git branch -M main

# Link remote repository & push
git remote add origin https://github.com/YogeshKshirsagar-2512/Spendly.git
git push -u origin main
```

---

## 6. Request Lifecycle & Architecture

```text
User Browser
    │
    ▼ (HTTP Request)
[app.py (Routes)] ──────────► [database/db.py] ──────────► SQLite Database
    │                                                            │
    │ (Data Context)                                             │ (Row Records)
    ▼                                                            │
[templates/*.html] ◄─────────────────────────────────────────────┘
    │ (Combines Jinja2 + static/css/style.css)
    ▼
Rendered HTML response to browser
```

---

## 7. Implementation Roadmap

- [x] Initial UI Templates (Landing, Login, Register, Base layout)
- [x] Styling & Assets setup
- [x] Repository initialized and pushed to GitHub
- [ ] **Step 1:** Database setup in `database/db.py` (`get_db`, `init_db`, `seed_db`)
- [ ] **Step 2:** User registration with password hashing
- [ ] **Step 3:** User login & session management (`/login`, `/logout`)
- [ ] **Step 4:** User profile view (`/profile`)
- [ ] **Step 5:** Expense listing & monthly summary dashboard
- [ ] **Step 6:** Category breakdown calculations
- [ ] **Step 7:** Add new expense endpoint (`/expenses/add`)
- [ ] **Step 8:** Edit expense endpoint (`/expenses/<id>/edit`)
- [ ] **Step 9:** Delete expense endpoint (`/expenses/<id>/delete`)
- [ ] **Step 10:** Automated tests with `pytest` and `pytest-flask`

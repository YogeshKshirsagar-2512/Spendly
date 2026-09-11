# Feature Specification: User Profile Page & Frontend Design System

**Feature Name:** User Profile Page & Frontend Design System  
**Status:** Approved for Implementation  
**Date:** 2026-09-11  
**Author:** Antigravity  
**Target Milestone:** Step 4 of Spendly Roadmap (`first.md` / `AGENTS.md`)  
**File Path:** `docs/specs/profile-page-design-spec.md`

---

## 1. Executive Summary & Problem Statement

### 1.1 Problem Statement
In the current application state, navigating to `/profile` returns a placeholder plain-text string: `"Profile page — coming in Step 4"`. Authenticated users have no dedicated space to view their account metadata, inspect high-level spending summaries, manage their personal details (display name, email), or update their passwords. Furthermore, while Spendly has established a refined editorial design aesthetic on the landing and authentication pages, there is no standardized frontend component pattern for authenticated dashboard views, user profile summaries, or settings forms.

### 1.2 Proposed Solution
Implement an elegant, production-ready **Profile Page** (`templates/profile.html` and route `/profile` in `app.py`) following Spendly's core design system tokens. The profile page serves two key functions:
1. **Account Overview & Activity Metrics**: Displays a personalized user header (initials avatar badge, user name, email, member since date) alongside high-level financial summary cards (Total Spent in ₹ INR, Total Transactions Logged, Categories Utilized).
2. **Account Settings & Security Management**: Provides clear, accessible forms to update personal profile details (Name, Email) and change account passwords with current-password verification.
3. **Design System Extension**: Establishes reusable dashboard and profile UI patterns (avatar badges, metric stat cards, settings form cards, section dividers) that seamlessly blend with `templates/base.html` and `static/css/style.css`.

### 1.3 Scope & Non-Goals
- **In Scope:**
  - `GET /profile`: Fetch user details from `users` and aggregated expense statistics from `expenses` to render `templates/profile.html`.
  - `POST /profile/update`: Validate and persist name and email changes (with email uniqueness protection).
  - `POST /profile/password`: Validate current password via `check_password_hash`, verify new password complexity and confirmation match, and persist hash via `generate_password_hash`.
  - Frontend UI components: Initials avatar badge, financial metric stat cards, form sections with `.auth-flash` notifications, responsive multi-column layout.
  - Comprehensive automated test suite in `tests/test_profile.py`.
- **Out of Scope (Non-Goals):**
  - Profile image / photo file uploads (Initials-based dynamic avatar badge used to maintain zero third-party cloud storage dependencies).
  - Multi-currency switching (Spendly is strictly anchored to Indian Rupees ₹ / INR).
  - Two-factor authentication (2FA) / SMS verification.

---

## 2. User Stories & Acceptance Criteria

### 2.1 User Personas & Stories
- **As an** authenticated user,  
  **I want to** navigate to `/profile` from the top navigation bar,  
  **So that** I can see my account details and an instant overview of my financial activity.
- **As an** active user,  
  **I want to** update my display name and email address,  
  **So that** my account information remains accurate and up-to-date.
- **As a** security-conscious user,  
  **I want to** change my password by verifying my existing password first,  
  **So that** my account remains secure against unauthorized access.
- **As an** unauthenticated visitor,  
  **I want to** be redirected to login when trying to access `/profile`,  
  **So that** private account data is never exposed to guests.

---

### 2.2 Acceptance Criteria (Gherkin Scenarios)

#### Scenario 1: Viewing Profile Dashboard (Authenticated)
- **Given** an authenticated user with `session['user_id'] = 1`,
- **When** the user sends a `GET` request to `/profile`,
- **Then** the page renders `templates/profile.html` with HTTP 200,
- **And** the user's name, email, and joined date are displayed,
- **And** an avatar badge with the user's initials is rendered,
- **And** the summary metric cards display Total Expenditure (e.g. `₹14,250.00`), Total Expenses count, and Categories count.

#### Scenario 2: Successfully Updating Name and Email
- **Given** an authenticated user on `/profile`,
- **When** they submit the profile form with a new name `"Nitish Sharma"` and email `"nitish.sharma@example.com"`,
- **Then** the database `users` record is updated,
- **And** `session['user_name']` is updated to `"Nitish Sharma"`,
- **And** the user is redirected to `/profile` with a success flash message: `"Profile updated successfully."`.

#### Scenario 3: Updating Email with Existing Duplicate
- **Given** another user already exists with email `"existing@example.com"`,
- **When** the current user attempts to change their email to `"existing@example.com"`,
- **Then** the update is rejected without database corruption,
- **And** a flash error is displayed: `"This email address is already in use by another account."`,
- **And** the profile page is re-rendered with status 400.

#### Scenario 4: Changing Password Successfully
- **Given** an authenticated user whose current password is `"password123"`,
- **When** the user submits the password form with:
  - `current_password`: `"password123"`,
  - `new_password`: `"newsecret456"`,
  - `confirm_password`: `"newsecret456"`,
- **Then** `check_password_hash` verifies the current password,
- **And** `password_hash` is updated with `generate_password_hash("newsecret456")`,
- **And** a success flash message is displayed: `"Password updated successfully."`.

#### Scenario 5: Changing Password with Incorrect Current Password
- **Given** an authenticated user,
- **When** they submit the password form with an invalid `current_password`,
- **Then** no database update occurs,
- **And** an error flash message is displayed: `"Current password does not match."`.

#### Scenario 6: Password Confirmation Mismatch or Too Short
- **Given** an authenticated user,
- **When** `new_password` does not match `confirm_password` or is less than 6 characters,
- **Then** an error flash message is displayed: `"New passwords do not match or are too short (minimum 6 characters)."`.

#### Scenario 7: Unauthenticated Access Guard
- **Given** a visitor with no active session,
- **When** they attempt to access `/profile` or any `POST` profile endpoint,
- **Then** `@login_required` redirects them to `/login?next=%2Fprofile`.

---

## 3. Architecture & Technical Design

### 3.1 Data Model & Persistence
No schema migrations are strictly required as `users` and `expenses` tables are already established in `database/db.py`:

```sql
-- Existing users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Existing expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

#### Analytical Queries for Profile Overview:
```sql
-- 1. Fetch user record
SELECT id, name, email, created_at FROM users WHERE id = ?;

-- 2. Aggregate expenditure metrics
SELECT 
    COUNT(id) AS total_count,
    COALESCE(SUM(amount), 0.0) AS total_spent,
    COUNT(DISTINCT category) AS category_count
FROM expenses
WHERE user_id = ?;
```

### 3.2 Routes & API Endpoints

| Method | Endpoint | Auth Required | Purpose | Payload | Response |
|---|---|---|---|---|---|
| `GET` | `/profile` | Yes (`@login_required`) | Render profile view & financial stats | None | 200 HTML (`profile.html`) |
| `POST` | `/profile/update` | Yes (`@login_required`) | Update display name and email | `name`, `email` | 302 Redirect to `/profile` (or 400 HTML on error) |
| `POST` | `/profile/password` | Yes (`@login_required`) | Update account password | `current_password`, `new_password`, `confirm_password` | 302 Redirect to `/profile` (or 400 HTML on error) |

### 3.3 Controller Logic (`app.py`)
- **`profile()`**:
  - Retrieve `user_id` from `session['user_id']`.
  - Fetch user row and aggregated stats from SQLite.
  - Parse `created_at` timestamp for human-readable display (e.g. `"September 2026"`).
  - Compute user initials for avatar (e.g. `"Nitish Kumar"` → `"NK"`).
  - Render `templates/profile.html` with `user`, `stats`, and `initials`.
- **`update_profile()`**:
  - Validate required fields (`name`, `email`).
  - Check email uniqueness excluding current user:
    `SELECT id FROM users WHERE email = ? AND id != ?`.
  - Update `users SET name = ?, email = ? WHERE id = ?`.
  - Update `session['user_name'] = name`.
  - Flash success message and redirect.
- **`update_password()`**:
  - Validate inputs (`current_password`, `new_password`, `confirm_password`).
  - Verify current password hash with `check_password_hash(user['password_hash'], current_password)`.
  - Verify `new_password == confirm_password` and `len(new_password) >= 6`.
  - Update `users SET password_hash = ? WHERE id = ?`.
  - Flash success message and redirect.

---

## 4. UI / UX Design & Presentation

### 4.1 Visual Hierarchy & Component Wireframe

```text
+-------------------------------------------------------------------------------+
| Spendly Navbar (Brand | Dashboard | Expenses | Profile | Sign out)            |
+-------------------------------------------------------------------------------+
|                                                                               |
|  [PROFILE HERO BANNER]                                                        |
|  +--------+                                                                   |
|  |   NK   |  Nitish Kumar                                                     |
|  | (Avatar|  nitish@example.com  •  Member since September 2026               |
|  +--------+                                                                   |
|                                                                               |
|  [FINANCIAL METRICS GRID]                                                     |
|  +---------------------+  +---------------------+  +---------------------+    |
|  | TOTAL SPENT         |  | TRANSACTIONS        |  | CATEGORIES          |    |
|  | ₹14,250.00          |  | 28 entries          |  | 6 active            |    |
|  +---------------------+  +---------------------+  +---------------------+    |
|                                                                               |
|  [TWO-COLUMN SETTINGS GRID]                                                   |
|  +--------------------------------+  +--------------------------------+       |
|  | Personal Information           |  | Security & Password            |       |
|  |                                |  |                                |       |
|  | Full Name: [Nitish Kumar     ] |  | Current Password: [••••••••  ] |       |
|  | Email:     [nitish@example... ] |  | New Password:     [••••••••  ] |       |
|  |                                |  | Confirm Password: [••••••••  ] |       |
|  | [ Save Changes ]               |  | [ Update Password ]            |       |
|  +--------------------------------+  +--------------------------------+       |
|                                                                               |
+-------------------------------------------------------------------------------+
```

### 4.2 Design Tokens & CSS Classes
Adhere strictly to the Spendly styling foundations:
- **Backgrounds**: `var(--paper)` (`#f7f6f3`) for body, `var(--paper-card)` (`#ffffff`) for cards, `var(--paper-warm)` (`#f0ede6`) for subtle panels.
- **Borders & Radii**: `border: 1px solid var(--border)` (`#e4e1da`), `border-radius: var(--radius-md)` (`12px`).
- **Typography**:
  - Headlines, numbers & metric totals: `font-family: var(--font-display)` (`'DM Serif Display', Georgia, serif`).
  - Body text, labels, inputs: `font-family: var(--font-body)` (`'DM Sans', system-ui, sans-serif`).
- **Initials Avatar Badge**:
  - Circular badge: `width: 72px; height: 72px; border-radius: 50%`.
  - Colors: Background `var(--accent-light)` (`#e8f0eb`), text `var(--accent)` (`#1a472a`), font size `1.6rem`, font family `var(--font-display)`.
- **Metric Cards**:
  - Small uppercase label (`var(--ink-muted)`, `letter-spacing: 0.05em`).
  - Stat figure: `var(--font-display)`, font size `1.85rem`, color `var(--ink)`.
- **Buttons**:
  - Primary button: `.btn-primary` with hover transition to `var(--accent)`.
- **Flash Notifications**:
  - Success: `.auth-flash.auth-flash-success`.
  - Error / Validation: `.auth-flash.auth-flash-warning` or `.auth-error`.

### 4.3 Responsive Design
- Desktop (> 900px): 3-column metric cards, 2-column settings forms side by side.
- Tablet & Mobile (< 768px): Single column stacked layout, full-width buttons, responsive avatar sizing.

---

## 5. Security & Edge Case Handling

1. **Authentication Enforcement**: Guarded by `@login_required`. Unauthorized requests are redirected to `/login?next=%2Fprofile`.
2. **Session Hijacking Mitigation**: Password updates immediately overwrite stored hash and require verification of existing password.
3. **Data Isolation**: All database operations query by `session['user_id']`, preventing cross-tenant access.
4. **Email Normalization & Validation**: Email strings are trimmed and lowercased before lookup and update.
5. **Zero State Handling**: If a user has no expenses, metrics gracefully display `₹0.00`, `0 entries`, and `0 active categories`.

---

## 6. Testing Strategy

Author comprehensive unit and integration tests in `tests/test_profile.py`:
- `test_profile_unauthenticated_redirect`: Visiting `/profile` unauthenticated redirects to `/login?next=%2Fprofile`.
- `test_profile_authenticated_view`: Authenticated user views profile page with status 200, user details, and stats.
- `test_profile_update_success`: Valid name and email change updates database and session.
- `test_profile_update_duplicate_email`: Attempting to use another user's email fails with flash error.
- `test_profile_update_invalid_email`: Empty name or malformed email format rejected.
- `test_profile_password_success`: Correct current password allows setting new password; verified with subsequent login.
- `test_profile_password_wrong_current`: Incorrect current password returns error.
- `test_profile_password_mismatch`: Mismatched new password and confirmation rejected.

---

## 7. Implementation Checklist

- [ ] **Phase 1: Profile View Route & Metric Queries (`app.py`)**
  - Implement `GET /profile` with user query and aggregated expense statistics.
- [ ] **Phase 2: Profile Update Handlers (`app.py`)**
  - Implement `POST /profile/update` (name and email changes).
  - Implement `POST /profile/password` (password change with hash check).
- [ ] **Phase 3: Profile Template (`templates/profile.html`)**
  - Extend `templates/base.html` with hero banner, initials avatar, stat cards, and forms.
- [ ] **Phase 4: CSS Styles (`static/css/style.css` / Profile Styles)**
  - Add profile-specific CSS classes (`.profile-hero`, `.profile-avatar`, `.profile-stats-grid`, `.profile-stat-card`).
- [ ] **Phase 5: Automated Test Suite (`tests/test_profile.py`)**
  - Add comprehensive pytest test cases for all scenarios.
- [ ] **Phase 6: Quality Gate & Autonomous Git Workflow**
  - Run `python -m py_compile` and `pytest -v`.
  - Stage files, commit with Conventional Commits, and push to GitHub.

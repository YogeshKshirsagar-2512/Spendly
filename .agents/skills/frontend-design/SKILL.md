---
name: frontend-design
description: >-
  Expert frontend design and UI engineering skill for Spendly. Specializes in crafting responsive, accessible,
  editorial-styled Jinja2 templates, CSS layout components, profile pages, financial metric cards, and design token integration.
---

# Frontend Design Skill for Spendly

Use this skill whenever you are designing, modifying, or implementing frontend user interfaces, templates, and styles within Spendly — particularly for the **Profile Page** (`/profile`), dashboard views, metric widgets, and form interfaces.

This skill ensures strict visual harmony with Spendly's warm editorial aesthetic (*DM Serif Display*, *DM Sans*, forest green accents, paper-toned backgrounds, and ₹ INR monetary formatting).

---

## 1. Design System & Token Foundation

All frontend templates and stylesheets must strictly adhere to the project's CSS variables defined in [static/css/style.css](file:///C:/Users/Samsung/Downloads/expense-tracker/expense-tracker/static/css/style.css):

### 1.1 Color Palette
- **Paper Backgrounds**:
  - Main Canvas: `var(--paper)` (`#f7f6f3`)
  - Warm Panel / Alt Surface: `var(--paper-warm)` (`#f0ede6`)
  - Card & Container Surface: `var(--paper-card)` (`#ffffff`)
- **Typography & Inks**:
  - Primary Ink: `var(--ink)` (`#0f0f0f`) — Main headings and bold text
  - Soft Ink: `var(--ink-soft)` (`#2d2d2d`) — Labels and body copy
  - Muted Ink: `var(--ink-muted)` (`#6b6b6b`) — Subtitles and secondary descriptors
  - Faint Ink: `var(--ink-faint)` (`#a0a0a0`) — Placeholders and footer text
- **Brand Accents**:
  - Forest Green Accent: `var(--accent)` (`#1a472a`) — Primary hover state, brand highlights, active tabs
  - Accent Light: `var(--accent-light)` (`#e8f0eb`) — Badges, avatar backgrounds, subtle pills
  - Warm Amber Accent: `var(--accent-2)` (`#c17f24`) — Secondary highlights, progress bars
  - Accent 2 Light: `var(--accent-2-light)` (`#fdf3e3`) — Warning cards, warm badges
- **Feedback & Danger**:
  - Danger / Delete: `var(--danger)` (`#c0392b`)
  - Danger Light: `var(--danger-light)` (`#fdecea`)
- **Borders & Dividers**:
  - Standard Border: `var(--border)` (`#e4e1da`)
  - Soft Border: `var(--border-soft)` (`#eeebe4`)

### 1.2 Typography
- **Display & Headline Font**: `var(--font-display)` (`'DM Serif Display', Georgia, serif`)
  - Used for: Page titles, hero titles, monetary values (₹), metric counts, card headers.
- **Body & Interface Font**: `var(--font-body)` (`'DM Sans', system-ui, sans-serif`)
  - Used for: Navigation items, form labels, inputs, table rows, button copy, descriptions.

### 1.3 Geometry & Radii
- Small Radius: `var(--radius-sm)` (`6px`) — Form inputs, buttons, badges
- Medium Radius: `var(--radius-md)` (`12px`) — Content cards, settings sections
- Large Radius: `var(--radius-lg)` (`20px`) — Mock visual cards, hero containers

---

## 2. Profile Page Design Blueprint

When implementing or iterating on the **Profile Page** (`templates/profile.html`), apply the following layout architecture:

### 2.1 Component Structure

1. **Page Container**:
   - Class: `.profile-container` (max-width `var(--max-width)` or `960px`, centered with `margin: 2.5rem auto 4rem; padding: 0 2rem`).

2. **Profile Hero Banner (`.profile-hero`)**:
   - An editorial card surface (`var(--paper-card)`) with subtle border (`var(--border)`).
   - **Initials Avatar Badge (`.profile-avatar`)**:
     - Circular dimensions: `72px x 72px` (or `80px x 80px`).
     - Display: Flexbox centering.
     - Background: `var(--accent-light)`, border: `2px solid var(--accent)`.
     - Text: `var(--accent)`, `var(--font-display)`, font-size `1.75rem`, font-weight `600`.
   - **User Identity Details (`.profile-identity`)**:
     - Name: `var(--font-display)`, `2rem`, `color: var(--ink)`.
     - Email & Metadata: `var(--ink-muted)`, `0.95rem`, display with inline bullet separator (`•`).
     - Member Since: Formatted nicely (e.g., `Member since September 2026`).

3. **Financial Summary Metrics Grid (`.profile-metrics-grid`)**:
   - Grid layout: `display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2.5rem;`.
   - Each metric card (`.metric-card`):
     - Background: `var(--paper-card)`, border: `1px solid var(--border)`, border-radius: `var(--radius-md)`, padding: `1.5rem`.
     - Metric Label: `var(--ink-muted)`, uppercase, `0.75rem`, `letter-spacing: 0.06em`, `font-weight: 600`.
     - Metric Value: `var(--font-display)`, `1.85rem`, `color: var(--ink)`.
     - Metric 1: **Total Expenditure** (`₹{{ "%.2f"|format(stats.total_spent) }}`).
     - Metric 2: **Transactions Logged** (`{{ stats.total_count }} entries`).
     - Metric 3: **Active Categories** (`{{ stats.category_count }} categories`).

4. **Settings & Security Grid (`.profile-settings-grid`)**:
   - Grid layout: 2-column layout on desktop (`display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;`).
   - **Card 1: Personal Details Form (`.settings-card`)**:
     - Header: "Personal Information" with subtitle "Update your name and email address".
     - Form action: `{{ url_for('update_profile') }}` via `POST`.
     - Input fields:
       - Name (`name="name"`, value `{{ user.name }}`).
       - Email (`name="email"`, type="email", value `{{ user.email }}`).
     - Action: `<button type="submit" class="btn-primary">Save Changes</button>`.
   - **Card 2: Security & Password Form (`.settings-card`)**:
     - Header: "Security & Password" with subtitle "Ensure your account is using a secure password".
     - Form action: `{{ url_for('update_password') }}` via `POST`.
     - Input fields:
       - Current Password (`name="current_password"`, type="password").
       - New Password (`name="new_password"`, type="password", minlength="6").
       - Confirm Password (`name="confirm_password"`, type="password", minlength="6").
     - Action: `<button type="submit" class="btn-primary">Update Password</button>`.

---

## 3. Frontend Implementation Workflow

Follow this multi-step workflow when executing any frontend design task in Spendly:

```mermaid
flowchart TD
    A[Step 1: Check Spec & Tokens] --> B[Step 2: Template Structure (Jinja2)]
    B --> C[Step 3: Component CSS Styling]
    C --> D[Step 4: Responsive & Mobile Verification]
    D --> E[Step 5: Flash & Feedback Testing]
```

### Step 1: Check Spec & Tokens
- Review the feature specification (e.g. [docs/specs/profile-page-design-spec.md](file:///C:/Users/Samsung/Downloads/expense-tracker/expense-tracker/docs/specs/profile-page-design-spec.md)).
- Confirm that all color, font, and spacing choices map directly to CSS variables in `style.css`.
- Avoid adding third-party styling frameworks (Bootstrap, Tailwind, etc.) — keep vanilla CSS3 clean.

### Step 2: Build Jinja2 Template
- All templates must extend `"base.html"`:
  ```jinja2
  {% extends "base.html" %}
  {% block title %}My Profile — Spendly{% endblock %}
  {% block content %}
    ...
  {% endblock %}
  ```
- Always render flash messages using the standardized flash container:
  ```jinja2
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="auth-flash auth-flash-{{ category }}">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  ```
- Always prefix monetary amounts with the Indian Rupee symbol `₹`:
  `₹{{ "%.2f"|format(stats.total_spent) }}`.

### Step 3: Implement CSS Component Classes
- Add dedicated component classes in `static/css/style.css` (or dedicated stylesheet) under a well-commented section:
  - `.profile-hero`, `.profile-avatar`, `.profile-identity`
  - `.profile-metrics-grid`, `.metric-card`, `.metric-value`, `.metric-label`
  - `.profile-settings-grid`, `.settings-card`
- Use CSS Grid and Flexbox for alignments.
- Apply subtle transitions (`transition: border-color 0.2s, background 0.2s`) on inputs and buttons.

### Step 4: Responsive & Mobile Optimization
- Ensure every grid collapses gracefully:
  - `@media (max-width: 900px)`:
    - `.profile-settings-grid`: collapse to `1fr`.
    - `.profile-metrics-grid`: switch to `repeat(2, 1fr)` or stacked.
  - `@media (max-width: 600px)`:
    - `.profile-hero`: stack avatar above identity details, text center.
    - `.profile-metrics-grid`: switch to `1fr` (stacked cards).
    - Buttons expand to full width (`width: 100%`).

### Step 5: Validation & Accessibility
- Forms must have semantic `<label for="...">` tags matching input `id` attributes.
- Inputs must specify explicit `type="email"`, `type="password"`, and `autocomplete` attributes.
- High-contrast text: Never use low-contrast text for critical numbers or inputs.

---

## 4. Skill Resources

The skill directory includes supporting assets:
- **Design Tokens Reference**: [resources/tokens-reference.md](./resources/tokens-reference.md)
- **Profile HTML Component Wireframe**: [resources/profile-component-wireframe.html](./resources/profile-component-wireframe.html)

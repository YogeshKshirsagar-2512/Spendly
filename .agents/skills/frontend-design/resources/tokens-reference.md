# Spendly Design Tokens & Component Reference

This cheat sheet documents the design tokens, reusable CSS utility classes, and markup patterns for all frontend development in Spendly.

---

## 1. CSS Variables / Tokens

```css
:root {
    /* Palette */
    --ink: #0f0f0f;             /* Primary text & high contrast buttons */
    --ink-soft: #2d2d2d;        /* Body text & labels */
    --ink-muted: #6b6b6b;       /* Secondary notes & hints */
    --ink-faint: #a0a0a0;       /* Form placeholders & muted borders */
    --paper: #f7f6f3;           /* Canvas background */
    --paper-warm: #f0ede6;      /* Subtle hero/features background */
    --paper-card: #ffffff;      /* Surface background for cards & inputs */
    --accent: #1a472a;          /* Forest green accent / primary hover */
    --accent-light: #e8f0eb;    /* Light green tint for badges & avatar */
    --accent-2: #c17f24;        /* Warm amber gold */
    --accent-2-light: #fdf3e3;  /* Warm amber tint */
    --danger: #c0392b;          /* Crimson red for errors & deletion */
    --danger-light: #fdecea;    /* Soft red tint for error cards */
    --border: #e4e1da;          /* Card and section borders */
    --border-soft: #eeebe4;     /* Inner card dividers */

    /* Typography */
    --font-display: 'DM Serif Display', Georgia, serif;
    --font-body: 'DM Sans', system-ui, sans-serif;

    /* Max Widths */
    --max-width: 1200px;
    --auth-width: 440px;

    /* Border Radii */
    --radius-sm: 6px;           /* Buttons & form controls */
    --radius-md: 12px;          /* Standard cards */
    --radius-lg: 20px;          /* Large hero mock containers */
}
```

---

## 2. Buttons

| Class | Appearance | Usage |
|---|---|---|
| `.btn-primary` | Solid ink background, white text, transitions to `--accent` | Primary submission actions ("Save Changes", "Update Password") |
| `.btn-ghost` | Transparent background, border with `--border`, hover `--ink` | Secondary actions ("Cancel", "Back") |
| `.btn-submit` | Full-width button for auth forms | Login / Register buttons |

---

## 3. Flash & Alert Messages

```html
<!-- Flash Messages Container -->
<div class="flash-container">
    <!-- Success Notification -->
    <div class="auth-flash auth-flash-success">
        Profile updated successfully.
    </div>

    <!-- Warning / Error Notification -->
    <div class="auth-flash auth-flash-warning">
        This email address is already in use.
    </div>

    <!-- Critical Error Notification -->
    <div class="auth-error">
        Invalid current password.
    </div>
</div>
```

---

## 4. Form Components

```html
<div class="form-group">
    <label for="display_name">Full Name</label>
    <input type="text" id="display_name" name="name" class="form-input" value="Nitish Kumar" required>
</div>
```

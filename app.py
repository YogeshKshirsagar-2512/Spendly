import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import close_db, get_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
app.teardown_appcontext(close_db)


def login_required(view_func):
    """View decorator ensuring active user session."""
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return decorated_view


@app.context_processor
def inject_current_user():
    """Makes current_user available across all templates."""
    if "user_id" in session:
        return {
            "current_user": {
                "id": session["user_id"],
                "name": session.get("user_name", "User"),
                "email": session.get("user_email", ""),
            }
        }
    return {"current_user": None}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # 1. Validation
        if not name or not email or not password:
            return render_template(
                "register.html",
                error="All fields are required.",
                name=name,
                email=email
            ), 400

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters long.",
                name=name,
                email=email
            ), 400

        if "@" not in email or "." not in email.split("@")[-1]:
            return render_template(
                "register.html",
                error="Please enter a valid email address.",
                name=name,
                email=email
            ), 400

        # 2. Check for duplicate email
        db = get_db()
        existing_user = db.execute(
            "SELECT id FROM users WHERE LOWER(email) = ?", (email,)
        ).fetchone()

        if existing_user:
            return render_template(
                "register.html",
                error="An account with this email already exists.",
                name=name,
                email=email
            ), 400

        # 3. Hash password and persist user
        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        db.commit()

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


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
                next=next_url,
            ), 400

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE LOWER(email) = ?", (email,)
        ).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                error="Invalid email address or password.",
                email=email,
                next=next_url,
            ), 401

        # Establish authenticated session
        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        flash(f"Welcome back, {user['name']}!", "success")

        # Validate next_url to prevent open redirect vulnerabilities
        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)
        return redirect(url_for("landing"))

    return render_template("login.html", next=next_url)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — protected endpoints                           #
# ------------------------------------------------------------------ #

@app.route("/profile")
@login_required
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
@login_required
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
@login_required
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
@login_required
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)

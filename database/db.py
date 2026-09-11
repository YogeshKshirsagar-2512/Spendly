import os
import sqlite3
from flask import g, has_app_context
from werkzeug.security import generate_password_hash

# Path to the single-file SQLite database in the repository root
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db"
)


def get_db(db_path=None):
    """
    Returns an active SQLite database connection with row_factory set to sqlite3.Row
    and foreign key constraints enabled.

    If executed within a Flask application context, the connection is cached on `flask.g`.
    If executed outside Flask (e.g. standalone scripts, seeding), a direct connection is returned.
    """
    target_path = db_path or DATABASE_PATH

    if has_app_context():
        if "db" not in g:
            conn = sqlite3.connect(target_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            g.db = conn
        return g.db

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def close_db(e=None):
    """
    Closes the SQLite database connection associated with the current Flask request context.
    """
    if has_app_context():
        db = g.pop("db", None)
        if db is not None:
            db.close()


def init_db(db_path=None):
    """
    Initializes the database by creating all required tables if they do not already exist.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    if not has_app_context():
        conn.close()


def seed_db(db_path=None):
    """
    Populates the database with initial demo data for local development if not already present.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    # Insert default demo user if not already present
    demo_email = "nitish@example.com"
    cursor.execute("SELECT id FROM users WHERE email = ?", (demo_email,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (
                "Nitish Kumar",
                demo_email,
                generate_password_hash("password123")
            )
        )
        user_id = cursor.lastrowid
    else:
        user_id = user["id"]

    # Check if user already has seeded expenses
    cursor.execute("SELECT COUNT(*) AS count FROM expenses WHERE user_id = ?", (user_id,))
    expense_count = cursor.fetchone()["count"]

    if expense_count == 0:
        sample_expenses = [
            (user_id, "Food", 450.0, "2026-03-01", "Dinner at Punjab Grill"),
            (user_id, "Transport", 120.0, "2026-03-02", "Metro card recharge"),
            (user_id, "Bills", 1850.0, "2026-03-03", "Electricity bill"),
            (user_id, "Health", 720.0, "2026-03-05", "Pharmacy medicines"),
            (user_id, "Entertainment", 950.0, "2026-03-07", "Movie tickets & snacks"),
            (user_id, "Food", 320.0, "2026-03-08", "Weekly grocery staples"),
            (user_id, "Transport", 350.0, "2026-03-10", "Auto rickshaw & cab fare")
        ]

        cursor.executemany(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            sample_expenses
        )

    conn.commit()
    if not has_app_context():
        conn.close()

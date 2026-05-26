import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """Inserts sample data for development if the database is empty."""
    with get_db() as conn:
        # Check if users table already contains data
        user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if user:
            return

        # Insert demo user
        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash)
        )
        user_id = cursor.lastrowid

        # Insert 8 sample expenses across 7 categories
        expenses = [
            (user_id, 12.50, "Food", "2026-05-01", "Lunch at cafe"),
            (user_id, 45.00, "Transport", "2026-05-02", "Fuel refill"),
            (user_id, 120.00, "Bills", "2026-05-03", "Electricity bill"),
            (user_id, 30.00, "Health", "2026-05-05", "Pharmacy"),
            (user_id, 15.00, "Entertainment", "2026-05-07", "Movie ticket"),
            (user_id, 60.00, "Shopping", "2026-05-10", "Grocery store"),
            (user_id, 10.00, "Other", "2026-05-12", "Miscellaneous"),
            (user_id, 25.00, "Food", "2026-05-15", "Dinner out"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

def get_user_by_email(email):
    """Retrieves a user from the database by their email address."""
    with get_db() as conn:
        return conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()

def create_user(name, email, password):
    """Hashes password and inserts a new user into the database."""
    password_hash = generate_password_hash(password)
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid

def get_user_expenses(user_id):
    """Retrieves all expenses for a specific user, ordered by date descending."""
    with get_db() as conn:
        return conn.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ).fetchall()


def get_user_category_totals(user_id):
    """Retrieves total spending per category for a specific user."""
    with get_db() as conn:
        return conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category",
            (user_id,)
        ).fetchall()

def get_user_profile(user_id):
    """Retrieves user profile information."""
    with get_db() as conn:
        return conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

def get_user_stats(user_id):
    """Retrieves summary statistics for a user's expenses."""
    with get_db() as conn:
        return conn.execute(
            "SELECT SUM(amount) as total_spent, COUNT(id) as transaction_count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

def get_top_category(user_id):
    """Retrieves the category with the highest total spend for a user."""
    with get_db() as conn:
        return conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()



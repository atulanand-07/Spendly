from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.db import init_db, seed_db, create_user, get_user_by_email
import sqlite3
from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret-key-123"

# Initialize and seed database
with app.app_context():
    init_db()
    seed_db()


def login_required(f):
    """Decorator to ensure a user is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #


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
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not all([name, email, password, confirm_password]):
            flash("All fields are required", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        try:
            create_user(name, email, password)
            flash("Account created successfully!", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered", "error")
            return render_template("register.html")

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([email, password]):
            flash("Email and password are required", "error")
            return render_template("login.html")

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("landing"))

        flash("Invalid email or password", "error")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    user = {
        "name": "Atul Anand",
        "email": "atul@example.com",
        "member_since": "May 2026"
    }
    stats = {
        "total_spent": "₹12,450.00",
        "transaction_count": 42,
        "top_category": "Food"
    }
    transactions = [
        {"date": "2026-05-21", "description": "Grocery Shopping", "category": "Food", "amount": "₹1,200.00"},
        {"date": "2026-05-20", "description": "Uber Ride", "category": "Transport", "amount": "₹450.00"},
        {"date": "2026-05-19", "description": "Netflix Subscription", "category": "Entertainment", "amount": "₹499.00"},
        {"date": "2026-05-18", "description": "Dinner with friends", "category": "Food", "amount": "₹2,100.00"},
        {"date": "2026-05-17", "description": "Electricity Bill", "category": "Utilities", "amount": "₹3,200.00"},
    ]
    categories = [
        {"name": "Food", "amount": "₹4,500.00", "percentage": 36},
        {"name": "Utilities", "amount": "₹3,200.00", "percentage": 25},
        {"name": "Transport", "amount": "₹2,100.00", "percentage": 17},
        {"name": "Entertainment", "amount": "₹2,650.00", "percentage": 22},
    ]
    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)

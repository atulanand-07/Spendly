from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.db import init_db, seed_db, create_user, get_user_by_email, get_user_expenses, get_user_category_totals, get_user_profile, get_user_stats, get_top_category
import sqlite3
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import datetime, date, timedelta

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
    user_id = session["user_id"]
    active_filter = request.args.get("preset", "all")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    today = date.today()

    def subtract_months(source_date, months):
        month_index = source_date.month - months - 1
        year = source_date.year + month_index // 12
        month = month_index % 12 + 1
        return source_date.replace(year=year, month=month, day=1)

    if active_filter == "month":
        start_date = today.replace(day=1).isoformat()
        next_month = subtract_months(today.replace(day=1), -1)
        end_date = (next_month - timedelta(days=1)).isoformat()
    elif active_filter == "3months":
        start_date = subtract_months(today, 2).isoformat()
        next_month = subtract_months(today.replace(day=1), -1)
        end_date = (next_month - timedelta(days=1)).isoformat()
    elif active_filter == "6months":
        start_date = subtract_months(today, 5).isoformat()
        next_month = subtract_months(today.replace(day=1), -1)
        end_date = (next_month - timedelta(days=1)).isoformat()
    elif active_filter == "custom":
        pass
    elif start_date or end_date:
        active_filter = "custom"
    else:
        active_filter = "all"
        start_date = None
        end_date = None

    # Get user profile
    profile_data = get_user_profile(user_id)
    member_since = "Unknown"
    if profile_data and profile_data["created_at"]:
        try:
            dt = datetime.strptime(profile_data["created_at"], "%Y-%m-%d %H:%M:%S")
            member_since = dt.strftime("%B %Y")
        except ValueError:
            member_since = profile_data["created_at"]

    user = {
        "name": profile_data["name"] if profile_data else "User",
        "email": profile_data["email"] if profile_data else "",
        "member_since": member_since
    }
    # Get user stats
    stats_data = get_user_stats(user_id, start_date, end_date)
    total_spent = stats_data["total_spent"] if stats_data and stats_data["total_spent"] is not None else 0.0

    top_cat_row = get_top_category(user_id, start_date, end_date)
    top_category = top_cat_row["category"] if top_cat_row else "None"

    stats = {
        "total_spent": f"₹{total_spent:,.2f}",
        "transaction_count": stats_data["transaction_count"] if stats_data else 0,
        "top_category": top_category
    }
    transactions = [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": f"₹{row['amount']:,.2f}"
        }
        for row in get_user_expenses(user_id, start_date, end_date)
    ]

    category_data = get_user_category_totals(user_id, start_date, end_date)
    overall_total = sum(row["total"] for row in category_data)

    categories = [
        {
            "name": row["category"],
            "amount": f"₹{row['total']:,.2f}",
            "percentage": int((row["total"] / overall_total * 100)) if overall_total > 0 else 0
        }
        for row in category_data
    ]
    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories, start_date=start_date, end_date=end_date, active_filter=active_filter)


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

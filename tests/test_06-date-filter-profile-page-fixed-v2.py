import pytest
from datetime import date, timedelta
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': 'test_spendly.db',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass', 'confirm_password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

def seed_expense(user_id, amount, category, date_str, description="Test Expense"):
    """Helper to seed a specific expense."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date_str, description)
        )
        conn.commit()

class TestProfileDateFilter:

    def test_profile_auth_guard(self, client):
        """Verify that unauthenticated users are redirected to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_profile_custom_range_filters_data(self, auth_client):
        """Verify custom date range correctly filters transactions and stats."""
        # Get user_id from session
        with auth_client.session_transaction() as sess:
            user_id = sess.get('user_id')

        # Seed data: Jan, Feb, March
        seed_expense(user_id, 100.0, "Food", "2026-01-15")
        seed_expense(user_id, 200.0, "Transport", "2026-02-15")
        seed_expense(user_id, 300.0, "Bills", "2026-03-15")

        # Filter Jan to Feb
        response = auth_client.get('/profile', query_string={'start_date': '2026-01-01', 'end_date': '2026-02-28'})

        assert response.status_code == 200
        # Stats check (100 + 200 = 300)
        assert "₹300.00".encode("utf-8") in response.data
        # Transaction count check (2 items)
        assert b"2" in response.data # Looking for the count in stats
        # Content check
        assert b"Food" in response.data
        assert b"Transport" in response.data
        assert b"Bills" not in response.data

    def test_profile_preset_month_filters_correctly(self, auth_client):
        """Verify 'This Month' preset shows only current month data."""
        with auth_client.session_transaction() as sess:
            user_id = sess.get('user_id')

        today = date.today()
        last_month = today.replace(day=1) - timedelta(days=1)

        seed_expense(user_id, 50.0, "Food", today.isoformat())
        seed_expense(user_id, 100.0, "Bills", last_month.isoformat())

        response = auth_client.get('/profile', query_string={'preset': 'month'})

        assert "₹50.00".encode("utf-8") in response.data
        assert "₹150.00".encode("utf-8") not in response.data # Total should not include last month

    def test_profile_preset_3months_filters_correctly(self, auth_client):
        """Verify 'Last 3 Months' preset covers the correct range."""
        with auth_client.session_transaction() as sess:
            user_id = sess.get('user_id')

        today = date.today()
        # 2 months ago
        two_months_ago = today.replace(day=1) - timedelta(days=60) # Simplified range
        # 5 months ago
        five_months_ago = today.replace(day=1) - timedelta(days=150)

        seed_expense(user_id, 50.0, "Food", today.isoformat())
        seed_expense(user_id, 50.0, "Bills", two_months_ago.isoformat())
        seed_expense(user_id, 50.0, "Other", five_months_ago.isoformat())

        response = auth_client.get('/profile', query_string={'preset': '3months'})

        # Should see the today and 2-month-old expense, not the 5-month-old one
        assert "₹100.00".encode("utf-8") in response.data
        assert b"Other" not in response.data

    def test_profile_custom_range_no_results(self, auth_client):
        """Verify stats and list when no expenses match the date range."""
        with auth_client.session_transaction() as sess:
            user_id = sess.get('user_id')

        seed_expense(user_id, 100.0, "Food", "2025-01-01")

        response = auth_client.get('/profile', query_string={'start_date': '2026-01-01', 'end_date': '2026-01-31'})

        assert response.status_code == 200
        assert "₹0.00".encode("utf-8") in response.data
        assert b"0" in response.data # Transaction count

    def test_profile_ui_persistence(self, auth_client):
        """Verify that date parameters are reflected in the rendered HTML."""
        start = "2026-01-01"
        end = "2026-01-31"
        response = auth_client.get('/profile', query_string={'start_date': start, 'end_date': end})

        assert response.status_code == 200
        # Check if the dates appear in the HTML (usually in value attributes of date inputs)
        assert start.encode() in response.data
        assert end.encode() in response.data

    def test_profile_reset_restores_all_data(self, auth_client):
        """Verify that removing filter parameters restores the full view."""
        with auth_client.session_transaction() as sess:
            user_id = sess.get('user_id')

        seed_expense(user_id, 100.0, "Food", "2026-01-01")
        seed_expense(user_id, 200.0, "Bills", "2026-05-01")

        # 1. Apply filter
        auth_client.get('/profile', query_string={'start_date': '2026-05-01', 'end_date': '2026-05-31'})

        # 2. Reset (get profile without params)
        response = auth_client.get('/profile')

        assert response.status_code == 200
        assert "₹300.00".encode("utf-8") in response.data
        assert b"Food" in response.data
        assert b"Bills" in response.data

    def test_profile_invalid_date_range(self, auth_client):
        """Verify that a start_date > end_date returns no results gracefully."""
        with auth_client.session_transaction() as sess:
            user_id = sess.get('user_id')

        seed_expense(user_id, 100.0, "Food", "2026-01-15")

        response = auth_client.get('/profile', query_string={'start_date': '2026-02-01', 'end_date': '2026-01-01'})

        assert response.status_code == 200
        assert "₹0.00".encode("utf-8") in response.data

import pytest
import os
from app import app as flask_app
from database.db import init_db, get_db
import sqlite3

@pytest.fixture
def app():
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test_spendly.db')
        flask_app.config.update({
            'TESTING': True,
            'DATABASE': db_path,
            'SECRET_KEY': 'test-secret',
            'WTF_CSRF_ENABLED': False,
        })
        with flask_app.app_context():
            init_db()
            # Seed data for testing date filters
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    ("Test User", "test@example.com", "hashed_pass")
                )
                user_id = conn.execute("SELECT id FROM users LIMIT 1").fetchone()[0]

                expenses = [
                    (user_id, 100.0, "Food", "2026-01-01", "Jan expense"),
                    (user_id, 200.0, "Transport", "2026-01-15", "Jan expense 2"),
                    (user_id, 300.0, "Bills", "2026-02-01", "Feb expense"),
                    (user_id, 400.0, "Health", "2026-02-15", "Feb expense 2"),
                    (user_id, 500.0, "Shopping", "2026-03-01", "Mar expense"),
                ]
                conn.executemany(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    expenses
                )
                conn.commit()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    # Manually set session since we didn't implement registration/login in this test
    with client.session_transaction() as session:
        session["user_id"] = 1
    return client

def test_profile_no_filter(auth_client):
    """Verify all data is shown when no filter is applied."""
    response = auth_client.get('/profile')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert "Jan expense" in data
    assert "Mar expense" in data
    # Total spent: 100+200+300+400+500 = 1500
    assert "₹1,500.00" in data

def test_profile_start_date_filter(auth_client):
    """Verify only expenses after start_date are shown."""
    # From 2026-02-01: should see Feb and Mar expenses (300, 400, 500)
    response = auth_client.get('/profile?start_date=2026-02-01')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert "Jan expense" not in data
    assert "Feb expense" in data
    assert "Mar expense" in data
    # Total: 300+400+500 = 1200
    assert "₹1,200.00" in data

def test_profile_end_date_filter(auth_client):
    """Verify only expenses before end_date are shown."""
    # Until 2026-01-31: should see Jan expenses (100, 200)
    response = auth_client.get('/profile?end_date=2026-01-31')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert "Jan expense" in data
    assert "Feb expense" not in data
    # Total: 100+200 = 300
    assert "₹300.00" in data

def test_profile_date_range_filter(auth_client):
    """Verify only expenses within the range are shown."""
    # 2026-01-10 to 2026-02-20: should see Jan 15, Feb 01, Feb 15 (200, 300, 400)
    response = auth_client.get('/profile?start_date=2026-01-10&end_date=2026-02-20')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert "Jan expense" in data # The second one
    assert "Feb expense" in data
    assert "Mar expense" not in data
    # Total: 200+300+400 = 900
    assert "₹900.00" in data

def test_profile_empty_range(auth_client):
    """Verify results when no expenses match the date range."""
    response = auth_client.get('/profile?start_date=2020-01-01&end_date=2020-01-02')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert "₹0.00" in data
    assert "None" in data # Top category

def test_profile_input_persistence(auth_client):
    """Verify that filter dates persist in the UI."""
    response = auth_client.get('/profile?start_date=2026-01-01&end_date=2026-01-31')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert 'value="2026-01-01"' in data
    assert 'value="2026-01-31"' in data

---
# Spec: Date Filter for Profile Page

## Overview
The profile page currently displays all user expenses and aggregate statistics. This feature introduces date filtering, allowing users to analyze their spending habits over specific periods (e.g., "Last 30 Days", "This Month", or a custom range). When a filter is applied, the total spent, transaction count, category breakdown, and transaction list will all update to reflect only the data within the selected time window.

## Depends on
- 05-backend-routes-profile-page

## Routes
No new routes. The existing `/profile` route will be enhanced to accept optional query parameters:
- `GET /profile?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — filters profile data by the specified date range (logged-in).

## Database changes
No database schema changes. The following functions in `database/db.py` will be updated or overloaded to support optional date filtering:
- `get_user_expenses(user_id, start_date=None, end_date=None)`
- `get_user_category_totals(user_id, start_date=None, end_date=None)`
- `get_user_stats(user_id, start_date=None, end_date=None)`
- `get_top_category(user_id, start_date=None, end_date=None)`

## Templates
- **Modify:** `templates/profile.html` — Add a date filter section (dropdown for presets and date inputs for custom ranges) and a "Clear Filter" button.

## Files to change
- `app.py` — Update the `/profile` route to handle date filter parameters from the request.
- `database/db.py` — Update the expense-related functions to incorporate `WHERE date BETWEEN ? AND ?` clauses when date parameters are provided.
- `templates/profile.html` — Implement the filter UI.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] Profile page displays a date filter UI with presets (e.g., All Time, Last 30 Days, This Month) and custom date pickers.
- [ ] Applying a date filter correctly updates the "Total Spent" and "Transaction Count" stats.
- [ ] Applying a date filter correctly updates the "Category Breakdown" (totals and percentages).
- [ ] Applying a date filter correctly updates the "Recent Transactions" list to show only expenses within the range.
- [ ] The filter state is reflected in the URL query parameters.
- [ ] A "Clear Filter" button successfully resets the view to "All Time".
- [ ] All date-filtered queries in `database/db.py` use parameterized inputs to prevent SQL injection.
---

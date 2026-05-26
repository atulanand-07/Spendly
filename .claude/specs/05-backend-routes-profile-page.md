---
# Spec: Backend Routes for Profile Page

## Overview
This feature connects the `/profile` route to the database, replacing hardcoded data with real user and expense information. It involves implementing database helper functions to retrieve user profiles and calculate spending statistics, ensuring the profile page reflects the actual state of the logged-in user's account.

## Depends on
- Step 01: Database setup
- Step 02: Registration
- Step 03: Login + Logout
- Step 04: Profile Page (UI)

## Routes
- `GET /profile` — fetch and render real user data and expense statistics — logged-in only

## Database changes
No database changes.

## Templates
No changes needed.

## Files to change
- `app.py` — update the `profile` view function to use database helpers instead of hardcoded data.
- `database/db.py` — add functions to retrieve user details and calculate expense statistics.

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
- [ ] Visiting `/profile` while logged in displays the correct name and email for the authenticated user.
- [ ] Summary stats (total spent, transaction count, top category) are correctly calculated from the database.
- [ ] The transaction history table displays the user's actual expenses in reverse chronological order.
- [ ] The category breakdown section accurately reflects the user's spending by category.
- [ ] The page handles users with no expenses gracefully (0 totals, empty lists) without crashing.
---

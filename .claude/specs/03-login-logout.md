---
# Spec: Login and Logout

## Overview
This feature implements the authentication flow, allowing users to securely log in to their accounts and log out. This is a critical step in the roadmap as it enables personalized access to the expense tracker, ensuring that users can only see and manage their own expenses.

## Depends on
- 02 Registration
- 01 Database Setup

## Routes
- `GET /login` — Displays the login form — public
- `POST /login` — Validates credentials and starts session — public
- `GET /logout` — Clears the session and redirects to landing — logged-in

## Database changes
No database changes.

## Templates
- **Create:** None
- **Modify:** 
    - `templates/login.html`: Implement the login form and handle flash messages.
    - `templates/base.html`: Add conditional navigation links (e.g., "Login" vs "Logout") based on session status.

## Files to change
- `app.py`
- `templates/login.html`
- `templates/base.html`

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
- [ ] User can navigate to `/login` and see a login form.
- [ ] User can log in with correct email and password; redirected to the landing page or a protected route.
- [ ] User sees an error message ("Invalid email or password") when using wrong credentials.
- [ ] User is redirected to the login page if they try to access a protected route while not logged in.
- [ ] User can click "Logout" and is successfully signed out, redirected to the landing page.
- [ ] Navigation bar correctly toggles between "Login" and "Logout" links based on auth state.
---

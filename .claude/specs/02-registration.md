---
# Spec: Registration

## Overview
Allow new users to create an account by providing their name, email, and password. This is the first step in user onboarding, enabling personal expense tracking.

## Depends on
01-database-setup

## Routes
- `GET /register` — Display registration form — public
- `POST /register` — Handle registration form submission — public

## Database changes
No database changes.

## Templates
- **Modify:** `templates/register.html` — Update the form to use POST and include necessary fields.
- **Modify:** `templates/base.html` — Ensure navigation includes a link to registration.

## Files to change
- `app.py` — Add POST handler for `/register` and implement user creation logic.
- `database/db.py` — Add a `create_user` helper function.
- `templates/register.html` — Implementation of the registration form.
- `templates/base.html` — Navigation updates.

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
- [ ] User can access `/register` and see a registration form.
- [ ] Submitting the form with valid data creates a new record in the `users` table.
- [ ] Passwords are stored as hashes using `werkzeug.security.generate_password_hash`.
- [ ] Registration fails with an error message if the email is already registered.
- [ ] User is redirected to a success page or login page after successful registration.
---

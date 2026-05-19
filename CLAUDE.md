# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands
- Run application: `python app.py`
- Run tests: `pytest`
- Install dependencies: `pip install -r requirements.txt`

## Architecture and Structure
- **Backend**: Flask application (`app.py`) serving as the main entry point and routing layer.
- **Frontend**:
    - **Templates**: Jinja2 templates located in `templates/`, using `base.html` for layout consistency.
    - **Assets**: Static files in `static/css` and `static/js`.
- **Database**: SQLite implementation managed in `database/db.py` (currently in setup phase).
- **Styling**: Vanilla CSS with a custom variable system in `style.css` for colors, fonts, and spacing.

## Development Patterns
- **Routing**: Defined in `app.py` using Flask decorators.
- **Templating**: Use template inheritance (`{% extends "base.html" %}`) and blocks for page-specific content.
- **JavaScript**: Use vanilla JS without external frameworks for frontend interactivity.

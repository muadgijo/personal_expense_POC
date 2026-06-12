# Riafy Expense Manager

A small local expense tracker built with Flask and SQLite.

## What This Is
 Riafy Expense Manager is a simple personal expense tracker for local use. It lets you add, edit, delete, filter, and summarize expenses without any authentication or deployment setup.

## Stack
- Python 3.14
- Flask
- SQLite
- Jinja2 templates
- Vanilla CSS and a little JavaScript

## Why This Stack
- Flask keeps the app small and easy to reason about.
- SQLite is enough for a local single-user tracker and avoids database setup.
- Jinja templates keep the UI simple without a frontend framework.
- Vanilla CSS/JS keeps the app fast to edit and easy to maintain.

## Tradeoffs
- SQLite is not ideal for concurrent multi-user usage, but it is fine for a local POC.
- Money is stored as `REAL`, which is simple, but integer cents would be safer for exact currency math.
- The app is server-rendered, so it is less dynamic than a React or API-driven frontend.
- Validation is intentionally lightweight to keep the project simple.

## How To Run It
From PowerShell in the workspace root:

```powershell
cd C:\projects\personal_expense_POC
.\.venv\Scripts\Activate.ps1
python app.py
```

Or without activating the virtual environment first:

```powershell
cd C:\projects\personal_expense_POC
.\.venv\Scripts\python.exe app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## What Is Done
- Add expense form
- Edit expense form
- Delete expense
- Expense list
- Filters by title, category, and date range
- Monthly summary page
- CSV export
- Light and dark theme toggle
- Local SQLite persistence
- Basic form validation

## What Is Skipped
- Authentication and user accounts, because this is a local POC
- Deployment, because the brief only asked for a local app
- Automated tests, because the focus here was building the working core fast
- API layer, because server-rendered Flask pages were simpler for the scope
- Complex styling system, because the UI is intentionally basic

## Known Rough Edges
- The app uses SQLite `REAL` for amounts, so it is not perfect for exact currency math.
- There is no CSRF protection yet.
- The app is still single-user and local-first.
- The date picker icon can look browser-specific in dark mode.
- Some validation is app-level rather than enforced by database constraints.
- The secret key is hardcoded for convenience and should be moved to an environment variable for anything beyond a demo.

## Project Structure
- `app.py` - Flask app and routes
- `templates/` - Jinja HTML templates
- `static/` - static assets
- `expenses.db` - local SQLite database
- `.venv/` - Python virtual environment

## Notes
- The app is intentionally simple.
- The current product-style name is `Riafy Expense Manager`.

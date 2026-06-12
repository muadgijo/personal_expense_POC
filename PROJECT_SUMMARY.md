# Expense Tracker Project Summary

## What This Project Is
 This is a small Flask-based expense manager built to run locally from the workspace root. It stores expenses in SQLite, lets you add, edit, and delete records, shows a filtered expense list, and provides a monthly summary by category.

## Current Project Structure
- `app.py` - main Flask application and all routes
- `requirements.txt` - Python dependency list
- `.gitignore` - ignores the virtual environment, bytecode, and database file
- `expenses.db` - local SQLite database created on first run
- `templates/` - Jinja templates for the UI
- `static/` - static assets such as CSS
- `.venv/` - local Python virtual environment

## Pages and Behavior
### `/`
Main expense list page.
- Shows all expenses sorted by date descending
- Includes filter controls for title, category, and date range
- Shows edit and delete actions per row
- Shows the total count and total amount in the table footer

### `/add`
Add-expense form.
- Title
- Amount
- Category
- Date
- Note

### `/edit/<id>`
Edit-expense form.
- Loads the selected expense into the same shared form template
- Uses the same validation as add
- Safely handles missing records

### `/delete/<id>`
Deletes an expense after confirming it exists.

### `/summary`
Monthly summary page.
- Displays the current month total
- Shows category breakdown for the current month
- Displays category share percentages

## Validation Rules
The app validates the following before saving:
- Title is required
- Title must be 200 characters or fewer
- Amount must be a valid number
- Amount must be greater than zero
- Amount must not be unrealistically large
- Category must match one of the allowed categories
- Date is required
- Date must be a valid calendar date

## Database Design
The SQLite table is `expenses`.

Columns:
- `id` - primary key
- `title` - expense title
- `amount` - numeric amount
- `category` - allowed category name
- `date` - expense date in `YYYY-MM-DD`
- `note` - optional note
- `created_at` - row creation timestamp

## Template Files
### `templates/base.html`
Shared layout with:
- top navigation
- flash messages
- shared styling
- light and dark theme toggle
- global table, form, and button styles

### `templates/index.html`
Expense list page with:
- filter form
- expense table
- delete confirmation
- footer totals

### `templates/form.html`
Shared add/edit form.
- Works in two modes: add and edit
- Reuses the same markup for both actions

### `templates/summary.html`
Monthly totals and breakdown table.

## Styling Notes
The design is intentionally simple and functional.
- Dark nav with gold accent
- Clean cards and tables
- Theme toggle support
- Date input styling was adjusted so the calendar picker stays visible in both light and dark modes

## How To Run It
From the workspace root:

```powershell
cd C:\projects\personal_expense_POC
.\.venv\Scripts\Activate.ps1
python app.py
```

Or without activating the environment:

```powershell
cd C:\projects\personal_expense_POC
.\.venv\Scripts\python.exe app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Important Workspace Notes
- The project was flattened so the root folder is now the main project folder
- The old nested `expense-tracker/` folder was removed
- The root `app.py` is the real Flask entrypoint
- The app should be opened through Flask on port `5000`, not through Live Server on port `5500`

## Known Good State
The current root app has been syntax-checked successfully and runs from the root virtual environment.

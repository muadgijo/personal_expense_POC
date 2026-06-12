from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import csv
import io
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = 'expense-tracker-secret'

DB_PATH = 'expenses.db'
CATEGORIES = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Other']


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                note        TEXT,
                recurring   INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        ''')
        # Add recurring column if upgrading an existing DB
        try:
            conn.execute('ALTER TABLE expenses ADD COLUMN recurring INTEGER NOT NULL DEFAULT 0')
        except Exception:
            pass
        conn.commit()


def validate_form(form_data):
    errors = []
    title       = form_data.get('title', '').strip()
    amount_raw  = form_data.get('amount', '').strip().replace(',', '')
    category    = form_data.get('category', '').strip()
    expense_date= form_data.get('date', '').strip()
    note        = form_data.get('note', '').strip()
    recurring   = 1 if form_data.get('recurring') else 0

    if not title:
        errors.append('Title is required.')
    elif len(title) > 200:
        errors.append('Title must be under 200 characters.')

    try:
        amount = float(amount_raw)
        if amount <= 0:
            errors.append('Amount must be greater than zero.')
        elif amount > 999999999:
            errors.append('Amount is unrealistically large.')
    except (ValueError, TypeError):
        errors.append('Amount must be a valid number.')

    if category not in CATEGORIES:
        errors.append('Please select a valid category.')

    if not expense_date:
        errors.append('Date is required.')
    else:
        try:
            datetime.strptime(expense_date, '%Y-%m-%d')
        except ValueError:
            errors.append('Date must be a valid calendar date.')

    return errors, title, amount_raw, category, expense_date, note, recurring


@app.route('/')
def index():
    category     = request.args.get('category', '')
    date_from    = request.args.get('date_from', '')
    date_to      = request.args.get('date_to', '')
    title_search = request.args.get('title_search', '')

    query  = 'SELECT * FROM expenses WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)
    if title_search:
        query += ' AND LOWER(title) LIKE LOWER(?)'
        params.append(f'%{title_search}%')

    query += ' ORDER BY date DESC, id DESC'

    with get_db() as conn:
        expenses = conn.execute(query, params).fetchall()

    return render_template('index.html',
                           expenses=expenses,
                           categories=CATEGORIES,
                           filters={
                               'category': category,
                               'date_from': date_from,
                               'date_to': date_to,
                               'title_search': title_search
                           })


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        errors, title, amount_raw, category, expense_date, note, recurring = validate_form(request.form)

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('form.html',
                                   categories=CATEGORIES,
                                   today=date.today().isoformat(),
                                   form_data=request.form,
                                   action='Add')

        with get_db() as conn:
            conn.execute(
                'INSERT INTO expenses (title, amount, category, date, note, recurring) VALUES (?, ?, ?, ?, ?, ?)',
                (title, float(amount_raw), category, expense_date, note if note else None, recurring)
            )
            conn.commit()

        flash('Expense added.', 'success')
        return redirect(url_for('index'))

    return render_template('form.html',
                           categories=CATEGORIES,
                           today=date.today().isoformat(),
                           form_data={},
                           action='Add')


@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    with get_db() as conn:
        row = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()

    if not row:
        flash('Expense not found.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        errors, title, amount_raw, category, expense_date, note, recurring = validate_form(request.form)

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('form.html',
                                   categories=CATEGORIES,
                                   today=date.today().isoformat(),
                                   form_data=request.form,
                                   action='Edit',
                                   expense_id=expense_id)

        with get_db() as conn:
            conn.execute(
                'UPDATE expenses SET title=?, amount=?, category=?, date=?, note=?, recurring=? WHERE id=?',
                (title, float(amount_raw), category, expense_date, note if note else None, recurring, expense_id)
            )
            conn.commit()

        flash('Expense updated.', 'success')
        return redirect(url_for('index'))

    return render_template('form.html',
                           categories=CATEGORIES,
                           today=date.today().isoformat(),
                           form_data=dict(row),
                           action='Edit',
                           expense_id=expense_id)


@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    with get_db() as conn:
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('index'))


@app.route('/summary')
def summary():
    today         = date.today()
    current_month = today.strftime('%Y-%m')
    days_so_far   = today.day

    with get_db() as conn:
        total_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE strftime('%Y-%m', date) = ?",
            (current_month,)
        ).fetchone()

        by_category = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses "
            "WHERE strftime('%Y-%m', date) = ? GROUP BY category ORDER BY total DESC",
            (current_month,)
        ).fetchall()

        highest = conn.execute(
            "SELECT title, amount, category FROM expenses "
            "WHERE strftime('%Y-%m', date) = ? ORDER BY amount DESC LIMIT 1",
            (current_month,)
        ).fetchone()

        expense_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM expenses WHERE strftime('%Y-%m', date) = ?",
            (current_month,)
        ).fetchone()['cnt']

    total        = total_row['total']
    avg_per_day  = total / days_so_far if days_so_far > 0 else 0

    return render_template('summary.html',
                           total=total,
                           by_category=by_category,
                           month_label=today.strftime('%B %Y'),
                           highest=dict(highest) if highest else None,
                           avg_per_day=avg_per_day,
                           expense_count=expense_count,
                           days_so_far=days_so_far)


@app.route('/export')
def export_csv():
    with get_db() as conn:
        expenses = conn.execute(
            'SELECT date, title, category, amount, note, recurring FROM expenses ORDER BY date DESC, id DESC'
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Title', 'Category', 'Amount (INR)', 'Note', 'Recurring'])
    for e in expenses:
        writer.writerow([
            e['date'], e['title'], e['category'],
            f"{e['amount']:.2f}",
            e['note'] or '',
            'Yes' if e['recurring'] else 'No'
        ])

    filename = f"paisa-expenses-{date.today().isoformat()}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
           headers={'Content-Disposition': f'attachment; filename=riafy-expense-manager-{date.today().isoformat()}.csv'}
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

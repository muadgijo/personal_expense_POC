# Senior Engineer Interview Simulator: Expense Tracker Practical

> You are in a 2-hour onsite practical. This is not a theory test.
> You will be evaluated on: requirements reading, decision-making, building, debugging, and communication.
> One task at a time. Justify everything.

---

## How to use this file

Work through each section in order. Write your answers directly below each prompt.
The "Interviewer Notes" blocks are hidden from you during the interview — peek only after you've answered.

---

## The Brief (read once, carefully)

Build a personal expense tracker web app. Users can:

1. **Add** an expense: Title, Amount (local currency), Category (Food / Transport / Shopping / Bills / Entertainment / Other), Date (defaults today), Note (optional)
2. **View** all expenses, sorted by date descending, all fields visible
3. **Edit or delete** any expense
4. **Monthly summary**: total spent + breakdown by category for the current month
5. **Filter** the list by category, date range (from/to), and title (partial text match)

Stack: your choice. Runs locally. No auth, no deployment.
Time: 2 hours.

---

## Round 1 — Before You Write a Single Line

### Q1. Walk me through your approach before touching any code. What's your mental model of this app?

*Your answer:*


---

> **Interviewer follow-up:** You mentioned [your stack choice]. Why that over [the obvious alternative]?
> What are you trading away by choosing it?

*Your answer:*


---

> **Interviewer follow-up:** What's the riskiest part of this build in 2 hours?
> What's the one thing most likely to eat your time?

*Your answer:*


---

<details>
<summary>Interviewer Notes (read after answering)</summary>

**Strong answer looks like:**
- Names a concrete stack immediately, doesn't hedge ("I could do X or Y or Z...")
- Identifies the real time sink: the filter UI + wiring it to the backend is where most candidates lose 30 min
- Recognises the summary is a read-only derived view, not a separate data model
- Mentions the form (add/edit) is shared state — one form, two modes

**Red flags:**
- "I'd spend time thinking about the architecture first" — you have 2 hours, not 2 weeks
- Picking a stack they don't actually know
- Not mentioning validation at all in the first pass
- Treating the monthly summary as a separate complex feature rather than a single GROUP BY query

</details>

---

## Round 2 — Data Model

### Q2. Design your database schema. Tell me every table, every column, every constraint. Don't write code — describe it.

*Your answer:*


---

> **Interviewer follow-up:** You said amount is [your type]. What happens if someone enters `"abc"`, `"-50"`, `"0"`, or `"999999999999"`?
> Where do you catch each of those — client, server, or DB?

*Your answer:*


---

> **Interviewer follow-up:** Do you need more than one table?

*Your answer:*


---

> **Interviewer challenge (curveball):** The requirement says "local currency, no multi-currency."
> A user enters `1,234.50` (comma as thousands separator). What does your system do?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Strong answer:**
- Single table: `expenses(id, title, amount, category, date, note, created_at)`
- `amount` as REAL/DECIMAL — not TEXT, not INTEGER
- `date` as TEXT in ISO format (YYYY-MM-DD) if SQLite, or DATE type if Postgres
- `category` as TEXT with a CHECK constraint OR validated at app layer (both is fine, one is required)
- `note` is nullable
- `created_at` for tiebreaking sort order

**Common mistakes:**
- Storing amount as TEXT — breaks SUM(), comparisons, everything
- No created_at — sort by date alone is non-deterministic for same-day entries
- Forgetting `note` is nullable, then crashing when it's absent
- No constraint on category — garbage data gets in silently

**The comma answer:** Strong candidates say "strip commas before parsing" or "reject and show an error." Weak candidates say "the browser input type=number handles it" — it doesn't, consistently, across locales.

</details>

---

## Round 3 — Prioritisation Under Time Pressure

### Q3. You have 2 hours. Rank these features: Add expense, View list, Edit, Delete, Monthly summary, Filters. What order do you build them in, and what do you cut if time runs short?

*Your answer:*


---

> **Interviewer follow-up:** At the 90-minute mark, filters aren't done.
> Do you keep going or ship what you have? How do you decide?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Strong order:** Add → View → Delete → Edit → Summary → Filters
- Add+View is the core loop. Nothing else matters until data can go in and come back out.
- Delete before Edit — simpler, proves your ID-based routing works
- Summary is a single query, fast to add once the data layer exists
- Filters are the most UI-heavy and the most likely to be cut

**The 90-minute question:** Strong candidates say "I ship what works and document what's missing in the README." They don't say "I'd just quickly finish it" — that's how you blow the 2 hours.

**Red flag:** Building the UI first before any backend works. Lots of AI-assisted developers do this because it looks like progress.

</details>

---

## Round 4 — Validation Strategy

### Q4. List every invalid input a user could submit on the Add Expense form. For each one, where does your app catch it and what does the user see?

*Your answer:*


---

> **Interviewer follow-up:** Your backend returns a 400 with `{"errors": ["Amount must be positive"]}`.
> Walk me through exactly how your frontend handles that response.

*Your answer:*


---

> **Interviewer curveball:** User submits the form twice by double-clicking the submit button.
> What happens? Is that a bug?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Inputs to validate:**
- Title: empty, whitespace-only, >200 chars
- Amount: empty, NaN, zero, negative, over a sane max, comma-formatted
- Category: not in allowed list (even if you use a `<select>` — never trust the client)
- Date: empty, invalid format, future date (requirement doesn't say invalid, but worth noting)
- Note: probably fine as freeform, but max length is reasonable

**The double-submit:** Strong candidates disable the button on first click. Weaker ones say "it would just create a duplicate" and move on. The better answer: disable on submit, re-enable on response. Server-side, it's an idempotency problem — duplicates aren't dangerous here, just annoying, so client-side guard is sufficient.

**The 400 handling:** Red flag if they say "I'd console.log it." They should describe showing the error message near the field or at the top of the form.

</details>

---

## Round 5 — Debugging Under Fire

### Q5. You run the app. The Add Expense form submits but nothing appears in the list. No visible error. What do you do, step by step?

*Your answer:*


---

> **Interviewer follow-up:** You open the Network tab. The POST to `/api/expenses` returns 201.
> The GET to `/api/expenses` returns `[]`. What do you check next?

*Your answer:*


---

> **Interviewer follow-up:** The GET returns data but the list is still empty on screen.
> What's the bug?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Debugging ladder (strong candidate):**
1. Open DevTools Network tab — is the POST even firing?
2. Check the POST response — 201 or error?
3. Is the GET firing after the POST? (Maybe the frontend isn't refreshing the list)
4. Does the GET return data?
5. If yes — is the frontend rendering it? (JS error in console? Wrong property name?)

**The "GET returns data but list is empty" bug:** Almost always one of:
- Rendering the wrong state variable
- Forgetting to call the fetch after successful POST
- Async timing — reading state before it's updated
- Mismatched property name (e.g. backend returns `amount`, frontend reads `price`)

**Red flag:** Jumping to "it must be a database issue" before checking the network. Always check the outermost layer first.

</details>

---

## Round 6 — The Filter Feature

### Q6. Describe exactly how your filter UI works and how it translates to a database query. Be specific about the SQL or equivalent.

*Your answer:*


---

> **Interviewer curveball:** User sets `from = 2024-03-10` and `to = 2024-03-05`. That's a backwards range.
> What does your app do?

*Your answer:*


---

> **Interviewer curveball:** User filters by category "Food" AND title "coffee". Should that return expenses that are Food OR contain "coffee", or Food AND contain "coffee"?

*Your answer:*


---

> **Interviewer follow-up:** No filters are set. User hits "Apply Filters". What SQL runs?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Strong SQL description:**
```sql
SELECT * FROM expenses
WHERE 1=1
  AND (category = ? OR ? IS NULL)
  AND date >= COALESCE(?, '0000-00-00')
  AND date <= COALESCE(?, '9999-99-99')
  AND LOWER(title) LIKE LOWER(?)
ORDER BY date DESC, id DESC
```
Or equivalent dynamic query building.

**Backwards range:** Should either (a) show an error "From date must be before To date" or (b) return empty results silently. Both are defensible — but the candidate must have *thought* about it. "It would just return nothing" without knowing why is a weak answer.

**AND vs OR:** The requirement says filters should combine (AND). If a user filters Food + "coffee" they want Food expenses with "coffee" in the title, not all Food expenses plus all "coffee" expenses. This seems obvious but many candidates miss it.

**No filters:** `WHERE 1=1` with no additional clauses — returns everything. Strong candidates already have this handled by their dynamic query builder.

</details>

---

## Round 7 — The Monthly Summary

### Q7. How does the monthly summary work? What query powers it? What does "current month" mean precisely in your implementation?

*Your answer:*


---

> **Interviewer curveball:** It's 11:58 PM on January 31st. User adds an expense.
> Two minutes later it's February 1st. Which month does the summary show?

*Your answer:*


---

> **Interviewer curveball:** No expenses this month. What does the summary show?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Strong answer:**
- Summary is powered by a single GROUP BY query filtered with `WHERE date LIKE '2024-06-%'` or `strftime('%Y-%m', date) = '2024-06'`
- "Current month" is determined at request time on the server (or client, with clear justification)
- The January 31st question: the expense date is what was submitted — if the user submitted January 31st, it's in January. The summary shows the month based on when the page loads (server time). Strong candidates point out this is a timezone edge case.
- Empty month: summary shows £0.00 total, no category rows — frontend must handle the empty `byCategory` array without crashing

**Red flag:** "I'd use a separate summary table" — massive overengineering, stale data risk, write complexity for zero benefit.

</details>

---

## Round 8 — Changing Requirements

> **Interviewer:** The product team just told you they want to add a **budget per category** feature.
> Users set a monthly budget for each category (e.g. Food: £300/month).
> The summary shows how much of each budget has been used.

### Q8. How does this change your data model? Your API? Your UI? What breaks?

*Your answer:*


---

> **Interviewer follow-up:** You're 75 minutes in. Do you build this now or defer it?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Strong answer:**
- New table: `budgets(id, category TEXT UNIQUE, monthly_amount REAL, updated_at TEXT)`
- The summary query now needs a LEFT JOIN to budgets
- API needs a new endpoint: GET/PUT `/api/budgets`
- UI needs a settings/budget screen or inline editable budget per category row
- Nothing in expenses breaks — it's purely additive

**Defer it:** Yes. 75 minutes in, this is a scope change. Strong candidates say "I'll note it in the README as a known extension point and keep the schema clean enough to add it later." They do NOT start building it.

**Red flag:** "I'd add a budget column to the expenses table." Wrong table — budget is per category per month, not per transaction.

</details>

---

## Round 9 — Code Review

> The interviewer shows you this function. Find every problem.

```python
@app.route('/api/expenses', methods=['POST'])
def create_expense():
    data = request.json
    db.execute(f"INSERT INTO expenses VALUES ('{data['title']}', {data['amount']}, '{data['category']}', '{data['date']}')")
    db.commit()
    return "ok"
```

### Q9. What's wrong with this code? List every issue.

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Issues (in order of severity):**

1. **SQL injection** — f-string with user input directly in SQL. `data['title']` could be `'; DROP TABLE expenses; --`. Critical.
2. **No validation** — any value for amount, category, date goes straight to the DB
3. **`request.json` can be None** — if Content-Type header is wrong, this crashes with `TypeError`
4. **No error handling** — DB failure = 500 with stack trace exposed to client
5. **Wrong return** — returns plain string "ok" not JSON, wrong status code (should be 201)
6. **Column names omitted** — `INSERT INTO expenses VALUES (...)` breaks if column order ever changes
7. **No `created_at`** — not setting the timestamp
8. **`data['amount']` unquoted but also unvalidated** — if it's a string like `"abc"`, this produces invalid SQL

**Strong candidate:** Catches SQL injection immediately as the #1 issue, then works through the rest systematically.

</details>

---

## Round 10 — The README

### Q10. You have 5 minutes left. Write the key sections of your README from memory. What must it contain?

*Your answer:*


---

<details>
<summary>Interviewer Notes</summary>

**Must contain:**
1. **How to run** — exact commands, no ambiguity. `python app.py` alone is not enough if they need to install Flask first.
2. **Stack choices and tradeoffs** — why Flask over Django, why SQLite over Postgres
3. **What's done vs skipped** — honest accounting of unfinished features
4. **Known rough edges** — things that work but imperfectly

**Strong README signal:** "To run: `pip install flask && python app.py` then open `http://localhost:3000`" — zero ambiguity.

**Weak README signal:** Bullet list of technologies with no tradeoff discussion.

</details>

---

## Scoring Rubric

| Area | Weight | What "good" looks like |
|---|---|---|
| Requirements understanding | 15% | Catches all 5 features, notices implicit requirements (sorting, empty states) |
| Prioritisation | 15% | Ships core loop first, defers correctly, doesn't gold-plate |
| Data modelling | 15% | Clean schema, right types, right constraints |
| Validation & error handling | 15% | Both layers, clear user feedback, covers edge cases |
| Debugging ability | 15% | Systematic, starts at the edges, reads actual errors |
| Code quality (when shown code) | 10% | Spots SQL injection, missing error handling |
| Communication | 15% | Justifies tradeoffs, admits uncertainty, asks clarifying questions |

---

## Self-Assessment (fill in after completing the interview)

What did you get right?

What did you miss?

What would you do differently in a real 2-hour session?


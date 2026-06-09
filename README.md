# 💸 SpendSmart – Daily Expense Tracker

A sleek Streamlit app for tracking daily expenses with charts, filters, and user accounts.

## Features
- 🔐 Register & Login (password hashed with SHA-256)
- ➕ Add expenses with category, date, and note
- 📋 Transaction history with filters (category, month, sort)
- 📊 Dashboard with today / monthly / all-time totals
- 📈 Analytics: monthly trend, category breakdown, daily spending
- 💾 Data stored locally in JSON files

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Project Structure
```
expense_tracker/
├── app.py              ← Main Streamlit app
├── requirements.txt    ← Python dependencies
└── data/               ← Auto-created on first run
    ├── users.json      ← User credentials
    ├── names.json      ← Display names
    └── expenses.json   ← All expense records
```

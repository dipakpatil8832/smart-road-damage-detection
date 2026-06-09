import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import hashlib
from datetime import datetime, date

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SpendSmart",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.json")
BALANCES_FILE = os.path.join(DATA_DIR, "balances.json")

os.makedirs(DATA_DIR, exist_ok=True)


CATEGORIES = [
    "🍔 Food & Dining", "🚗 Transport", "🏠 Housing", "💊 Health",
    "🎮 Entertainment", "👗 Shopping", "📚 Education", "✈️ Travel",
    "💡 Utilities", "💰 Savings", "📦 Other"
]

# ── Data helpers ───────────────────────────────────────────────────────────────
def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_users():
    return load_json(USERS_FILE, {})

def save_users(u):
    save_json(USERS_FILE, u)

def get_expenses():
    return load_json(EXPENSES_FILE, [])

def save_expenses(e):
    save_json(EXPENSES_FILE, e)

def get_balances():
    return load_json(BALANCES_FILE, [])

def save_balances(b):
    save_json(BALANCES_FILE, b)

def user_expenses(username):
    return [e for e in get_expenses() if e["user"] == username]

def user_balances(username):
    return [b for b in get_balances() if b["user"] == username]


# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}

/* Main background */
.stApp {
    background: #0d0d14;
    color: #e8e6f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #13131f !important;
    border-right: 1px solid #2a2a3d;
}

/* Cards */
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a45;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #a78bfa;
}
.metric-card .label {
    font-size: 0.8rem;
    color: #8888aa;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

/* Mobile friendly tweaks */
@media (max-width: 640px) {
    .metric-card { padding: 16px !important; }
    .metric-card .value { font-size: 1.35rem !important; }
    .metric-card .label { font-size: 0.7rem !important; }

    /* Reduce font sizes on headings */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.15rem !important; }

    /* Make sidebar content fit better */
    [data-testid="stSidebar"] { padding-top: 0px !important; }
}


/* Form styling */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #1a1a2e !important;
    border: 1px solid #2a2a45 !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.9 !important; }

/* Expense row */
.expense-row {
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.expense-row .amount { color: #f87171; font-weight: 700; font-size: 1.1rem; }
.expense-row .cat { color: #a78bfa; font-size: 0.85rem; }
.expense-row .note { color: #aaa; font-size: 0.85rem; }

/* Auth box */
.auth-box {
    background: #13131f;
    border: 1px solid #2a2a45;
    border-radius: 20px;
    padding: 40px;
    max-width: 440px;
    margin: 0 auto;
}

.logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle { color: #666680; margin-top: -10px; margin-bottom: 30px; }

[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: #888 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #a78bfa !important;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #e8e6f0;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2a2a45;
}
</style>
""", unsafe_allow_html=True)

# ── Auth pages ─────────────────────────────────────────────────────────────────
def show_auth():
    st.markdown('<div style="text-align:center; padding: 40px 0 20px;"><div class="logo-text">💸 SpendSmart</div><p class="subtitle">Your daily expense companion</p></div>', unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        tab1, tab2 = st.tabs(["  Login  ", "  Register  "])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="Enter password")
            if st.button("Login →", key="btn_login"):
                users = get_users()
                if username in users and users[username] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            new_user = st.text_input("Choose Username", key="reg_user", placeholder="e.g. john_doe")
            new_name = st.text_input("Full Name", key="reg_name", placeholder="e.g. John Doe")
            new_pw = st.text_input("Password", type="password", key="reg_pw", placeholder="Min 6 characters")
            new_pw2 = st.text_input("Confirm Password", type="password", key="reg_pw2")
            if st.button("Create Account →", key="btn_reg"):
                users = get_users()
                if not new_user or not new_pw:
                    st.error("Fill all fields.")
                elif new_user in users:
                    st.error("Username already taken.")
                elif len(new_pw) < 6:
                    st.error("Password too short.")
                elif new_pw != new_pw2:
                    st.error("Passwords don't match.")
                else:
                    users[new_user] = hash_pw(new_pw)
                    save_users(users)
                    # Store name separately
                    names = load_json(os.path.join(DATA_DIR, "names.json"), {})
                    names[new_user] = new_name or new_user
                    save_json(os.path.join(DATA_DIR, "names.json"), names)
                    st.success("Account created! Please login.")

# ── Main App ───────────────────────────────────────────────────────────────────
def show_app():
    username = st.session_state.username
    names = load_json(os.path.join(DATA_DIR, "names.json"), {})
    display_name = names.get(username, username)

    # Sidebar
    with st.sidebar:
        st.markdown(f'<div style="font-family:Syne;font-size:1.5rem;font-weight:800;color:#a78bfa;margin-bottom:4px;">💸 SpendSmart</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#666;font-size:0.85rem;margin-bottom:24px;">Hey, <b style="color:#e8e6f0">{display_name}</b> 👋</div>', unsafe_allow_html=True)
        st.divider()
        page = st.radio("Navigate", ["📊 Dashboard", "💰 Add Balance", "➕ Add Expense", "📋 Transactions", "📈 Analytics"], label_visibility="collapsed")
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    expenses = user_expenses(username)
    df = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["user","date","category","amount","note"])

    # ── Dashboard ──────────────────────────────────────────────────────────────
    if page == "📊 Dashboard":
        st.markdown('<h1 style="margin-bottom:4px;">Dashboard</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#666;">Overview for {date.today().strftime("%B %Y")}</p>', unsafe_allow_html=True)

        today = date.today().isoformat()
        month = date.today().strftime("%Y-%m")

        total_all = sum(e["amount"] for e in expenses)
        total_month = sum(e["amount"] for e in expenses if e["date"].startswith(month))
        total_today = sum(e["amount"] for e in expenses if e["date"] == today)
        num_tx = len(expenses)

        balances = user_balances(username)
        total_balance = sum(b["amount"] for b in balances)


        c1, c2, c3, c4, c5 = st.columns(5)
        for col, val, label in [
            (c1, f"₹{total_today:,.0f}", "Today"),
            (c2, f"₹{total_month:,.0f}", "This Month"),
            (c3, f"₹{total_balance:,.0f}", "Total Balance"),
            (c4, f"₹{total_all:,.0f}", "All Time"),
            (c5, str(num_tx), "Transactions"),
        ]:

            with col:
                st.markdown(f'<div class="metric-card"><div class="value">{val}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not df.empty:
            col_l, col_r = st.columns([1, 1])

            with col_l:
                st.markdown('<div class="section-title">Spending by Category</div>', unsafe_allow_html=True)
                cat_df = df.groupby("category")["amount"].sum().reset_index()
                fig = px.pie(cat_df, values="amount", names="category",
                             color_discrete_sequence=px.colors.sequential.Purples_r,
                             hole=0.55)
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e8e6f0", legend=dict(font=dict(size=11)),
                    margin=dict(t=10, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_r:
                st.markdown('<div class="section-title">Recent Transactions</div>', unsafe_allow_html=True)
                recent = sorted(expenses, key=lambda x: x["date"], reverse=True)[:5]
                for e in recent:
                    st.markdown(f"""
                    <div class="expense-row">
                        <div>
                            <div>{e['category']}</div>
                            <div class="note">{e.get('note','—')}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="amount">₹{e['amount']:,.0f}</div>
                            <div class="cat">{e['date']}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("No expenses yet! Add your first expense →")

    # ── Add Balance ────────────────────────────────────────────────────────────
    elif page == "💰 Add Balance":
        st.markdown('<h1>Add Balance</h1>', unsafe_allow_html=True)
        with st.form("add_balance_form"):
            amount = st.number_input("Amount to add (₹)", min_value=0.0, step=1.0, format="%.2f")
            bal_date = st.date_input("Date", value=date.today())
            note = st.text_input("Note (optional)", placeholder="e.g. Salary / top up")
            submitted = st.form_submit_button("Add Balance ✓")

            if submitted:
                if amount <= 0:
                    st.error("Enter a valid amount.")
                else:
                    all_bal = get_balances()
                    all_bal.append({
                        "user": username,
                        "date": str(bal_date),
                        "amount": amount,
                        "note": note,
                    })
                    save_balances(all_bal)
                    st.success(f"Added ₹{amount:,.2f} to your balance!")
                    st.balloons()

    # ── Add Expense ────────────────────────────────────────────────────────────
    elif page == "➕ Add Expense":

        st.markdown('<h1>Add Expense</h1>', unsafe_allow_html=True)
        col, _ = st.columns([1.8, 1])
        with col:
            with st.form("add_expense_form"):
                amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, format="%.2f")
                category = st.selectbox("Category", CATEGORIES)
                exp_date = st.date_input("Date", value=date.today())
                note = st.text_input("Note (optional)", placeholder="e.g. Lunch with friends")
                submitted = st.form_submit_button("Add Expense ✓")
                if submitted:
                    if amount <= 0:
                        st.error("Enter a valid amount.")
                    else:
                        all_exp = get_expenses()
                        all_exp.append({
                            "user": username,
                            "date": str(exp_date),
                            "category": category,
                            "amount": amount,
                            "note": note
                        })
                        save_expenses(all_exp)
                        st.success(f"Added ₹{amount:,.2f} for {category}!")
                        st.balloons()

    # ── Transactions ───────────────────────────────────────────────────────────
    elif page == "📋 Transactions":
        st.markdown('<h1>Transactions</h1>', unsafe_allow_html=True)

        if df.empty:
            st.info("No transactions yet.")
        else:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                cats = ["All"] + sorted(df["category"].unique().tolist())
                sel_cat = st.selectbox("Category", cats)
            with col2:
                months = ["All"] + sorted(df["date"].str[:7].unique().tolist(), reverse=True)
                sel_month = st.selectbox("Month", months)
            with col3:
                sort_by = st.selectbox("Sort by", ["Date (newest)", "Date (oldest)", "Amount (high)", "Amount (low)"])

            filtered = df.copy()
            if sel_cat != "All":
                filtered = filtered[filtered["category"] == sel_cat]
            if sel_month != "All":
                filtered = filtered[filtered["date"].str.startswith(sel_month)]

            sort_map = {
                "Date (newest)": ("date", False),
                "Date (oldest)": ("date", True),
                "Amount (high)": ("amount", False),
                "Amount (low)": ("amount", True),
            }
            col_s, asc_s = sort_map[sort_by]
            filtered = filtered.sort_values(col_s, ascending=asc_s)

            st.markdown(f'<p style="color:#666;margin-bottom:16px;">{len(filtered)} transactions · Total: ₹{filtered["amount"].sum():,.2f}</p>', unsafe_allow_html=True)

            for _, row in filtered.iterrows():
                st.markdown(f"""
                <div class="expense-row">
                    <div>
                        <div style="font-weight:600">{row['category']}</div>
                        <div class="note">{row.get('note','—')}</div>
                    </div>
                    <div style="text-align:right">
                        <div class="amount">₹{row['amount']:,.2f}</div>
                        <div class="cat">{row['date']}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── Analytics ─────────────────────────────────────────────────────────────
    elif page == "📈 Analytics":
        st.markdown('<h1>Analytics</h1>', unsafe_allow_html=True)

        if df.empty:
            st.info("Add some expenses to see analytics.")
        else:
            df["date"] = pd.to_datetime(df["date"])
            df["month"] = df["date"].dt.to_period("M").astype(str)
            df["day"] = df["date"].dt.date

            tab1, tab2, tab3 = st.tabs(["Monthly Trend", "Category Breakdown", "Daily Spending"])

            with tab1:
                monthly = df.groupby("month")["amount"].sum().reset_index()
                fig = px.bar(monthly, x="month", y="amount",
                             color_discrete_sequence=["#7c3aed"],
                             labels={"amount": "Total (₹)", "month": "Month"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="#e8e6f0", xaxis=dict(gridcolor="#2a2a45"),
                                  yaxis=dict(gridcolor="#2a2a45"))
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                cat_df = df.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=True)
                fig = px.bar(cat_df, x="amount", y="category", orientation="h",
                             color="amount", color_continuous_scale="Purples",
                             labels={"amount": "Total (₹)", "category": ""})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="#e8e6f0", xaxis=dict(gridcolor="#2a2a45"),
                                  yaxis=dict(gridcolor="#2a2a45"), showlegend=False,
                                  coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

            with tab3:
                daily = df.groupby("day")["amount"].sum().reset_index()
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily["day"], y=daily["amount"],
                    fill="tozeroy", line=dict(color="#a78bfa", width=2),
                    fillcolor="rgba(124,58,237,0.15)", mode="lines+markers",
                    marker=dict(color="#a78bfa", size=6)
                ))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="#e8e6f0", xaxis=dict(gridcolor="#2a2a45"),
                                  yaxis=dict(gridcolor="#2a2a45", title="Amount (₹)"))
                st.plotly_chart(fig, use_container_width=True)

# ── Session init & routing ─────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    show_auth()
else:
    show_app()

import streamlit as st
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F9FAFB;
        color: #000000;
    }

    button[kind="primary"], .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #9CA3AF !important;
        font-weight: 500;
    }

    input, textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #9CA3AF !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #9CA3AF !important;
    }

    [data-testid="stSuccess"] {
        background-color: #ECFDF5 !important;
        color: #10B981 !important;
    }

    label {
        color: #000000 !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

sa_info = json.loads(st.secrets["google_service_account"]["key"])

creds = Credentials.from_service_account_info(
    sa_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

gc = gspread.authorize(creds)

SHEET_ID = "1QKl7K7jhxoB41pG4GhtFcXQbr4ZPNmN2amgWQfpf0P4"

spreadsheet = gc.open_by_key(SHEET_ID)

txn_ws = spreadsheet.worksheet("Transactions")
heads_ws = spreadsheet.worksheet("Heads")

def indian_greeting():
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    if now.hour < 12:
        return "Good morning"
    elif now.hour < 18:
        return "Good afternoon"
    return "Good evening"

def append_transaction(t_type, main, sub, narration, amount):
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    txn_ws.append_row([
        now.strftime("%Y-%m-%d"),
        t_type,
        main,
        sub,
        narration,
        amount,
        now.strftime("%Y-%m-%d %H:%M:%S")
    ])

data = heads_ws.get_all_values()

types_row = data[0]
main_row = data[1]
sub_rows = data[2:]

heads = {}

for col in range(len(main_row)):
    t = types_row[col].strip()
    main = main_row[col].strip()
    if not t or not main:
        continue

    subs = []
    for r in sub_rows:
        if col < len(r) and r[col].strip():
            subs.append(r[col].strip())

    heads.setdefault(t, {})[main] = subs or ["Other"]

st.title("EM Expense Tracker")
st.subheader(f"{indian_greeting()}, EM 👋")

if "amount_text" not in st.session_state:
    st.session_state.amount_text = ""
if "narration" not in st.session_state:
    st.session_state.narration = ""

t_type = st.selectbox("Type", ["Income", "Expense"], index=1)

main_options = tuple(heads.get(t_type, {}).keys())
main = st.selectbox("Main Head", main_options)

sub_options = tuple(heads[t_type][main])
sub = st.selectbox("Sub Head", sub_options)

narration = st.text_input("Narration (optional)", key="narration")
amount_text = st.text_input("Amount", key="amount_text")

if st.button("Save Transaction"):
    if not amount_text.strip():
        st.warning("Please enter amount")
    else:
        append_transaction(
            t_type,
            main,
            sub,
            narration or "-",
            float(amount_text)
        )
        st.success("Transaction saved!")
        st.session_state.narration = ""
        st.session_state.amount_text = ""

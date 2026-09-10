import streamlit as st
from utils.db_connection import init_db

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")

# Create the SQLite DB + sample data the very first time the app runs
init_db()

st.title("🏏 Cricbuzz LiveStats")
st.subheader("Real-Time Cricket Insights & SQL-Based Analytics")

st.markdown(
    """
Welcome! This dashboard has 4 parts — use the **sidebar on the left** to move
between them:

| Page | What it does |
|---|---|
| 🔴 Live Matches | Pulls live/recent/upcoming matches from the Cricbuzz API |
| 📊 Player Stats | Top run-scorers, wicket-takers, etc. from the API |
| 🧮 SQL Analytics | Run the 25 practice SQL queries on the local database |
| ⚙️ CRUD Operations | Add / update / delete player records in the database |

**Tech stack:** Python · Streamlit · SQLite · Cricbuzz REST API · pandas

**Before you start:** add your Cricbuzz API key to a `.env` file
(see `README.md`) so the Live Matches and Player Stats pages work.
The SQL Analytics and CRUD pages work immediately with sample data —
no API key needed for those.
"""
)

st.info("👈 Pick a page from the sidebar to get started.")

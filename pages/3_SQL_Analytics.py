import streamlit as st
from utils.db_connection import run_query, init_db
from utils.queries import QUERIES
from utils.theme import apply_theme, hero

st.set_page_config(page_title="SQL Analytics", page_icon="🧮", layout="wide")
apply_theme()
init_db()

hero("🧮 SQL Queries & Analytics", "Run the 25 practice queries, or write your own SELECT")

mode = st.radio("Mode", ["Pick a practice question", "Write my own SQL"], horizontal=True)

if mode == "Pick a practice question":
    question = st.selectbox("Choose one of the 25 practice questions", list(QUERIES.keys()))
    sql = QUERIES[question]
    st.code(sql.strip(), language="sql")
    if st.button("▶️ Run query"):
        try:
            df = run_query(sql)
            st.dataframe(df, use_container_width=True)
            st.caption(f"{len(df)} row(s) returned")
        except Exception as e:
            st.error(f"Query failed: {e}")
else:
    sql = st.text_area("Type a SELECT statement", height=150, placeholder="SELECT * FROM players;")
    if st.button("▶️ Run query"):
        if not sql.strip().lower().startswith("select"):
            st.warning("For safety, this box only runs SELECT queries. Use the CRUD page to modify data.")
        else:
            try:
                df = run_query(sql)
                st.dataframe(df, use_container_width=True)
                st.caption(f"{len(df)} row(s) returned")
            except Exception as e:
                st.error(f"Query failed: {e}")

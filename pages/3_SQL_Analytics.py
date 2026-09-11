import streamlit as st
from utils.db_connection import run_query, run_action, init_db
from utils.theme import apply_theme, hero
from utils.queries import QUERIES
apply_theme()

st.set_page_config(page_title="SQL Analytics", page_icon="🧮", layout="wide")
init_db()

st.title("🧮 SQL Queries & Analytics")

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
            if not df.empty:
                st.download_button(
                    "📤 Download as CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    file_name="query_result.csv",
                    mime="text/csv",
                )
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
                if not df.empty:
                    st.download_button(
                        "📤 Download as CSV",
                        df.to_csv(index=False).encode("utf-8"),
                        file_name="query_result.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"Query failed: {e}")
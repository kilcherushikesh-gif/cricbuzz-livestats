import streamlit as st
from utils.db_connection import init_db, run_query
from utils.theme import apply_theme, hero

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")
apply_theme()

init_db()

# ── Hero Banner ──
hero("🏏 Cricbuzz LiveStats", "Real-Time Cricket Insights & SQL-Based Analytics")

# ── Live KPI Cards ──
total_players = run_query("SELECT COUNT(*) AS c FROM players")["c"][0]
total_matches = run_query("SELECT COUNT(*) AS c FROM matches")["c"][0]
total_teams   = run_query("SELECT COUNT(*) AS c FROM teams")["c"][0]
total_venues  = run_query("SELECT COUNT(*) AS c FROM venues")["c"][0]
total_runs    = run_query("SELECT COALESCE(SUM(runs_scored),0) AS c FROM player_match_stats")["c"][0]
total_wickets = run_query("SELECT COALESCE(SUM(wickets_taken),0) AS c FROM player_match_stats")["c"][0]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🏏 Players",  f"{total_players:,}")
c2.metric("🏟️ Matches",  f"{total_matches:,}")
c3.metric("🚩 Teams",    f"{total_teams:,}")
c4.metric("📍 Venues",   f"{total_venues:,}")
c5.metric("🔥 Total Runs",    f"{total_runs:,}")
c6.metric("🎯 Total Wickets", f"{total_wickets:,}")

st.divider()

# ── Top 5 Run Scorers & Wicket Takers ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 5 Run Scorers")
    df = run_query("""
        SELECT p.full_name AS Player, t.team_name AS Team,
               SUM(s.runs_scored) AS Runs,
               ROUND(AVG(s.strike_rate),1) AS "Avg SR"
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        LEFT JOIN teams t ON p.team_id = t.team_id
        GROUP BY p.player_id
        ORDER BY Runs DESC LIMIT 5
    """)
    st.dataframe(df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🎯 Top 5 Wicket Takers")
    df = run_query("""
        SELECT p.full_name AS Player, t.team_name AS Team,
               SUM(s.wickets_taken) AS Wickets,
               ROUND(AVG(NULLIF(s.economy_rate,0)),2) AS "Avg Eco"
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        LEFT JOIN teams t ON p.team_id = t.team_id
        GROUP BY p.player_id
        HAVING Wickets > 0
        ORDER BY Wickets DESC LIMIT 5
    """)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ── Pages Guide ──
st.subheader("📌 Pages Guide")
st.markdown("""
| Page | What it does |
|---|---|
| 🔴 Live Matches | Pulls live/recent/upcoming matches from the Cricbuzz API |
| 📊 Player Stats | Top run-scorers, wicket-takers etc. from the API |
| 🧮 SQL Analytics | Run the 25 practice SQL queries on the local database |
| ⚙️ CRUD Operations | Add / update / delete player records |
| 🏟️ Matches CRUD | Add / update / delete match records |
| 📝 Scores CRUD | Add / update / delete player score records |
| 📊 Visualizations | Interactive charts from the local database |
| 📈 Analytics Overview | Quick KPIs and leaderboards |
""")

st.info("👈 Pick a page from the sidebar to get started.")

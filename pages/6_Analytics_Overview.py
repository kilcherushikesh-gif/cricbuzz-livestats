import streamlit as st
from utils.db_connection import run_query, init_db
from utils.theme import apply_theme, hero

st.set_page_config(page_title="Analytics Overview", page_icon="📈", layout="wide")
apply_theme()
init_db()

hero("📈 Analytics Overview", "Quick KPIs and leaderboards from the local database")

total_players = run_query("SELECT COUNT(*) AS c FROM players")["c"][0]
total_matches = run_query("SELECT COUNT(*) AS c FROM matches")["c"][0]
total_teams = run_query("SELECT COUNT(*) AS c FROM teams")["c"][0]
total_venues = run_query("SELECT COUNT(*) AS c FROM venues")["c"][0]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Players", total_players)
k2.metric("Matches", total_matches)
k3.metric("Teams", total_teams)
k4.metric("Venues", total_venues)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Batting leaderboard")
    df = run_query(
        """SELECT p.full_name, SUM(s.runs_scored) AS total_runs,
                  ROUND(AVG(s.strike_rate), 2) AS avg_strike_rate
           FROM player_match_stats s JOIN players p ON s.player_id = p.player_id
           GROUP BY p.player_id
           ORDER BY total_runs DESC
           LIMIT 10"""
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🎯 Bowling leaderboard")
    df = run_query(
        """SELECT p.full_name, SUM(s.wickets_taken) AS total_wickets,
                  ROUND(AVG(NULLIF(s.economy_rate,0)), 2) AS avg_economy
           FROM player_match_stats s JOIN players p ON s.player_id = p.player_id
           GROUP BY p.player_id
           HAVING total_wickets > 0
           ORDER BY total_wickets DESC
           LIMIT 10"""
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("🏆 Team win tally")
df = run_query(
    """SELECT t.team_name, COUNT(*) AS wins
       FROM matches m JOIN teams t ON m.winning_team_id = t.team_id
       GROUP BY t.team_id ORDER BY wins DESC"""
)
st.dataframe(df, use_container_width=True, hide_index=True)

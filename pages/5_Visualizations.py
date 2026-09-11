import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import run_query, init_db
from utils.theme import apply_theme, hero
apply_theme()

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")
init_db()

st.title("📊 Cricket Visualizations")
st.caption("Interactive charts built from the local database.")

matches = run_query(
    """SELECT m.match_id, m.match_date, m.match_format, t1.team_name AS team1,
              t2.team_name AS team2, w.team_name AS winner
       FROM matches m
       JOIN teams t1 ON m.team1_id = t1.team_id
       JOIN teams t2 ON m.team2_id = t2.team_id
       LEFT JOIN teams w ON m.winning_team_id = w.team_id"""
)
stats = run_query(
    """SELECT s.*, p.full_name, p.playing_role, t.team_name
       FROM player_match_stats s
       JOIN players p ON s.player_id = p.player_id
       LEFT JOIN teams t ON s.team_id = t.team_id"""
)
players = run_query("SELECT * FROM players")

if matches.empty and stats.empty:
    st.info("No data yet.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Wins per team")
    if not matches.empty and matches["winner"].notna().any():
        win_counts = matches["winner"].value_counts().reset_index()
        win_counts.columns = ["team", "wins"]
        fig = px.bar(win_counts, x="team", y="wins", color="team", title="Total Wins by Team")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No completed matches with a recorded winner yet.")

with col2:
    st.subheader("👥 Players by role")
    if not players.empty:
        role_counts = players["playing_role"].value_counts().reset_index()
        role_counts.columns = ["role", "count"]
        fig = px.pie(role_counts, values="count", names="role", title="Playing Role Breakdown")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("🏏 Top run scorers")
if not stats.empty:
    top_runs = (
        stats.groupby("full_name")["runs_scored"].sum().reset_index()
        .sort_values("runs_scored", ascending=False).head(10)
    )
    fig = px.bar(top_runs, x="full_name", y="runs_scored", title="Top 10 Run Scorers")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🎯 Top wicket takers")
if not stats.empty:
    top_wickets = (
        stats.groupby("full_name")["wickets_taken"].sum().reset_index()
        .sort_values("wickets_taken", ascending=False).head(10)
    )
    top_wickets = top_wickets[top_wickets["wickets_taken"] > 0]
    if not top_wickets.empty:
        fig = px.bar(top_wickets, x="full_name", y="wickets_taken", title="Top 10 Wicket Takers")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bowling data yet.")

st.subheader("📅 Matches over time")
if not matches.empty:
    matches["match_date"] = pd.to_datetime(matches["match_date"], errors="coerce")
    timeline = matches.dropna(subset=["match_date"]).sort_values("match_date")
    if not timeline.empty:
        fig = px.scatter(
            timeline, x="match_date", y="match_format",
            hover_data=["team1", "team2"], title="Matches Timeline",
        )
        st.plotly_chart(fig, use_container_width=True)
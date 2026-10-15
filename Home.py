import streamlit as st
import pandas as pd
from utils.db_connection import init_db, run_query
from utils.theme import apply_theme, hero

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")
apply_theme()

init_db()

# ── Hero Banner ──
hero("🏏 Cricbuzz LiveStats", "Real-Time Cricket Insights & SQL-Based Analytics")

all_formats = run_query(
    "SELECT DISTINCT match_format FROM matches WHERE match_format IS NOT NULL ORDER BY match_format"
)["match_format"].tolist()
all_teams = run_query("SELECT team_name FROM teams ORDER BY team_name")["team_name"].tolist()
date_bounds = run_query("SELECT MIN(match_date) AS start_date, MAX(match_date) AS end_date FROM matches").iloc[0]

if pd.isna(date_bounds.start_date):
    st.info("No match data is available yet. Load match data to explore the dashboard.")
    st.stop()

min_date, max_date = pd.to_datetime(date_bounds).dt.date
with st.sidebar:
    st.subheader("Match filters")
    selected_formats = st.multiselect("Match format", all_formats, default=all_formats)
    date_range = st.date_input(
        "Match dates",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    selected_teams = st.multiselect("Teams (optional)", all_teams, help="Leave empty to include every team.")

if len(date_range) != 2:
    st.info("Choose both a start date and an end date.")
    st.stop()

where = ["m.match_date BETWEEN ? AND ?"]
params = [str(date_range[0]), str(date_range[1])]
if selected_formats:
    where.append("m.match_format IN (" + ", ".join("?" for _ in selected_formats) + ")")
    params.extend(selected_formats)
else:
    where.append("0")
if selected_teams:
    placeholders = ", ".join("?" for _ in selected_teams)
    where.append(f"(t1.team_name IN ({placeholders}) OR t2.team_name IN ({placeholders}))")
    params.extend(selected_teams)
    params.extend(selected_teams)
where_sql = " AND ".join(where)

matches = run_query(
    f"""SELECT m.match_id, m.match_date, m.match_format,
              t1.team_name AS team1, t2.team_name AS team2, v.venue_name AS venue,
              w.team_name AS winner
       FROM matches m
       JOIN teams t1 ON m.team1_id = t1.team_id
       JOIN teams t2 ON m.team2_id = t2.team_id
       LEFT JOIN teams w ON m.winning_team_id = w.team_id
       LEFT JOIN venues v ON m.venue_id = v.venue_id
       WHERE {where_sql}""",
    tuple(params),
)
stats = run_query(
    f"""SELECT s.match_id, p.full_name, t.team_name, s.runs_scored,
              s.strike_rate, s.wickets_taken, s.economy_rate
       FROM player_match_stats s
       JOIN matches m ON s.match_id = m.match_id
       JOIN teams t1 ON m.team1_id = t1.team_id
       JOIN teams t2 ON m.team2_id = t2.team_id
       JOIN players p ON s.player_id = p.player_id
       LEFT JOIN teams t ON s.team_id = t.team_id
       WHERE {where_sql}""",
    tuple(params),
)

if matches.empty:
    st.info("No matches match these filters. Try widening the date range or selecting more formats/teams.")
    st.stop()

total_players = stats["full_name"].nunique()
total_matches = len(matches)
total_teams = pd.concat([matches["team1"], matches["team2"]]).nunique()
total_venues = matches["venue"].nunique()
total_runs = int(stats["runs_scored"].sum()) if not stats.empty else 0
total_wickets = int(stats["wickets_taken"].sum()) if not stats.empty else 0

st.caption(f"Showing {total_matches:,} matches from {date_range[0]:%d %b %Y} to {date_range[1]:%d %b %Y}")
with st.container(horizontal=True):
    st.metric("🏏 Players", f"{total_players:,}", border=True)
    st.metric("🏟️ Matches", f"{total_matches:,}", border=True)
    st.metric("🚩 Teams", f"{total_teams:,}", border=True)
    st.metric("📍 Venues", f"{total_venues:,}", border=True)
    st.metric("🔥 Total Runs", f"{total_runs:,}", border=True)
    st.metric("🎯 Total Wickets", f"{total_wickets:,}", border=True)

st.divider()

# ── Top 5 Run Scorers & Wicket Takers ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 5 Run Scorers")
    top_runs = (
        stats.groupby(["full_name", "team_name"], dropna=False)
        .agg(Runs=("runs_scored", "sum"), **{"Avg SR": ("strike_rate", "mean")})
        .reset_index().sort_values("Runs", ascending=False).head(5)
        .rename(columns={"full_name": "Player", "team_name": "Team"})
    )
    st.dataframe(top_runs, width="stretch", hide_index=True)

with col2:
    st.subheader("🎯 Top 5 Wicket Takers")
    top_wickets = (
        stats.groupby(["full_name", "team_name"], dropna=False)
        .agg(Wickets=("wickets_taken", "sum"), **{"Avg Eco": ("economy_rate", "mean")})
        .reset_index()
    )
    top_wickets = top_wickets[top_wickets["Wickets"] > 0].sort_values("Wickets", ascending=False).head(5)
    top_wickets = top_wickets.rename(columns={"full_name": "Player", "team_name": "Team"})
    st.dataframe(top_wickets, width="stretch", hide_index=True)

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

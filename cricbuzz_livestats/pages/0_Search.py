import streamlit as st
from utils.db_connection import run_query
from utils.theme import apply_theme, hero

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
apply_theme()
init_db = lambda: None

hero("🔍 Search", "Search players, teams, and matches")

tab1, tab2, tab3 = st.tabs(["🏏 Players", "🏆 Teams", "📅 Matches"])

with tab1:
    q = st.text_input("Search Player", placeholder="e.g. Virat Kohli")
    if q:
        df = run_query(f"""
            SELECT p.full_name AS Player, p.country AS Country,
                   p.playing_role AS Role,
                   SUM(s.runs_scored) AS Total_Runs,
                   SUM(s.wickets_taken) AS Total_Wickets
            FROM players p
            LEFT JOIN player_match_stats s ON p.player_id = s.player_id
            WHERE p.full_name LIKE '%{q}%'
            GROUP BY p.player_id
            ORDER BY Total_Runs DESC
        """)
        if df.empty:
            st.warning("Koi player nahi mila!")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    q2 = st.text_input("Search Team", placeholder="e.g. India")
    if q2:
        df2 = run_query(f"""
            SELECT t.team_name AS Team, t.country AS Country,
                   COUNT(m.match_id) AS Matches_Played,
                   SUM(CASE WHEN m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS Wins
            FROM teams t
            LEFT JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
            WHERE t.team_name LIKE '%{q2}%'
            GROUP BY t.team_id
        """)
        if df2.empty:
            st.warning("Koi team nahi mili!")
        else:
            st.dataframe(df2, use_container_width=True, hide_index=True)

with tab3:
    q3 = st.text_input("Search by Team Name", placeholder="e.g. India vs Australia")
    if q3:
        df3 = run_query(f"""
            SELECT m.match_date AS Date, m.match_format AS Format,
                   t1.team_name AS Team1, t2.team_name AS Team2,
                   w.team_name AS Winner, v.venue_name AS Venue
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN teams w ON m.winning_team_id = w.team_id
            LEFT JOIN venues v ON m.venue_id = v.venue_id
            WHERE t1.team_name LIKE '%{q3}%' OR t2.team_name LIKE '%{q3}%'
            ORDER BY m.match_date DESC LIMIT 50
        """)
        if df3.empty:
            st.warning("Koi match nahi mila!")
        else:
            st.dataframe(df3, use_container_width=True, hide_index=True)
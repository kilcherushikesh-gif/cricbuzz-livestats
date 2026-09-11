import streamlit as st
from utils.db_connection import run_query, run_action, init_db
from utils.theme import apply_theme, hero

st.set_page_config(page_title="Scores CRUD", page_icon="📝", layout="wide")
apply_theme()
init_db()

hero("📝 CRUD Operations — Player Scores", "Add, view, update or delete per-match batting/bowling stats")

tab_create, tab_read, tab_update, tab_delete = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])

matches_df = run_query(
    """SELECT m.match_id, m.match_desc, t1.team_name AS team1, t2.team_name AS team2
       FROM matches m
       LEFT JOIN teams t1 ON m.team1_id = t1.team_id
       LEFT JOIN teams t2 ON m.team2_id = t2.team_id
       ORDER BY m.match_id DESC"""
)
match_options = {
    f"{row.match_desc} (#{row.match_id})": row.match_id for row in matches_df.itertuples()
} if not matches_df.empty else {}

players_df = run_query(
    """SELECT p.player_id, p.full_name, p.team_id, t.team_name
       FROM players p LEFT JOIN teams t ON p.team_id = t.team_id
       ORDER BY p.full_name"""
)
player_options = {
    f"{row.full_name} ({row.team_name or 'no team'})": (row.player_id, row.team_id)
    for row in players_df.itertuples()
} if not players_df.empty else {}

with tab_create:
    st.subheader("Add a player's stats for a match")
    if not match_options or not player_options:
        st.warning("You need at least one match and one player first (use fetch_real_data.py / "
                   "the Matches CRUD page / the Players CRUD page).")
    else:
        with st.form("score_create_form"):
            match_label = st.selectbox("Match", list(match_options.keys()))
            player_label = st.selectbox("Player", list(player_options.keys()))
            batting_position = st.number_input("Batting position", min_value=0, step=1, value=0)

            st.markdown("**Batting**")
            c1, c2, c3, c4 = st.columns(4)
            runs_scored = c1.number_input("Runs", min_value=0, step=1)
            balls_faced = c2.number_input("Balls", min_value=0, step=1)
            fours = c3.number_input("4s", min_value=0, step=1)
            sixes = c4.number_input("6s", min_value=0, step=1)

            st.markdown("**Bowling**")
            c5, c6, c7 = st.columns(3)
            overs_bowled = c5.number_input("Overs bowled", min_value=0.0, step=0.1, format="%.1f")
            runs_conceded = c6.number_input("Runs conceded", min_value=0, step=1)
            wickets_taken = c7.number_input("Wickets", min_value=0, step=1)

            st.markdown("**Fielding**")
            c8, c9 = st.columns(2)
            catches = c8.number_input("Catches", min_value=0, step=1)
            stumpings = c9.number_input("Stumpings", min_value=0, step=1)

            submitted = st.form_submit_button("Add score")
            if submitted:
                match_id = match_options[match_label]
                player_id, team_id = player_options[player_label]
                strike_rate = round(runs_scored * 100.0 / balls_faced, 2) if balls_faced else 0
                economy_rate = round(runs_conceded / overs_bowled, 2) if overs_bowled else 0
                run_action(
                    """INSERT INTO player_match_stats
                       (match_id, player_id, team_id, batting_position, runs_scored, balls_faced,
                        fours, sixes, strike_rate, overs_bowled, runs_conceded, wickets_taken,
                        economy_rate, catches, stumpings)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        match_id, player_id, team_id, int(batting_position),
                        int(runs_scored), int(balls_faced), int(fours), int(sixes),
                        strike_rate, float(overs_bowled), int(runs_conceded), int(wickets_taken),
                        economy_rate, int(catches), int(stumpings),
                    ),
                )
                st.success("Score added.")

with tab_read:
    st.subheader("All player scores")
    df = run_query(
        """SELECT s.stat_id, m.match_desc, p.full_name, t.team_name,
                  s.runs_scored, s.balls_faced, s.strike_rate,
                  s.overs_bowled, s.wickets_taken, s.economy_rate,
                  s.catches, s.stumpings
           FROM player_match_stats s
           JOIN matches m ON s.match_id = m.match_id
           JOIN players p ON s.player_id = p.player_id
           LEFT JOIN teams t ON s.team_id = t.team_id
           ORDER BY m.match_date DESC, s.stat_id DESC"""
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} score row(s) total")

with tab_update:
    st.subheader("Update a score")
    df = run_query(
        """SELECT s.stat_id, m.match_desc, p.full_name
           FROM player_match_stats s
           JOIN matches m ON s.match_id = m.match_id
           JOIN players p ON s.player_id = p.player_id
           ORDER BY m.match_date DESC, s.stat_id DESC"""
    )
    if df.empty:
        st.info("No score rows yet.")
    else:
        options = {f"{row.full_name} — {row.match_desc} (#{row.stat_id})": row.stat_id for row in df.itertuples()}
        chosen = st.selectbox("Score row to edit", list(options.keys()))
        sid = options[chosen]
        current = run_query("SELECT * FROM player_match_stats WHERE stat_id = ?", (sid,)).iloc[0]
        with st.form("score_update_form"):
            c1, c2, c3, c4 = st.columns(4)
            runs_scored = c1.number_input("Runs", min_value=0, step=1, value=int(current["runs_scored"] or 0))
            balls_faced = c2.number_input("Balls", min_value=0, step=1, value=int(current["balls_faced"] or 0))
            fours = c3.number_input("4s", min_value=0, step=1, value=int(current["fours"] or 0))
            sixes = c4.number_input("6s", min_value=0, step=1, value=int(current["sixes"] or 0))
            c5, c6, c7 = st.columns(3)
            overs_bowled = c5.number_input("Overs bowled", min_value=0.0, step=0.1, format="%.1f",
                                            value=float(current["overs_bowled"] or 0))
            runs_conceded = c6.number_input("Runs conceded", min_value=0, step=1,
                                             value=int(current["runs_conceded"] or 0))
            wickets_taken = c7.number_input("Wickets", min_value=0, step=1,
                                             value=int(current["wickets_taken"] or 0))
            if st.form_submit_button("Save changes"):
                strike_rate = round(runs_scored * 100.0 / balls_faced, 2) if balls_faced else 0
                economy_rate = round(runs_conceded / overs_bowled, 2) if overs_bowled else 0
                run_action(
                    """UPDATE player_match_stats SET
                         runs_scored=?, balls_faced=?, fours=?, sixes=?, strike_rate=?,
                         overs_bowled=?, runs_conceded=?, wickets_taken=?, economy_rate=?
                       WHERE stat_id=?""",
                    (
                        int(runs_scored), int(balls_faced), int(fours), int(sixes), strike_rate,
                        float(overs_bowled), int(runs_conceded), int(wickets_taken), economy_rate,
                        sid,
                    ),
                )
                st.success("Updated.")

with tab_delete:
    st.subheader("Delete a score row")
    df = run_query(
        """SELECT s.stat_id, m.match_desc, p.full_name
           FROM player_match_stats s
           JOIN matches m ON s.match_id = m.match_id
           JOIN players p ON s.player_id = p.player_id
           ORDER BY m.match_date DESC, s.stat_id DESC"""
    )
    if df.empty:
        st.info("No score rows yet.")
    else:
        options = {f"{row.full_name} — {row.match_desc} (#{row.stat_id})": row.stat_id for row in df.itertuples()}
        chosen = st.selectbox("Score row to delete", list(options.keys()), key="score_delete_select")
        if st.button("🗑️ Delete this score row", type="primary"):
            run_action("DELETE FROM player_match_stats WHERE stat_id = ?", (options[chosen],))
            st.success(f"Deleted score row for {chosen}.")
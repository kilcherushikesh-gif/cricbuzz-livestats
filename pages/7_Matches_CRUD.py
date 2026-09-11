import streamlit as st
from utils.db_connection import run_query, run_action, init_db
from utils.theme import apply_theme, hero

st.set_page_config(page_title="Matches CRUD", page_icon="🏟️", layout="wide")
apply_theme()
init_db()

hero("🏟️ CRUD Operations — Matches", "Add, view, update or delete match records")

tab_create, tab_read, tab_update, tab_delete = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])

teams_df = run_query("SELECT team_id, team_name FROM teams ORDER BY team_name")
team_options = dict(zip(teams_df["team_name"], teams_df["team_id"])) if not teams_df.empty else {}

venues_df = run_query("SELECT venue_id, venue_name FROM venues ORDER BY venue_name")
venue_options = dict(zip(venues_df["venue_name"], venues_df["venue_id"])) if not venues_df.empty else {}

series_df = run_query("SELECT series_id, series_name FROM series ORDER BY series_name")
series_options = dict(zip(series_df["series_name"], series_df["series_id"])) if not series_df.empty else {}

FORMATS = ["Test", "ODI", "T20I"]
VICTORY_TYPES = ["runs", "wickets", ""]

with tab_create:
    st.subheader("Add a new match")
    if not team_options:
        st.warning("Add some teams first (fetch real data, or use the CRUD/SQL pages).")
    else:
        with st.form("match_create_form"):
            match_desc = st.text_input("Match description", placeholder="India vs Australia, 1st ODI")
            col1, col2 = st.columns(2)
            with col1:
                team1_name = st.selectbox("Team 1", list(team_options.keys()))
            with col2:
                team2_name = st.selectbox("Team 2", list(team_options.keys()), index=min(1, len(team_options) - 1))
            venue_name = st.selectbox("Venue", ["(none)"] + list(venue_options.keys()))
            series_name = st.selectbox("Series", ["(none)"] + list(series_options.keys()))
            match_date = st.date_input("Match date")
            match_format = st.selectbox("Format", FORMATS)
            winner_name = st.selectbox("Winning team", ["(no result yet)"] + list(team_options.keys()))
            col3, col4 = st.columns(2)
            with col3:
                victory_margin = st.number_input("Victory margin", min_value=0, step=1)
            with col4:
                victory_type = st.selectbox("Victory type", VICTORY_TYPES)
            submitted = st.form_submit_button("Add match")
            if submitted:
                if not match_desc:
                    st.warning("Match description is required.")
                elif team1_name == team2_name:
                    st.warning("Team 1 and Team 2 must be different.")
                else:
                    run_action(
                        """INSERT INTO matches
                           (series_id, match_desc, team1_id, team2_id, venue_id, match_date, match_format,
                            winning_team_id, victory_margin, victory_type, toss_winner_id, toss_decision)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)""",
                        (
                            series_options.get(series_name),
                            match_desc,
                            team_options[team1_name],
                            team_options[team2_name],
                            venue_options.get(venue_name),
                            str(match_date),
                            match_format,
                            team_options.get(winner_name),
                            int(victory_margin) if victory_margin else None,
                            victory_type or None,
                        ),
                    )
                    st.success(f"Added match: {match_desc}")

with tab_read:
    st.subheader("All matches")
    df = run_query(
        """SELECT m.match_id, m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
                  v.venue_name, m.match_date, m.match_format,
                  w.team_name AS winner, m.victory_margin, m.victory_type
           FROM matches m
           LEFT JOIN teams t1 ON m.team1_id = t1.team_id
           LEFT JOIN teams t2 ON m.team2_id = t2.team_id
           LEFT JOIN venues v ON m.venue_id = v.venue_id
           LEFT JOIN teams w ON m.winning_team_id = w.team_id
           ORDER BY m.match_date DESC"""
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} match(es) total")

with tab_update:
    st.subheader("Update a match")
    df = run_query("SELECT match_id, match_desc FROM matches ORDER BY match_id DESC")
    if df.empty:
        st.info("No matches yet.")
    else:
        options = {f"{row.match_desc} (#{row.match_id})": row.match_id for row in df.itertuples()}
        chosen = st.selectbox("Match to edit", list(options.keys()))
        mid = options[chosen]
        current = run_query("SELECT * FROM matches WHERE match_id = ?", (mid,)).iloc[0]
        with st.form("match_update_form"):
            new_desc = st.text_input("Match description", current["match_desc"] or "")
            new_format = st.selectbox(
                "Format", FORMATS,
                index=FORMATS.index(current["match_format"]) if current["match_format"] in FORMATS else 0,
            )
            new_margin = st.number_input("Victory margin", min_value=0, step=1,
                                          value=int(current["victory_margin"] or 0))
            new_vtype = st.selectbox(
                "Victory type", VICTORY_TYPES,
                index=VICTORY_TYPES.index(current["victory_type"]) if current["victory_type"] in VICTORY_TYPES else 2,
            )
            if st.form_submit_button("Save changes"):
                run_action(
                    """UPDATE matches SET match_desc=?, match_format=?, victory_margin=?, victory_type=?
                       WHERE match_id=?""",
                    (new_desc, new_format, new_margin or None, new_vtype or None, mid),
                )
                st.success("Updated.")

with tab_delete:
    st.subheader("Delete a match")
    df = run_query("SELECT match_id, match_desc FROM matches ORDER BY match_id DESC")
    if df.empty:
        st.info("No matches yet.")
    else:
        options = {f"{row.match_desc} (#{row.match_id})": row.match_id for row in df.itertuples()}
        chosen = st.selectbox("Match to delete", list(options.keys()), key="match_delete_select")
        mid = options[chosen]
        stat_count = run_query(
            "SELECT COUNT(*) AS c FROM player_match_stats WHERE match_id = ?", (mid,)
        )["c"][0]
        if stat_count:
            st.warning(f"This match has {stat_count} linked player stat row(s), which will be deleted too.")
        if st.button("🗑️ Delete this match", type="primary"):
            run_action("DELETE FROM player_match_stats WHERE match_id = ?", (mid,))
            run_action("DELETE FROM matches WHERE match_id = ?", (mid,))
            st.success(f"Deleted {chosen}.")

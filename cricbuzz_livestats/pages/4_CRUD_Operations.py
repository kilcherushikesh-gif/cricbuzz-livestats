import streamlit as st
from utils.db_connection import run_query, run_action, init_db
from utils.theme import apply_theme, hero
apply_theme()

st.set_page_config(page_title="CRUD Operations", page_icon="⚙️", layout="wide")
init_db()

hero("⚙️ CRUD Operations — Players", "Add, view, update or delete player records")

tab_create, tab_read, tab_update, tab_delete = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])

teams_df = run_query("SELECT team_id, team_name FROM teams ORDER BY team_name")
team_options = dict(zip(teams_df["team_name"], teams_df["team_id"])) if not teams_df.empty else {}

ROLES    = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
STATUSES = ["Active", "Retired", "Injured", "Unknown"]

with tab_create:
    st.subheader("Add a new player")
    with st.form("create_form"):
        full_name     = st.text_input("Full name")
        team_name     = st.selectbox("Team", list(team_options.keys())) if team_options else None
        role          = st.selectbox("Playing role", ROLES)
        status        = st.selectbox("Status", STATUSES)
        batting_style = st.text_input("Batting style", "Right-hand bat")
        bowling_style = st.text_input("Bowling style (leave blank if none)", "")
        submitted = st.form_submit_button("Add player")
        if submitted:
            if not full_name:
                st.warning("Full name is required.")
            else:
                run_action(
                    """INSERT INTO players
                       (full_name, team_id, playing_role, batting_style, bowling_style, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (full_name, team_options.get(team_name), role,
                     batting_style, bowling_style or None, status),
                )
                st.success(f"Added {full_name}.")

with tab_read:
    st.subheader("All players")
    fc1, fc2, fc3 = st.columns(3)
    search   = fc1.text_input("🔍 Search by name")
    f_status = fc2.selectbox("Filter by status", ["All"] + STATUSES)
    f_role   = fc3.selectbox("Filter by role",   ["All"] + ROLES)
    df = run_query(
        """SELECT p.player_id, p.full_name, t.team_name,
                  p.playing_role, p.batting_style, p.bowling_style,
                  COALESCE(p.status, 'Active') AS status
           FROM players p LEFT JOIN teams t ON p.team_id = t.team_id
           ORDER BY p.full_name"""
    )
    if search:
        df = df[df["full_name"].str.contains(search, case=False, na=False)]
    if f_status != "All":
        df = df[df["status"] == f_status]
    if f_role != "All":
        df = df[df["playing_role"] == f_role]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} player(s) shown")

with tab_update:
    st.subheader("Update a player")
    df = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    if df.empty:
        st.info("No players yet.")
    else:
        options = dict(zip(df["full_name"], df["player_id"]))
        chosen  = st.selectbox("Player to edit", list(options.keys()))
        pid     = options[chosen]
        current = run_query("SELECT * FROM players WHERE player_id = ?", (pid,)).iloc[0]
        with st.form("update_form"):
            new_name    = st.text_input("Full name", current["full_name"])
            new_role    = st.selectbox("Playing role", ROLES,
                            index=ROLES.index(current["playing_role"])
                            if current["playing_role"] in ROLES else 0)
            cur_status  = current.get("status", "Active") or "Active"
            new_status  = st.selectbox("Status", STATUSES,
                            index=STATUSES.index(cur_status)
                            if cur_status in STATUSES else 0)
            new_batting = st.text_input("Batting style", current["batting_style"] or "")
            new_bowling = st.text_input("Bowling style", current["bowling_style"] or "")
            if st.form_submit_button("Save changes"):
                run_action(
                    """UPDATE players
                       SET full_name=?, playing_role=?, batting_style=?,
                           bowling_style=?, status=?
                       WHERE player_id=?""",
                    (new_name, new_role, new_batting, new_bowling, new_status, pid),
                )
                st.success("Updated.")

with tab_delete:
    st.subheader("Delete a player")
    df = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    if df.empty:
        st.info("No players yet.")
    else:
        options = dict(zip(df["full_name"], df["player_id"]))
        chosen  = st.selectbox("Player to delete", list(options.keys()), key="del_sel")
        if st.button("🗑️ Delete this player", type="primary"):
            run_action("DELETE FROM players WHERE player_id = ?", (options[chosen],))
            st.success(f"Deleted {chosen}.")
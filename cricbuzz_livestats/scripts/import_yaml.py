"""
scripts/import_yaml.py

Imports Cricsheet-format YAML match files into the local SQLite database.
Each YAML file contains ball-by-ball data for one match.

Usage (run from project root):
    python scripts/import_yaml.py --folder "C:\\path\\to\\yaml\\folder"

Example:
    python scripts/import_yaml.py --folder "C:\\Users\\HP\\Downloads\\yaml_matches"

Requirements:
    pip install pyyaml   (add to requirements.txt if not already there)

What gets inserted:
  - teams          : from info.teams
  - venues         : from info.venue + info.city
  - matches        : from info fields
  - players        : from info.players
  - player_match_stats : aggregated from ball-by-ball deliveries
    (runs, balls, fours, sixes, overs bowled, runs conceded, wickets, catches)

Already-inserted matches (same teams + date) are skipped automatically.
"""

import argparse
import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run:  pip install pyyaml")
    sys.exit(1)

from utils.db_connection import get_connection, init_db


# ── helpers ──────────────────────────────────────────────────────────────────

def get_or_create(conn, table, name_col, name_val, extra_cols=None):
    """Generic upsert-or-fetch for simple lookup tables."""
    if not name_val:
        return None
    cur = conn.cursor()
    cur.execute(f"SELECT rowid FROM {table} WHERE {name_col} = ?", (name_val,))
    row = cur.fetchone()
    if row:
        return row[0]
    cols = [name_col] + list((extra_cols or {}).keys())
    vals = [name_val] + list((extra_cols or {}).values())
    placeholders = ",".join("?" * len(cols))
    cur.execute(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", vals
    )
    conn.commit()
    return cur.lastrowid


def get_or_create_team(conn, name):
    return get_or_create(conn, "teams", "team_name", name, {"country": name})


def get_or_create_venue(conn, venue_name, city):
    if not venue_name:
        return None
    cur = conn.cursor()
    cur.execute("SELECT venue_id FROM venues WHERE venue_name = ?", (venue_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO venues (venue_name, city, country, capacity) VALUES (?, ?, NULL, NULL)",
        (venue_name, city),
    )
    conn.commit()
    return cur.lastrowid


def get_or_create_player(conn, name, team_id):
    if not name:
        return None
    cur = conn.cursor()
    cur.execute("SELECT player_id FROM players WHERE full_name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO players (full_name, team_id, playing_role) VALUES (?, ?, NULL)",
        (name, team_id),
    )
    conn.commit()
    return cur.lastrowid


def match_already_inserted(conn, team1_id, team2_id, match_date):
    cur = conn.cursor()
    cur.execute(
        """SELECT match_id FROM matches
           WHERE team1_id=? AND team2_id=? AND match_date=?""",
        (team1_id, team2_id, match_date),
    )
    row = cur.fetchone()
    return row[0] if row else None


# ── main importer ────────────────────────────────────────────────────────────

def import_yaml_file(conn, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    info = data.get("info", {})
    innings_list = data.get("innings", [])

    # ── teams ──
    teams = info.get("teams", [])
    if len(teams) < 2:
        return False, "less than 2 teams"
    team1_id = get_or_create_team(conn, teams[0])
    team2_id = get_or_create_team(conn, teams[1])

    # ── venue ──
    venue_id = get_or_create_venue(conn, info.get("venue"), info.get("city"))

    # ── date ──
    dates = info.get("dates", [])
    match_date = str(dates[0]) if dates else None

    # ── skip if already in DB ──
    existing_id = match_already_inserted(conn, team1_id, team2_id, match_date)
    if existing_id:
        return False, "already exists"

    # ── outcome ──
    outcome = info.get("outcome", {})
    winner_name = outcome.get("winner")
    winning_team_id = None
    if winner_name:
        for t in teams:
            if t == winner_name:
                winning_team_id = get_or_create_team(conn, t)
                break
    by = outcome.get("by", {})
    victory_margin = None
    victory_type = None
    if "runs" in by:
        victory_margin = by["runs"]
        victory_type = "runs"
    elif "wickets" in by:
        victory_margin = by["wickets"]
        victory_type = "wickets"

    # ── toss ──
    toss = info.get("toss", {})
    toss_winner_name = toss.get("winner")
    toss_winner_id = None
    if toss_winner_name:
        toss_winner_id = get_or_create_team(conn, toss_winner_name)
    toss_decision = toss.get("decision")

    # ── match format ──
    fmt_map = {"Test": "Test", "ODI": "ODI", "T20": "T20I", "T20I": "T20I",
               "T20 Blast": "T20I", "IPL": "T20I"}
    match_format = fmt_map.get(info.get("match_type", ""), info.get("match_type", ""))

    # ── match description ──
    filename = os.path.splitext(os.path.basename(filepath))[0]
    match_desc = f"{teams[0]} vs {teams[1]}, {match_date} ({filename})"

    # ── insert match ──
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO matches
           (series_id, match_desc, team1_id, team2_id, venue_id, match_date, match_format,
            winning_team_id, victory_margin, victory_type, toss_winner_id, toss_decision)
           VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (match_desc, team1_id, team2_id, venue_id, match_date, match_format,
         winning_team_id, victory_margin, victory_type, toss_winner_id, toss_decision),
    )
    match_id = cur.lastrowid
    conn.commit()

    # ── register all players ──
    player_team_map = {}  # name -> team_id
    for team_name, player_list in info.get("players", {}).items():
        tid = get_or_create_team(conn, team_name)
        for p in (player_list or []):
            pid = get_or_create_player(conn, p, tid)
            player_team_map[p] = (pid, tid)

    # ── aggregate ball-by-ball stats ──
    # batting_stats[player_name] = {runs, balls, fours, sixes}
    # bowling_stats[player_name] = {deliveries, runs_conceded, wickets}
    # fielding_stats[player_name] = {catches}
    batting_stats = {}
    bowling_stats = {}
    fielding_stats = {}

    def bat(name):
        if name not in batting_stats:
            batting_stats[name] = {"runs": 0, "balls": 0, "fours": 0, "sixes": 0}
        return batting_stats[name]

    def bowl(name):
        if name not in bowling_stats:
            bowling_stats[name] = {"deliveries": 0, "runs": 0, "wickets": 0}
        return bowling_stats[name]

    def field(name):
        if name not in fielding_stats:
            fielding_stats[name] = {"catches": 0}
        return fielding_stats[name]

    for innings in innings_list:
        for inn_key, inn_data in innings.items():
            deliveries = inn_data.get("deliveries", [])
            for delivery in deliveries:
                for _, d in delivery.items():
                    batsman = d.get("batsman")
                    bowler = d.get("bowler")
                    runs = d.get("runs", {})
                    extras = d.get("extras", {})

                    # batting
                    if batsman:
                        b = bat(batsman)
                        b["runs"] += runs.get("batsman", 0)
                        # count legal deliveries only (no wides)
                        if "wides" not in extras:
                            b["balls"] += 1
                        r = runs.get("batsman", 0)
                        if r == 4:
                            b["fours"] += 1
                        elif r == 6:
                            b["sixes"] += 1

                    # bowling (count all deliveries incl. no-balls, not wides for overs)
                    if bowler:
                        bo = bowl(bowler)
                        if "wides" not in extras and "noballs" not in extras:
                            bo["deliveries"] += 1
                        bo["runs"] += runs.get("total", 0)

                    # wickets
                    wicket = d.get("wicket", {})
                    if wicket:
                        kind = wicket.get("kind", "")
                        player_out = wicket.get("player_out")
                        # credit bowler (not run-outs)
                        if bowler and kind not in ("run out", "retired hurt", "obstructing the field"):
                            bowl(bowler)["wickets"] += 1
                        # catches
                        if kind == "caught":
                            for fielder in (wicket.get("fielders") or []):
                                field(fielder)["catches"] += 1

    # ── insert player_match_stats rows ──
    all_players = set(batting_stats) | set(bowling_stats)
    position = 1
    for name in all_players:
        if name not in player_team_map:
            # player appeared in deliveries but not in the players list — register them
            pid = get_or_create_player(conn, name, None)
            player_team_map[name] = (pid, None)

        pid, tid = player_team_map[name]
        bs = batting_stats.get(name, {"runs": 0, "balls": 0, "fours": 0, "sixes": 0})
        bw = bowling_stats.get(name, {"deliveries": 0, "runs": 0, "wickets": 0})
        fs = fielding_stats.get(name, {"catches": 0})

        overs = round(bw["deliveries"] / 6, 1)
        strike_rate = round(bs["runs"] * 100.0 / bs["balls"], 2) if bs["balls"] else 0
        economy = round(bw["runs"] / overs, 2) if overs else 0

        cur.execute(
            """INSERT INTO player_match_stats
               (match_id, player_id, team_id, batting_position, runs_scored, balls_faced,
                fours, sixes, strike_rate, overs_bowled, runs_conceded, wickets_taken,
                economy_rate, catches, stumpings)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (match_id, pid, tid, position,
             bs["runs"], bs["balls"], bs["fours"], bs["sixes"],
             strike_rate, overs, bw["runs"], bw["wickets"],
             economy, fs["catches"]),
        )
        position += 1

    conn.commit()
    return True, "ok"


def main():
    parser = argparse.ArgumentParser(description="Import Cricsheet YAML files into DB")
    parser.add_argument(
        "--folder", required=True,
        help='Path to the folder containing .yaml files, e.g. "C:\\Users\\HP\\Downloads\\yaml_matches"'
    )
    args = parser.parse_args()

    folder = args.folder
    if not os.path.isdir(folder):
        print(f"ERROR: Folder not found: {folder}")
        sys.exit(1)

    yaml_files = glob.glob(os.path.join(folder, "*.yaml")) + \
                 glob.glob(os.path.join(folder, "*.yml"))

    if not yaml_files:
        print(f"No .yaml/.yml files found in: {folder}")
        sys.exit(1)

    print(f"Found {len(yaml_files)} YAML file(s). Starting import...")
    init_db()
    conn = get_connection()

    inserted = 0
    skipped = 0
    errors = 0

    for i, filepath in enumerate(yaml_files, 1):
        fname = os.path.basename(filepath)
        try:
            ok, reason = import_yaml_file(conn, filepath)
            if ok:
                inserted += 1
                print(f"  [{i}/{len(yaml_files)}] ✓ {fname}")
            else:
                skipped += 1
                print(f"  [{i}/{len(yaml_files)}] - {fname} ({reason})")
        except Exception as e:
            errors += 1
            print(f"  [{i}/{len(yaml_files)}] ✗ {fname} → ERROR: {e}")

    conn.close()
    print(f"\nDone! Inserted: {inserted} | Skipped: {skipped} | Errors: {errors}")
    print("Refresh your Streamlit app to see the data.")


if __name__ == "__main__":
    main()

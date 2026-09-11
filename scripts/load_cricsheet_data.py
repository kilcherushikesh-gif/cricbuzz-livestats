"""
Loads real match data from Cricsheet YAML files (https://cricsheet.org) into
the local SQLite database. Cricsheet gives ball-by-ball data for real
international and league matches — no API key needed at all.

Usage (run from the project's root folder):

    python scripts/load_cricsheet_data.py --dir "C:\\path\\to\\yaml_folder"

Useful options:
    --limit 200          only load the first 200 matches found (fast test run)
    --format T20         only load a specific format: Test / ODI / T20 / IT20 / MDM / IPL / ...
    --team-type international   or "club" (domestic leagues like IPL)

Examples:
    python scripts/load_cricsheet_data.py --dir "./all_matches" --limit 100
    python scripts/load_cricsheet_data.py --dir "./all_matches" --format T20 --limit 500

NOTE: The full Cricsheet archive has ~23,000 matches. Loading everything will
take a long time and produce a large database — start with --limit 200-500 to
make sure everything looks right, then increase it.
"""

import os
import sys
import glob
import argparse

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.db_connection import get_connection, init_db


def get_or_create_team(conn, team_name):
    if not team_name:
        return None
    cur = conn.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute("INSERT INTO teams (team_name, country) VALUES (?, ?)", (team_name, team_name))
    return cur.lastrowid


def get_or_create_venue(conn, venue_name, city=None):
    if not venue_name:
        return None
    cur = conn.execute("SELECT venue_id FROM venues WHERE venue_name = ?", (venue_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO venues (venue_name, city, country, capacity) VALUES (?, ?, ?, ?)",
        (venue_name, city, None, None),
    )
    return cur.lastrowid


def get_or_create_series(conn, series_name, match_type=None):
    if not series_name:
        return None
    cur = conn.execute("SELECT series_id FROM series WHERE series_name = ?", (series_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO series (series_name, host_country, match_type, start_date, total_matches) VALUES (?, ?, ?, ?, ?)",
        (series_name, None, match_type, None, None),
    )
    return cur.lastrowid


def get_or_create_player(conn, full_name, team_id):
    if not full_name:
        return None
    cur = conn.execute("SELECT player_id FROM players WHERE full_name = ?", (full_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO players (full_name, team_id, playing_role, batting_style, bowling_style) VALUES (?, ?, NULL, NULL, NULL)",
        (full_name, team_id),
    )
    return cur.lastrowid


def parse_match(conn, match_id, data):
    info = data.get("info", {})
    teams = info.get("teams", [])
    if len(teams) != 2:
        return False

    team1_name, team2_name = teams[0], teams[1]
    team1_id = get_or_create_team(conn, team1_name)
    team2_id = get_or_create_team(conn, team2_name)

    venue_id = get_or_create_venue(conn, info.get("venue"), info.get("city"))
    series_name = info.get("competition") or f"{info.get('match_type', 'Unknown')} matches"
    series_id = get_or_create_series(conn, series_name, info.get("match_type"))

    dates = info.get("dates", [])
    match_date = str(dates[0]) if dates else None

    toss = info.get("toss", {})
    toss_winner_name = toss.get("winner")
    toss_winner_id = team1_id if toss_winner_name == team1_name else team2_id if toss_winner_name == team2_name else None
    toss_decision = toss.get("decision")

    outcome = info.get("outcome", {})
    winner_name = outcome.get("winner")
    winning_team_id = team1_id if winner_name == team1_name else team2_id if winner_name == team2_name else None
    by = outcome.get("by", {})
    victory_margin, victory_type = None, None
    if "runs" in by:
        victory_margin, victory_type = by["runs"], "runs"
    elif "wickets" in by:
        victory_margin, victory_type = by["wickets"], "wickets"

    # register players + which team they played for
    player_team = {}
    for team_name, roster in (info.get("players") or {}).items():
        tid = team1_id if team_name == team1_name else team2_id if team_name == team2_name else None
        for name in roster:
            get_or_create_player(conn, name, tid)
            player_team[name] = tid

    cur = conn.execute("SELECT match_id FROM matches WHERE match_id = ?", (match_id,))
    if cur.fetchone():
        return False  # already loaded

    conn.execute(
        """INSERT INTO matches (match_id, series_id, match_desc, team1_id, team2_id, venue_id,
               match_date, match_format, winning_team_id, victory_margin, victory_type,
               toss_winner_id, toss_decision)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            match_id, series_id, f"{team1_name} vs {team2_name}", team1_id, team2_id, venue_id,
            match_date, info.get("match_type"), winning_team_id, victory_margin, victory_type,
            toss_winner_id, toss_decision,
        ),
    )

    # --- ball-by-ball stats ---
    batting, bowling, fielding = {}, {}, {}

    def bat_row(name):
        return batting.setdefault(name, {"runs": 0, "balls": 0, "fours": 0, "sixes": 0})

    def bowl_row(name):
        return bowling.setdefault(name, {"balls": 0, "runs": 0, "wkts": 0})

    def field_row(name):
        return fielding.setdefault(name, {"catches": 0, "stumpings": 0})

    for innings_block in data.get("innings", []):
        for _, inn in innings_block.items():
            for delivery in inn.get("deliveries", []):
                for _, ball in delivery.items():
                    runs = ball.get("runs", {})
                    extras = ball.get("extras", {}) or {}
                    batsman = ball.get("batsman")
                    bowler = ball.get("bowler")

                    if batsman:
                        b = bat_row(batsman)
                        b["runs"] += runs.get("batsman", 0)
                        if "wides" not in extras:
                            b["balls"] += 1
                        if runs.get("batsman") == 4:
                            b["fours"] += 1
                        elif runs.get("batsman") == 6:
                            b["sixes"] += 1

                    if bowler:
                        bw = bowl_row(bowler)
                        is_legal = "wides" not in extras and "noballs" not in extras
                        if is_legal:
                            bw["balls"] += 1
                        conceded = runs.get("total", 0) - extras.get("byes", 0) - extras.get("legbyes", 0)
                        bw["runs"] += max(conceded, 0)

                    wicket = ball.get("wicket")
                    if wicket:
                        kind = (wicket.get("kind") or "").lower()
                        if bowler and kind not in ("run out",):
                            bowl_row(bowler)["wkts"] += 1
                        if kind == "caught":
                            for fielder in wicket.get("fielders", []) or []:
                                field_row(fielder)["catches"] += 1
                        elif kind == "stumped":
                            for fielder in wicket.get("fielders", []) or []:
                                field_row(fielder)["stumpings"] += 1

    all_names = set(batting) | set(bowling) | set(fielding)
    for name in all_names:
        team_id = player_team.get(name)
        player_id = get_or_create_player(conn, name, team_id)
        bat = batting.get(name, {"runs": 0, "balls": 0, "fours": 0, "sixes": 0})
        bwl = bowling.get(name, {"balls": 0, "runs": 0, "wkts": 0})
        fld = fielding.get(name, {"catches": 0, "stumpings": 0})

        strike_rate = round(bat["runs"] * 100 / bat["balls"], 2) if bat["balls"] else 0
        overs_bowled = (bwl["balls"] // 6) + (bwl["balls"] % 6) / 10.0
        economy = round(bwl["runs"] / (bwl["balls"] / 6), 2) if bwl["balls"] else 0

        conn.execute(
            """INSERT INTO player_match_stats
               (match_id, player_id, team_id, runs_scored, balls_faced, fours, sixes, strike_rate,
                overs_bowled, runs_conceded, wickets_taken, economy_rate, catches, stumpings)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                match_id, player_id, team_id, bat["runs"], bat["balls"], bat["fours"], bat["sixes"],
                strike_rate, overs_bowled, bwl["runs"], bwl["wkts"], economy,
                fld["catches"], fld["stumpings"],
            ),
        )

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Folder containing the Cricsheet .yaml files")
    parser.add_argument("--limit", type=int, default=200, help="Max number of matches to load (default 200)")
    parser.add_argument("--format", default=None, help="Only load this match_type, e.g. T20, ODI, Test, IPL")
    parser.add_argument("--team-type", default=None, help="Only load 'international' or 'club' matches")
    args = parser.parse_args()

    init_db()
    conn = get_connection()

    files = sorted(glob.glob(os.path.join(args.dir, "*.yaml")))
    if not files:
        print(f"No .yaml files found in {args.dir}")
        return

    print(f"Found {len(files)} yaml files. Loading up to {args.limit}...")
    loaded, skipped = 0, 0

    for path in files:
        if loaded >= args.limit:
            break
        match_id_str = os.path.splitext(os.path.basename(path))[0]
        if not match_id_str.isdigit():
            continue
        match_id = int(match_id_str)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"  could not parse {path}: {e}")
            continue

        info = data.get("info", {})
        if args.format and info.get("match_type") != args.format:
            continue
        if args.team_type and info.get("team_type") != args.team_type:
            continue

        try:
            ok = parse_match(conn, match_id, data)
            conn.commit()
            if ok:
                loaded += 1
                if loaded % 25 == 0:
                    print(f"  loaded {loaded} matches...")
            else:
                skipped += 1
        except Exception as e:
            print(f"  error on match {match_id}: {e}")
            conn.rollback()

    conn.close()
    print(f"\nDone. {loaded} match(es) loaded, {skipped} skipped (already existed or invalid).")
    print("Open the SQL Analytics / Visualizations pages in the app to see this data.")


if __name__ == "__main__":
    main()

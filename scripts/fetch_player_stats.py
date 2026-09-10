"""
scripts/fetch_player_stats.py

Fetches per-player batting/bowling stats from match SCORECARDS (not just the
match list) and fills the players + player_match_stats tables.

This uses more API calls than fetch_real_data.py (one call per match), so
it's kept separate and limited to MAX_MATCHES completed matches by default
to protect a free-tier RapidAPI quota. Raise MAX_MATCHES if your plan allows.

Run from the project root, AFTER fetch_real_data.py:
    python scripts/fetch_player_stats.py

If the Cricbuzz scorecard response shape differs from what's expected here
(unofficial APIs change their JSON shape without notice), the script prints
a warning per match it can't parse instead of crashing, and prints a sample
of the raw response the first time so the parsing can be adjusted.
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import api_utils
from utils.db_connection import get_connection, init_db

MAX_MATCHES = 15  # raise this if your API plan can handle more calls


def get_or_create_player(conn, full_name, team_id):
    if not full_name:
        return None
    cur = conn.cursor()
    cur.execute(
        "SELECT player_id FROM players WHERE full_name = ? AND (team_id = ? OR team_id IS NULL)",
        (full_name, team_id),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO players (full_name, team_id, playing_role, batting_style, bowling_style) VALUES (?, ?, NULL, NULL, NULL)",
        (full_name, team_id),
    )
    conn.commit()
    return cur.lastrowid


def get_or_create_team(conn, team_name):
    if not team_name:
        return None
    cur = conn.cursor()
    cur.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO teams (team_name, country) VALUES (?, ?)", (team_name, team_name))
    conn.commit()
    return cur.lastrowid


def find_local_match(conn, match_desc, team1_name, team2_name):
    """Match a Cricbuzz match to the row already inserted by fetch_real_data.py."""
    cur = conn.cursor()
    cur.execute(
        """SELECT m.match_id FROM matches m
           JOIN teams t1 ON m.team1_id = t1.team_id
           JOIN teams t2 ON m.team2_id = t2.team_id
           WHERE m.match_desc = ?
             AND ((t1.team_name = ? AND t2.team_name = ?) OR (t1.team_name = ? AND t2.team_name = ?))""",
        (match_desc, team1_name, team2_name, team2_name, team1_name),
    )
    row = cur.fetchone()
    return row[0] if row else None


def collect_completed_matches(data, limit):
    """Pull (cricbuzz_match_id, match_desc, team1_name, team2_name) for
    completed matches out of a recent-matches payload."""
    out = []
    if not data or "error" in data:
        return out
    for type_match in data.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})
            for match in wrapper.get("matches", []):
                info = match.get("matchInfo", {})
                status = info.get("status", "")
                if "won" not in status.lower():
                    continue  # only completed matches have full scorecards
                cricbuzz_id = info.get("matchId")
                team1 = info.get("team1", {}).get("teamName") or info.get("team1", {}).get("teamSName")
                team2 = info.get("team2", {}).get("teamName") or info.get("team2", {}).get("teamSName")
                match_desc = info.get("matchDesc", "")
                if cricbuzz_id and team1 and team2:
                    out.append((cricbuzz_id, match_desc, team1, team2))
                if len(out) >= limit:
                    return out
    return out


def parse_and_insert_innings(conn, scorecard_json, local_match_id):
    """Aggregate one match's batting + bowling into player_match_stats rows."""
    innings_list = scorecard_json.get("scoreCard", [])
    if not innings_list:
        return 0

    # player_key -> accumulated stats dict
    agg = {}

    def bucket(player_id, name, team_id):
        key = (player_id, team_id)
        if key not in agg:
            agg[key] = {
                "name": name, "team_id": team_id, "position": len(agg) + 1,
                "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
                "overs": 0.0, "runs_conceded": 0, "wickets": 0,
            }
        return agg[key]

    for innings in innings_list:
        bat_details = innings.get("batTeamDetails", {})
        bat_team_id = get_or_create_team(conn, bat_details.get("batTeamName"))
        batsmen = bat_details.get("batsmenData", {}) or {}
        for _, b in batsmen.items():
            name = b.get("batName") or b.get("name")
            if not name:
                continue
            entry = bucket(b.get("batId") or name, name, bat_team_id)
            entry["runs"] += int(b.get("runs", 0) or 0)
            entry["balls"] += int(b.get("balls", 0) or 0)
            entry["fours"] += int(b.get("fours", 0) or 0)
            entry["sixes"] += int(b.get("sixes", 0) or 0)

        bowl_details = innings.get("bowlTeamDetails", {})
        bowl_team_id = get_or_create_team(conn, bowl_details.get("bowlTeamName"))
        bowlers = bowl_details.get("bowlersData", {}) or {}
        for _, bo in bowlers.items():
            name = bo.get("bowlName") or bo.get("name")
            if not name:
                continue
            entry = bucket(bo.get("bowlerId") or name, name, bowl_team_id)
            entry["overs"] += float(bo.get("overs", 0) or 0)
            entry["runs_conceded"] += int(bo.get("runs", 0) or 0)
            entry["wickets"] += int(bo.get("wickets", 0) or 0)

    inserted = 0
    cur = conn.cursor()
    for (_, team_id), stats in agg.items():
        player_id = get_or_create_player(conn, stats["name"], team_id)
        strike_rate = round(stats["runs"] * 100.0 / stats["balls"], 2) if stats["balls"] else 0
        economy_rate = round(stats["runs_conceded"] / stats["overs"], 2) if stats["overs"] else 0
        cur.execute(
            """INSERT INTO player_match_stats
               (match_id, player_id, team_id, batting_position, runs_scored, balls_faced,
                fours, sixes, strike_rate, overs_bowled, runs_conceded, wickets_taken,
                economy_rate, catches, stumpings)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)""",
            (
                local_match_id, player_id, team_id, stats["position"],
                stats["runs"], stats["balls"], stats["fours"], stats["sixes"],
                strike_rate, stats["overs"], stats["runs_conceded"], stats["wickets"],
                economy_rate,
            ),
        )
        inserted += 1
    conn.commit()
    return inserted


def main():
    init_db()
    conn = get_connection()

    print("Fetching recent completed matches list...")
    recent = api_utils.get_recent_matches()
    candidates = collect_completed_matches(recent, MAX_MATCHES)
    print(f"Found {len(candidates)} completed match(es) to pull scorecards for "
          f"(limit={MAX_MATCHES}).")

    printed_sample = False
    total_stats_rows = 0

    for cricbuzz_id, match_desc, team1, team2 in candidates:
        local_match_id = find_local_match(conn, match_desc, team1, team2)
        if local_match_id is None:
            print(f"  Skipping '{match_desc}': not found in local matches table "
                  f"(run fetch_real_data.py again if this looks wrong).")
            continue

        # Skip if we already have stats for this match (avoid duplicate inserts on reruns)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM player_match_stats WHERE match_id = ?", (local_match_id,))
        if cur.fetchone()[0] > 0:
            print(f"  Skipping '{match_desc}': already has player stats.")
            continue

        print(f"  Fetching scorecard for '{match_desc}'...")
        scorecard = api_utils.get_match_scorecard(str(cricbuzz_id))

        if not scorecard or "error" in scorecard:
            print(f"    -> error: {scorecard.get('error') if scorecard else 'no data'}")
            continue

        if not printed_sample:
            printed_sample = True
            keys_preview = json.dumps(list(scorecard.keys()))
            print(f"    (response top-level keys: {keys_preview})")

        try:
            n = parse_and_insert_innings(conn, scorecard, local_match_id)
            print(f"    -> inserted stats for {n} player(s)")
            total_stats_rows += n
        except Exception as e:
            print(f"    -> could not parse this scorecard: {e}")

    conn.close()
    print(f"\nDone. {total_stats_rows} player_match_stats row(s) inserted total.")
    print("If this came out as 0 and you saw parsing errors above, the API's exact "
          "scorecard field names may differ from what this script expects — share "
          "the printed sample keys and I'll adjust the parsing.")


if __name__ == "__main__":
    main()

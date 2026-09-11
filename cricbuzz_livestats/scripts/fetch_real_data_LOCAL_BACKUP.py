"""
Fetches REAL match data from the Cricbuzz API and loads it into the local
SQLite database (teams, venues, series, matches, player_match_stats).

Run it from the project's root folder:
    python scripts/fetch_real_data.py

What it does:
1. Calls /matches/v1/recent (finished matches — these have full scorecards)
2. For each match: saves the series, both teams, and the venue
3. Calls the scorecard endpoint for that match and saves each batsman's/
   bowler's numbers into player_match_stats (creating the player row if
   it doesn't exist yet)

NOTE: The Cricbuzz API's exact JSON layout can vary slightly by endpoint
version. This script uses .get() everywhere and skips anything it can't
find instead of crashing, and it prints what it's doing as it goes. If a
match gets skipped, re-run with DEBUG=1 to dump the raw JSON so we can see
what changed:
    DEBUG=1 python scripts/fetch_real_data.py
"""

import os
import re
import sys
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import api_utils
from utils.db_connection import get_connection, init_db

DEBUG = os.getenv("DEBUG", "0") == "1"


def dbg(label, data):
    if DEBUG:
        fname = f"debug_{label}.json"
        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
        print(f"   (debug) saved raw response to {fname}")


def get_or_create_team(conn, team_name, country=None):
    if not team_name:
        return None
    cur = conn.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO teams (team_name, country) VALUES (?, ?)",
        (team_name, country or team_name),
    )
    return cur.lastrowid


def get_or_create_venue(conn, venue_name, city=None, country=None, capacity=None):
    if not venue_name:
        return None
    cur = conn.execute("SELECT venue_id FROM venues WHERE venue_name = ?", (venue_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO venues (venue_name, city, country, capacity) VALUES (?, ?, ?, ?)",
        (venue_name, city, country, capacity),
    )
    return cur.lastrowid


def get_or_create_series(conn, series_name, host_country=None, match_type=None):
    if not series_name:
        return None
    cur = conn.execute("SELECT series_id FROM series WHERE series_name = ?", (series_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO series (series_name, host_country, match_type, start_date, total_matches) VALUES (?, ?, ?, ?, ?)",
        (series_name, host_country, match_type, None, None),
    )
    return cur.lastrowid


def get_or_create_player(conn, full_name, team_id=None, role=None):
    if not full_name:
        return None
    cur = conn.execute("SELECT player_id FROM players WHERE full_name = ?", (full_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO players (full_name, team_id, playing_role, batting_style, bowling_style) VALUES (?, ?, ?, ?, ?)",
        (full_name, team_id, role, None, None),
    )
    return cur.lastrowid


def parse_winner_from_status(status_text, team1_name, team2_name):
    """Cricbuzz's 'status' field reads like 'India won by 45 runs'."""
    if not status_text:
        return None, None, None
    m = re.search(r"^(.*?)\s+won by\s+(\d+)\s+(run|runs|wkt|wkts|wicket|wickets)", status_text, re.I)
    if not m:
        return None, None, None
    winner_name, margin, unit = m.group(1).strip(), int(m.group(2)), m.group(3).lower()
    victory_type = "runs" if "run" in unit else "wickets"
    winner = winner_name if winner_name in (team1_name, team2_name) else None
    return winner, margin, victory_type


def save_match(conn, match_info, match_score=None):
    match_id = match_info.get("matchId")
    team1 = match_info.get("team1", {})
    team2 = match_info.get("team2", {})
    venue = match_info.get("venueInfo", {})

    team1_id = get_or_create_team(conn, team1.get("teamName") or team1.get("teamSName"))
    team2_id = get_or_create_team(conn, team2.get("teamName") or team2.get("teamSName"))
    venue_id = get_or_create_venue(
        conn, venue.get("ground"), venue.get("city"), venue.get("country")
    )
    series_id = get_or_create_series(
        conn, match_info.get("seriesName"), match_type=match_info.get("matchFormat")
    )

    start_ms = match_info.get("startDate")
    match_date = None
    if start_ms:
        try:
            match_date = time.strftime("%Y-%m-%d", time.gmtime(int(start_ms) / 1000))
        except (ValueError, TypeError):
            pass

    toss = match_info.get("tossResults", {})
    toss_winner_id = None
    if toss.get("tossWinnerName") in (team1.get("teamName"), team2.get("teamName")):
        toss_winner_id = team1_id if toss.get("tossWinnerName") == team1.get("teamName") else team2_id
    toss_decision = (toss.get("decision") or "").lower() or None

    winner_name, margin, victory_type = parse_winner_from_status(
        match_info.get("status"), team1.get("teamName"), team2.get("teamName")
    )
    winning_team_id = None
    if winner_name == team1.get("teamName"):
        winning_team_id = team1_id
    elif winner_name == team2.get("teamName"):
        winning_team_id = team2_id

    cur = conn.execute("SELECT match_id FROM matches WHERE match_id = ?", (match_id,))
    if cur.fetchone():
        print(f"   match {match_id} already saved, skipping insert")
        return match_id, team1_id, team2_id

    conn.execute(
        """INSERT INTO matches (match_id, series_id, match_desc, team1_id, team2_id, venue_id,
               match_date, match_format, winning_team_id, victory_margin, victory_type,
               toss_winner_id, toss_decision)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            match_id, series_id, match_info.get("matchDesc"), team1_id, team2_id, venue_id,
            match_date, match_info.get("matchFormat"), winning_team_id, margin, victory_type,
            toss_winner_id, toss_decision,
        ),
    )
    return match_id, team1_id, team2_id


def save_scorecard(conn, match_id, team1_id, team2_id, team1_name, team2_name):
    card = api_utils.get_match_scorecard(str(match_id))
    dbg(f"scorecard_{match_id}", card)
    if not card or "error" in card:
        print(f"   could not fetch scorecard for match {match_id}: {card.get('error') if card else 'no data'}")
        return

    for innings in card.get("scoreCard", []):
        bat_team = innings.get("batTeamDetails", {})
        bat_team_name = bat_team.get("batTeamName")
        bat_team_id = team1_id if bat_team_name == team1_name else team2_id if bat_team_name == team2_name else None

        for _, batsman in (bat_team.get("batsmenData") or {}).items():
            player_id = get_or_create_player(conn, batsman.get("batName"), bat_team_id)
            if player_id is None:
                continue
            conn.execute(
                """INSERT INTO player_match_stats
                   (match_id, player_id, team_id, runs_scored, balls_faced, fours, sixes, strike_rate)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    match_id, player_id, bat_team_id,
                    batsman.get("runs", 0), batsman.get("balls", 0),
                    batsman.get("fours", 0), batsman.get("sixes", 0),
                    batsman.get("strikeRate", 0),
                ),
            )

        bowl_team = innings.get("bowlTeamDetails", {})
        bowl_team_name = bowl_team.get("bowlTeamName")
        bowl_team_id = team1_id if bowl_team_name == team1_name else team2_id if bowl_team_name == team2_name else None

        for _, bowler in (bowl_team.get("bowlersData") or {}).items():
            player_id = get_or_create_player(conn, bowler.get("bowlName"), bowl_team_id)
            if player_id is None:
                continue
            conn.execute(
                """INSERT INTO player_match_stats
                   (match_id, player_id, team_id, overs_bowled, runs_conceded, wickets_taken, economy_rate)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    match_id, player_id, bowl_team_id,
                    bowler.get("overs", 0), bowler.get("runs", 0),
                    bowler.get("wickets", 0), bowler.get("economy", 0),
                ),
            )


def main():
    init_db()
    conn = get_connection()

    print("Fetching recent matches from Cricbuzz API...")
    data = api_utils.get_recent_matches()
    dbg("recent_matches", data)

    if not data or "error" in data:
        print("ERROR:", data.get("error") if data else "No response from API.")
        print("Check that RAPIDAPI_KEY is set correctly in your .env file.")
        return

    saved = 0
    for type_match in data.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})
            for match in wrapper.get("matches", []):
                info = match.get("matchInfo", {})
                if not info.get("matchId"):
                    continue
                desc = f"{info.get('team1', {}).get('teamName')} vs {info.get('team2', {}).get('teamName')} — {info.get('matchDesc')}"
                print(f"Saving match: {desc}")
                match_id, team1_id, team2_id = save_match(conn, info)
                conn.commit()
                save_scorecard(
                    conn, match_id, team1_id, team2_id,
                    info.get("team1", {}).get("teamName"),
                    info.get("team2", {}).get("teamName"),
                )
                conn.commit()
                saved += 1

    conn.close()
    print(f"\nDone. {saved} match(es) processed into database/cricbuzz.db")
    print("Open the SQL Analytics page in the app to query this real data.")


if __name__ == "__main__":
    main()

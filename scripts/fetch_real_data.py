"""
scripts/fetch_real_data.py

Fetches real match data from the Cricbuzz API (via utils/api_utils.py) and
loads it into the local SQLite database (database/cricbuzz.db) using the
existing utils/db_connection.py helpers.

Run this from the PROJECT ROOT (same folder as Home.py):
    python scripts/fetch_real_data.py

Requires a valid RAPIDAPI_KEY in your .env file.

NOTE on scope: the live/recent/upcoming endpoints give match, team, venue
and series info, so this script fills teams / venues / series / matches.
Per-player batting & bowling stats (player_match_stats table) need the
match scorecard endpoint, which is not fetched here to avoid burning
through a free-tier API quota. Load database/seed_data.sql (see
load_sample_data() in utils/db_connection.py) if you want the
Player Stats charts (top run scorers, wicket takers) to have data too.
"""

import os
import sys
import time

# Make "utils" importable when this script is run as `python scripts/fetch_real_data.py`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import api_utils
from utils.db_connection import get_connection, init_db

FORMAT_MAP = {"TEST": "Test", "ODI": "ODI", "T20": "T20I", "T20I": "T20I"}


def normalize_format(fmt):
    if not fmt:
        return None
    return FORMAT_MAP.get(str(fmt).upper(), fmt)


def get_or_create_team(conn, team_name, country=None):
    if not team_name:
        return None
    cur = conn.cursor()
    cur.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO teams (team_name, country) VALUES (?, ?)",
        (team_name, country or team_name),
    )
    conn.commit()
    return cur.lastrowid


def get_or_create_venue(conn, venue_info):
    if not venue_info:
        return None
    name = venue_info.get("ground") or venue_info.get("venueName") or "Unknown Venue"
    city = venue_info.get("city", "")
    country = venue_info.get("country", "")
    cur = conn.cursor()
    cur.execute(
        "SELECT venue_id FROM venues WHERE venue_name = ? AND city = ?", (name, city)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO venues (venue_name, city, country, capacity) VALUES (?, ?, ?, ?)",
        (name, city, country, None),
    )
    conn.commit()
    return cur.lastrowid


def get_or_create_series(conn, series_name):
    if not series_name:
        return None
    cur = conn.cursor()
    cur.execute("SELECT series_id FROM series WHERE series_name = ?", (series_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """INSERT INTO series (series_name, host_country, match_type, start_date, total_matches)
           VALUES (?, NULL, NULL, NULL, NULL)""",
        (series_name,),
    )
    conn.commit()
    return cur.lastrowid


def parse_result(conn, team1, team2, status_text):
    """Best-effort parse of Cricbuzz's free-text status field,
    e.g. 'India won by 6 wkts' or 'Australia won by 45 runs'."""
    if not status_text or "won by" not in status_text:
        return None, None, None
    for t in (team1, team2):
        name = t.get("teamName") or t.get("teamSName")
        if name and status_text.startswith(name):
            winning_team_id = get_or_create_team(conn, name)
            tail = status_text.split("won by")[-1].strip()
            parts = tail.split()
            margin = None
            if parts:
                try:
                    margin = int(parts[0])
                except ValueError:
                    margin = None
            v_type = "wickets" if "wkt" in tail else ("runs" if "run" in tail else None)
            return winning_team_id, margin, v_type
    return None, None, None


def insert_match(conn, series_id, match_info):
    team1 = match_info.get("team1", {})
    team2 = match_info.get("team2", {})
    team1_id = get_or_create_team(conn, team1.get("teamName") or team1.get("teamSName"))
    team2_id = get_or_create_team(conn, team2.get("teamName") or team2.get("teamSName"))
    venue_id = get_or_create_venue(conn, match_info.get("venueInfo"))

    match_desc = match_info.get("matchDesc", "")
    match_format = normalize_format(match_info.get("matchFormat"))

    match_date = None
    start_ms = match_info.get("startDate")
    if start_ms:
        try:
            match_date = time.strftime("%Y-%m-%d", time.localtime(int(start_ms) / 1000))
        except (ValueError, TypeError):
            match_date = None

    status_text = match_info.get("status", "")
    winning_team_id, victory_margin, victory_type = parse_result(conn, team1, team2, status_text)

    cur = conn.cursor()
    cur.execute(
        "SELECT match_id FROM matches WHERE match_desc = ? AND team1_id = ? AND team2_id = ?",
        (match_desc, team1_id, team2_id),
    )
    existing = cur.fetchone()
    if existing:
        return existing[0], False

    cur.execute(
        """INSERT INTO matches
           (series_id, match_desc, team1_id, team2_id, venue_id, match_date, match_format,
            winning_team_id, victory_margin, victory_type, toss_winner_id, toss_decision)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)""",
        (
            series_id, match_desc, team1_id, team2_id, venue_id, match_date, match_format,
            winning_team_id, victory_margin, victory_type,
        ),
    )
    conn.commit()
    return cur.lastrowid, True


def process_matches_payload(conn, data, label):
    if not data:
        print(f"  [{label}] skipped: no data returned")
        return 0
    if "error" in data:
        print(f"  [{label}] skipped: {data['error']}")
        return 0

    inserted = 0
    for type_match in data.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})
            series_id = get_or_create_series(conn, wrapper.get("seriesName"))
            for match in wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                _, was_new = insert_match(conn, series_id, match_info)
                if was_new:
                    inserted += 1
    return inserted


def main():
    print("Initializing database (creates tables only if missing)...")
    init_db()
    conn = get_connection()

    try:
        for label, fetch_fn in [
            ("recent", api_utils.get_recent_matches),
            ("upcoming", api_utils.get_upcoming_matches),
            ("live", api_utils.get_live_matches),
        ]:
            print(f"Fetching {label} matches from Cricbuzz API...")
            data = fetch_fn()
            n = process_matches_payload(conn, data, label)
            print(f"  -> {n} new match(es) inserted")
    finally:
        conn.close()

    print("\nDone. Open the SQL Analytics / Analytics Overview / Visualizations pages to see it.")
    print(
        "Note: this fills teams, venues, series and matches. Player-level batting/"
        "bowling stats need scorecard data per match, which isn't fetched here to "
        "save API quota — ask if you want that added too."
    )


if __name__ == "__main__":
    main()

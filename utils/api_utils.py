"""
Thin wrapper around the Cricbuzz Cricket API (hosted on RapidAPI).
Get your free API key here: https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/
Steps to get the key are in README.md.

We read the key from an environment variable (RAPIDAPI_KEY) so it is
never hard-coded / committed to git. See .env.example.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # reads a local .env file if present

API_KEY = os.getenv("RAPIDAPI_KEY", "")
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com",
}


def _get(endpoint: str, params: dict | None = None):
    """Internal helper: does the actual GET request with error handling."""
    if not API_KEY:
        return {"error": "RAPIDAPI_KEY not set. Add it to your .env file."}
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_live_matches():
    """Live + recent + upcoming matches."""
    return _get("/matches/v1/live")


def get_recent_matches():
    return _get("/matches/v1/recent")


def get_upcoming_matches():
    return _get("/matches/v1/upcoming")


def get_match_scorecard(match_id: str):
    return _get(f"/mcenter/v1/{match_id}/scard")


def get_top_stats(stats_type: str = "mostRuns"):
    """
    stats_type examples: mostRuns, mostWickets, highestScore, bestBowling
    (see the API docs on RapidAPI for the exact list per format).
    """
    return _get(f"/stats/v1/topstats/0", params={"statsType": stats_type})


def get_player_info(player_id: str):
    return _get(f"/stats/v1/player/{player_id}")

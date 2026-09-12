import os
import requests
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

# .env location
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"


def get_api_headers():
    api_key = os.getenv("RAPIDAPI_KEY")

    if not api_key:
        return None

    return {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }


def _get(endpoint, params=None):

    headers = get_api_headers()

    if headers is None:
        return {
            "error": "RAPIDAPI_KEY not found in .env"
        }

    try:
        url = f"{BASE_URL}{endpoint}"

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        # Debug information
        if response.status_code == 403:
            return {
                "error": (
                    "403 Forbidden. "
                    "RapidAPI key invalid OR API subscription is inactive."
                )
            }

        if response.status_code == 401:
            return {
                "error": "401 Unauthorized. Check RapidAPI API key."
            }

        if response.status_code == 429:
            return {
                "error": "429 Too Many Requests. API quota exceeded."
            }

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        return {
            "error": f"API Request Failed: {str(e)}"
        }


@st.cache_data(ttl=300)
def get_live_matches():
    return _get("/matches/v1/live")


@st.cache_data(ttl=300)
def get_recent_matches():
    return _get("/matches/v1/recent")


@st.cache_data(ttl=300)
def get_upcoming_matches():
    return _get("/matches/v1/upcoming")


@st.cache_data(ttl=300)
def get_match_scorecard(match_id):
    return _get(f"/mcenter/v1/{match_id}/scard")


@st.cache_data(ttl=300)
def get_top_stats(stats_type="mostRuns", match_type="t20"):
    return _get(
        "/stats/v1/topstats/0",
        params={"statsType": stats_type, "matchType": match_type}
    )


@st.cache_data(ttl=300)
def get_player_info(player_id):
    return _get(f"/stats/v1/player/{player_id}")
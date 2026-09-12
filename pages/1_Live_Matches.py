import streamlit as st
from utils.theme import apply_theme
apply_theme()
from utils import api_utils

st.set_page_config(page_title="Live Matches", page_icon="🔴", layout="wide")
st.title("🔴 Live Matches")

tab1, tab2, tab3 = st.tabs(["Live", "Recent", "Upcoming"])


def show_matches(data):
    if not data:
        st.warning("No data returned.")
        return
    if "error" in data:
        st.error(data["error"])
        return
    # Cricbuzz returns nested typeMatches -> seriesMatches -> matches
    type_matches = data.get("typeMatches", [])
    if not type_matches:
        st.info("No matches found right now.")
        return
    for type_match in type_matches:
        st.markdown(f"### {type_match.get('matchType', '')}")
        for series_match in type_match.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})
            st.markdown(f"**{wrapper.get('seriesName', '')}**")
            for match in wrapper.get("matches", []):
                info = match.get("matchInfo", {})
                team1 = info.get("team1", {}).get("teamName", "Team 1")
                team2 = info.get("team2", {}).get("teamName", "Team 2")
                status = match.get("matchScore", {})
                with st.container(border=True):
                    st.write(f"**{team1} vs {team2}** — {info.get('matchDesc', '')}")
                    st.caption(info.get("status", ""))

with tab1:
    if st.button("🔄 Refresh live matches"):
        api_utils.get_live_matches.clear()  # sirf isi function ka cache clear karo
    show_matches(api_utils.get_live_matches())

with tab2:
    show_matches(api_utils.get_recent_matches())

with tab3:
    show_matches(api_utils.get_upcoming_matches())
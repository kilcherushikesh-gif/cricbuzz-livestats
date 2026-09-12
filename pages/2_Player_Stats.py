import streamlit as st
from utils.theme import apply_theme, hero
from utils.queries import get_top_stats_from_db
apply_theme()

st.set_page_config(page_title="Player Stats", page_icon="📊", layout="wide")
st.title("📊 Top Player Stats")

col1, col2 = st.columns(2)

with col1:
    stat_type = st.selectbox(
        "Choose a stat category",
        ["mostRuns", "mostWickets", "highestScore", "bestBowling"],
    )

with col2:
    match_format = st.selectbox(
        "Choose match format",
        ["Test", "ODI", "T20I"],
        index=2,
    )

df = get_top_stats_from_db(stat_type, match_format)

if df.empty:
    st.info("No stats data found for this combination.")
else:
    st.dataframe(df, use_container_width=True)
import streamlit as st
import pandas as pd
from utils.theme import apply_theme, hero
from utils import api_utils
apply_theme()

st.set_page_config(page_title="Player Stats", page_icon="📊", layout="wide")
st.title("📊 Top Player Stats")

stat_type = st.selectbox(
    "Choose a stat category",
    ["mostRuns", "mostWickets", "highestScore", "bestBowling"],
)

data = api_utils.get_top_stats(stat_type)

if "error" in data:
    st.error(data["error"])
else:
    rows = data.get("headers", [])
    values = data.get("values", [])
    if values:
        try:
            df = pd.DataFrame([v.get("values", []) for v in values], columns=rows if rows else None)
            st.dataframe(df, use_container_width=True)
        except Exception:
            st.json(data)
    else:
        st.json(data)
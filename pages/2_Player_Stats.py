import streamlit as st
import pandas as pd
from utils import api_utils

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
    values = data.get("values", [])  # exact keys depend on the live API response shape
    if values:
        try:
            df = pd.DataFrame([v.get("values", []) for v in values], columns=rows if rows else None)
            st.dataframe(df, use_container_width=True)
        except Exception:
            st.json(data)  # fallback: show raw JSON if the shape differs
    else:
        st.json(data)

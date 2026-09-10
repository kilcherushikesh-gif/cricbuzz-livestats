"""
utils/theme.py

Shared visual styling for every page. Call apply_theme() right after
st.set_page_config() on each page, and use hero(title, subtitle) instead
of st.title() for the big page header.
"""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* ---- Hero banner used at the top of every page ---- */
        .hero-banner {
            background: linear-gradient(135deg, #0b3d2e 0%, #157347 55%, #2ecc71 100%);
            padding: 1.8rem 2.2rem;
            border-radius: 16px;
            margin-bottom: 1.6rem;
            box-shadow: 0 10px 28px rgba(11, 61, 46, 0.25);
        }
        .hero-banner h1 {
            color: #ffffff !important;
            margin: 0;
            font-size: 2.1rem;
            font-weight: 700;
        }
        .hero-banner p {
            color: #eafaf1;
            margin-top: 0.35rem;
            margin-bottom: 0;
            font-size: 1.02rem;
        }

        /* ---- Metric cards (st.metric) ---- */
        div[data-testid="stMetric"] {
            background: linear-gradient(155deg, #ffffff, #eef8f2);
            border: 1px solid #dceee2;
            border-radius: 14px;
            padding: 0.9rem 1.1rem;
            box-shadow: 0 4px 14px rgba(21, 115, 71, 0.08);
        }
        div[data-testid="stMetricValue"] {
            color: #157347;
            font-weight: 700;
        }
        div[data-testid="stMetricLabel"] {
            color: #4b5f56;
        }

        /* ---- Bordered containers (match cards, etc.) ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
            border: 1px solid #e2eae5 !important;
            transition: box-shadow 0.15s ease-in-out, transform 0.15s ease-in-out;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            transform: translateY(-1px);
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background: #0b3d2e;
        }
        section[data-testid="stSidebar"] * {
            color: #eafaf1 !important;
        }
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] a {
            color: #eafaf1 !important;
        }

        /* ---- Buttons ---- */
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 8px;
            border: none;
            background: #157347;
            color: white;
            font-weight: 600;
            padding: 0.5rem 1.3rem;
            transition: background 0.15s ease-in-out;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background: #0f5c38;
            color: white;
        }

        /* ---- Dataframes / tables ---- */
        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e2eae5;
        }

        /* ---- Tabs ---- */
        button[data-baseweb="tab"] {
            font-weight: 600;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #157347 !important;
            border-bottom-color: #157347 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str = ""):
    """Gradient header banner. Use instead of st.title()."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

import streamlit as st

def apply_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

        * { font-family: 'Inter', sans-serif !important; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif !important; }

        /* Flat solid background — no stripes, no noise */
        .stApp { background: #0A1F16 !important; }
        .main .block-container { background: transparent !important; padding-top: 2rem !important; }

        /* Sidebar — clean, single solid border, no dashes */
        section[data-testid="stSidebar"] {
            background: #0D2419 !important;
            border-right: 1px solid #1E3D2B !important;
        }
        section[data-testid="stSidebar"] a {
            color: #C9D6C7 !important;
            font-size: 0.95rem !important;
            padding: 8px 10px !important;
            border-radius: 6px !important;
        }
        section[data-testid="stSidebar"] a:hover {
            color: #F4F1E8 !important;
            background: #14301F !important;
        }

        /* Text */
        h1, h2, h3, h4, h5, h6 { color: #F4F1E8 !important; }
        p, li, span, div { color: #B9C7B8 !important; }
        label { color: #8CA491 !important; font-size: 0.85rem !important; }

        /* Metric cards — flat panel, single left accent bar, no busy borders */
        [data-testid="metric-container"] {
            background: #10281B !important;
            border: none !important;
            border-left: 3px solid #E8C468 !important;
            border-radius: 6px !important;
            padding: 1rem 1.2rem !important;
        }
        [data-testid="metric-container"] label { color: #8CA491 !important; }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #F4F1E8 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 1.9rem !important;
            font-weight: 600 !important;
        }

        /* Buttons — the one bright accent color, used sparingly */
        .stButton > button {
            background: #E14B3D !important;
            color: #F4F1E8 !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.6rem !important;
            transition: background 0.2s !important;
        }
        .stButton > button:hover {
            background: #C63A2E !important;
        }

        /* Inputs */
        input, textarea {
            background: #10281B !important;
            color: #F4F1E8 !important;
            border: 1px solid #234433 !important;
            border-radius: 6px !important;
        }
        input:focus { border-color: #E8C468 !important; }
        input::placeholder { color: #5C7864 !important; }

        /* Dropdowns */
        [data-baseweb="select"] > div {
            background: #10281B !important;
            border: 1px solid #234433 !important;
            border-radius: 6px !important;
            color: #F4F1E8 !important;
        }
        [data-baseweb="select"] span { color: #F4F1E8 !important; }
        [data-baseweb="popover"] { background: #10281B !important; }
        [data-baseweb="popover"] li {
            color: #F4F1E8 !important;
            background: #10281B !important;
        }
        [data-baseweb="popover"] li:hover {
            background: #1E3D2B !important;
            color: #F4F1E8 !important;
        }

        /* Tabs — clean underline style instead of filled pill */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid #1E3D2B !important;
            gap: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #8CA491 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 500 !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            color: #F4F1E8 !important;
            border-bottom: 2px solid #E14B3D !important;
            font-weight: 600 !important;
        }

        /* Dataframe */
        .stDataFrame {
            border: 1px solid #1E3D2B !important;
            border-radius: 8px !important;
        }

        hr { border-color: #1E3D2B !important; }

        .stDateInput input { color: #F4F1E8 !important; }
        .stNumberInput input { color: #F4F1E8 !important; }

        [data-testid="stForm"] {
            background: #0D2419 !important;
            border: 1px solid #1E3D2B !important;
            border-radius: 10px !important;
            padding: 1.5rem !important;
        }

        /* Live pulse dot */
        @keyframes pulse-ball {
            0% { box-shadow: 0 0 0 0 rgba(225,75,61,0.55); }
            70% { box-shadow: 0 0 0 9px rgba(225,75,61,0); }
            100% { box-shadow: 0 0 0 0 rgba(225,75,61,0); }
        }
        .live-dot {
            display: inline-block;
            width: 9px; height: 9px;
            background: #E14B3D;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse-ball 1.6s infinite;
        }
        </style>
    """, unsafe_allow_html=True)


def hero(title, subtitle=""):
    st.markdown(f"""
        <div style='
            position: relative;
            overflow: hidden;
            background: #0D2419;
            padding: 2.2rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            border-left: 4px solid #E8C468;
        '>
            <h1 style='color: #F4F1E8 !important; margin: 0; font-size: 2.2rem; font-weight: 700; font-family: "Space Grotesk", sans-serif;'>{title}</h1>
            <p style='color: #8CA491 !important; margin: 0.5rem 0 0 0; font-size: 0.95rem;'>{subtitle}</p>

            <svg width="70" height="70" viewBox="0 0 150 150"
                 style="position:absolute; right:24px; top:50%; transform:translateY(-50%); opacity:0.85;">
                <g transform="rotate(-18 75 75)">
                    <rect x="60" y="8" width="20" height="72" rx="9" fill="#E8C468"/>
                    <rect x="66" y="80" width="8" height="38" rx="3" fill="#7a4a24"/>
                    <rect x="63" y="116" width="14" height="10" rx="3" fill="#4a2e16"/>
                </g>
                <circle cx="115" cy="108" r="16" fill="#E14B3D"/>
            </svg>
        </div>
    """, unsafe_allow_html=True)


def live_badge(text="LIVE"):
    st.markdown(f"""
        <div style='display:flex; align-items:center; margin-bottom:0.5rem;'>
            <span class='live-dot'></span>
            <span style='color:#E14B3D; font-weight:600; font-family:"Space Grotesk", sans-serif; letter-spacing:0.5px;'>{text}</span>
        </div>
    """, unsafe_allow_html=True)
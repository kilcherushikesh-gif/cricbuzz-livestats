import streamlit as st

def apply_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        
        * { font-family: 'Poppins', sans-serif !important; }
        
        /* Main background */
        .stApp { background: #0a0a0a !important; }
        .main .block-container { background: #0a0a0a !important; }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #111111 !important;
            border-right: 2px solid #00ff88 !important;
        }
        section[data-testid="stSidebar"] a {
            color: #ffffff !important;
            font-size: 1rem !important;
            padding: 8px 0 !important;
        }
        section[data-testid="stSidebar"] a:hover {
            color: #00ff88 !important;
        }
        
        /* All text */
        h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
        p, li, span, div { color: #cccccc !important; }
        label { color: #aaaaaa !important; font-size: 0.85rem !important; }
        
        /* Metric cards */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #1a1a1a, #222222) !important;
            border: 1px solid #00ff88 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 0 20px rgba(0,255,136,0.1) !important;
        }
        [data-testid="metric-container"] label { color: #00ff88 !important; }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #00ff88, #00cc6a) !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            padding: 0.5rem 2rem !important;
            transition: all 0.3s !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0,255,136,0.4) !important;
        }
        
        /* Input fields */
        input, textarea {
            background: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
        }
        input:focus { border-color: #00ff88 !important; }
        input::placeholder { color: #555555 !important; }
        
        /* Dropdowns */
        [data-baseweb="select"] > div {
            background: #1a1a1a !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            color: #ffffff !important;
        }
        [data-baseweb="select"] span { color: #ffffff !important; }
        [data-baseweb="popover"] { background: #1a1a1a !important; }
        [data-baseweb="popover"] li {
            color: #ffffff !important;
            background: #1a1a1a !important;
        }
        [data-baseweb="popover"] li:hover {
            background: #00ff88 !important;
            color: #000000 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: #111111 !important;
            border-radius: 10px !important;
            padding: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #888888 !important;
            border-radius: 8px !important;
        }
        .stTabs [aria-selected="true"] {
            background: #00ff88 !important;
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        /* Dataframe */
        .stDataFrame {
            border: 1px solid #222222 !important;
            border-radius: 10px !important;
        }
        
        /* Divider */
        hr { border-color: #222222 !important; }
        
        /* Date input */
        .stDateInput input { color: #ffffff !important; }
        
        /* Number input */
        .stNumberInput input { color: #ffffff !important; }
        
        /* Form */
        [data-testid="stForm"] {
            background: #111111 !important;
            border: 1px solid #222222 !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

def hero(title, subtitle=""):
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #0d1f0d 0%, #0a2a1a 50%, #0d1f0d 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid #00ff88;
            box-shadow: 0 0 40px rgba(0,255,136,0.15);
        '>
            <h1 style='color: #00ff88 !important; margin: 0; font-size: 2.5rem; font-weight: 700;'>{title}</h1>
            <p style='color: #aaaaaa !important; margin: 0.5rem 0 0 0; font-size: 1rem;'>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)
# 🏏 Cricbuzz LiveStats — Setup Guide (Step-by-Step)

Ye project **Streamlit + SQL + Cricbuzz API** use karke ek cricket analytics
dashboard banata hai. Neeche bilkul shuru se steps diye hain.

## Project structure

```
cricbuzz_livestats/
├── Home.py                     ← ye file run karni hai (main entry)
├── requirements.txt
├── .env.example
├── database/
│   ├── schema.sql               ← tables banane ka SQL
│   └── seed_data.sql            ← testing ke liye sample rows
├── utils/
│   ├── db_connection.py         ← saara DB code yahin hai
│   ├── api_utils.py             ← Cricbuzz API calls yahin hain
│   └── queries.py                ← 25 practice SQL queries
└── pages/
    ├── 1_Live_Matches.py
    ├── 2_Player_Stats.py
    ├── 3_SQL_Analytics.py
    └── 4_CRUD_Operations.py
```

## Step 1 — Python install karo (agar pehle se nahi hai)

Python 3.9+ chahiye. Terminal me check karo:
```bash
python --version
```
Agar nahi hai to https://www.python.org/downloads/ se install karo.

## Step 2 — Project folder me jao aur virtual environment banao

```bash
cd cricbuzz_livestats
python -m venv venv
```

Activate karo:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

(Terminal me `(venv)` dikhega — matlab activate ho gaya.)

## Step 3 — Dependencies install karo

```bash
pip install -r requirements.txt
```

## Step 4 — Cricbuzz API key lo (RapidAPI se, free hai)

1. https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/ par jao
2. RapidAPI par account banao / login karo (free)
3. "Subscribe" button dabao aur **free/basic plan** choose karo
4. Left side me "X-RapidAPI-Key" dikhega — wo copy karo

## Step 5 — API key ko `.env` file me daalo

`.env.example` file ko copy karke naam do `.env`:
```bash
cp .env.example .env
```
Ab `.env` file open karke apni key paste karo:
```
RAPIDAPI_KEY=yaha_apni_key_paste_karo
```

⚠️ `.env` file ko kabhi GitHub par push mat karna — isme secret key hoti hai.

## Step 6 — App run karo

```bash
streamlit run Home.py
```

Ye command chalte hi browser me automatically ek tab khulega
(`http://localhost:8501`). Sidebar me 4 pages dikhenge:

- **🔴 Live Matches** — API se live/recent/upcoming matches (API key chahiye)
- **📊 Player Stats** — API se top stats (API key chahiye)
- **🧮 SQL Analytics** — 25 practice queries, sample data ke saath turant kaam karega (API key ki zaroorat nahi)
- **⚙️ CRUD Operations** — players add/update/delete karo (API key ki zaroorat nahi)

Pehli baar run karne par `database/cricbuzz.db` (SQLite file) apne aap ban
jayegi, schema + sample data ke saath — koi extra setup nahi chahiye.

## Step 7 — Apna khud ka data daalna ho to

Abhi jo data hai wo sirf testing ke liye chhota sa dummy data hai
(`database/seed_data.sql`). Real data chahiye to:
- `utils/api_utils.py` ke functions call karke API se data lao
- Us data ko `players`, `matches`, `player_match_stats` tables me insert karo
  (CRUD page se manually, ya ek Python script likh ke bulk insert karo)

## Common problems (agar error aaye)

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: streamlit` | `pip install -r requirements.txt` dubara chalao (venv activate hona chahiye) |
| Live Matches page pe "RAPIDAPI_KEY not set" | `.env` file check karo, key sahi se paste hui ya nahi |
| API se koi data nahi aa raha | RapidAPI dashboard me check karo subscription active hai ya nahi |
| Port already in use | `streamlit run Home.py --server.port 8502` try karo |

## Next steps (project ko aage badhane ke liye)

- Real match data ko API se fetch karke database me store karo
- SQLite ki jagah PostgreSQL/MySQL use karna ho to sirf
  `utils/db_connection.py` ka `get_connection()` function badlo — baaki
  poora app waise hi chalega
- Charts add karo (`st.bar_chart`, `st.line_chart`) SQL Analytics page par
- Deploy karne ke liye Streamlit Community Cloud use kar sakte ho (free)

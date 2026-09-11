"""
scripts/add_player_status.py

Adds a 'status' column (Active / Retired / Injured / Unknown) to the
players table if it doesn't already exist.

Run ONCE from the project root:
    python scripts/add_player_status.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.db_connection import get_connection

conn = get_connection()
cur = conn.cursor()

# Check if column already exists
cur.execute("PRAGMA table_info(players)")
cols = [row[1] for row in cur.fetchall()]

if "status" in cols:
    print("'status' column already exists — nothing to do.")
else:
    cur.execute("ALTER TABLE players ADD COLUMN status TEXT DEFAULT 'Active'")
    conn.commit()
    print("Done! 'status' column added to players table with default value 'Active'.")

conn.close()
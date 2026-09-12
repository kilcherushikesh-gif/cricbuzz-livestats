import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database" / "cricbuzz.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = ["teams", "players", "venues", "series", "matches", "player_match_stats"]

print("=" * 50)
print("DATABASE STATUS REPORT")
print("=" * 50)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table:25s} : {count:>10,} rows")

print("=" * 50)

print("\nMatches by format:")
cursor.execute("SELECT match_format, COUNT(*) FROM matches GROUP BY match_format")
for fmt, cnt in cursor.fetchall():
    print(f"   {fmt:15s} : {cnt:>8,}")

cursor.execute("SELECT MIN(match_date), MAX(match_date) FROM matches")
min_date, max_date = cursor.fetchone()
print(f"\nMatch date range: {min_date} to {max_date}")

cursor.execute("""
    SELECT COUNT(DISTINCT m.match_id)
    FROM matches m
    LEFT JOIN player_match_stats s ON m.match_id = s.match_id
    WHERE s.match_id IS NULL
""")
missing = cursor.fetchone()[0]
print(f"\nMatches WITHOUT any player stats linked: {missing:,}")

conn.close()
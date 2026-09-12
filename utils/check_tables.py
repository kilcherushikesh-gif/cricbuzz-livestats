import sqlite3

conn = sqlite3.connect("database/cricbuzz.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in database:")
for t in tables:
    print("-", t[0])

for t in tables:
    table_name = t[0]
    print(f"\nColumns in '{table_name}':")
    cursor.execute(f"PRAGMA table_info({table_name})")
    for col in cursor.fetchall():
        print("   ", col[1], "-", col[2])

conn.close()
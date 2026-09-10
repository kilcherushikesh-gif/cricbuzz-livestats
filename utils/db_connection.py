"""
Central place for all database access.
Uses SQLite by default (zero setup, one file: database/cricbuzz.db).
If you later want PostgreSQL/MySQL, just swap get_connection() below —
every page in this app calls run_query()/run_action(), so the rest of
the code never has to change.
"""

import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "cricbuzz.db")


def get_connection():
    """Return a sqlite3 connection. Swap this function for Postgres/MySQL later."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """For SELECT queries. Returns a pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
    return df


def run_action(sql: str, params: tuple = ()) -> int:
    """For INSERT / UPDATE / DELETE. Returns number of affected rows."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        rows_affected = cur.rowcount
    finally:
        conn.close()
    return rows_affected


def init_db():
    """Create tables + load sample data if the DB doesn't exist yet."""
    if os.path.exists(DB_PATH):
        return
    conn = get_connection()
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "..", "database", "schema.sql")) as f:
        conn.executescript(f.read())
    with open(os.path.join(base_dir, "..", "database", "seed_data.sql")) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

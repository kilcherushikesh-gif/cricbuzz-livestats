"""
scripts/cleanup_sample_data.py

Removes ONLY the dummy/testing data that came from database/seed_data.sql
(Virat Kohli, Steve Smith, the 2 sample matches, etc.) while keeping any
real data pulled in by scripts/fetch_real_data.py.

Team rows (India, Australia, England, South Africa) are intentionally left
alone, because real matches you fetched may reuse those same team rows.
Venues and series are only deleted if no remaining match still points to
them, so nothing gets orphaned.

Run from the project root:
    python scripts/cleanup_sample_data.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.db_connection import get_connection

SAMPLE_PLAYER_NAMES = [
    "Virat Kohli", "Jasprit Bumrah", "Ravindra Jadeja",
    "Steve Smith", "Pat Cummins", "Joe Root", "Ben Stokes", "Kagiso Rabada",
]
SAMPLE_MATCH_DESCS = [
    "India vs Australia, 1st Test",
    "India vs England, 1st ODI",
]
SAMPLE_VENUE_NAMES = [
    "Melbourne Cricket Ground", "Eden Gardens", "Lord's", "Wankhede Stadium",
]
SAMPLE_SERIES_NAMES = [
    "Border-Gavaskar Trophy 2024", "India vs England ODI Series 2024",
]


def main():
    conn = get_connection()
    cur = conn.cursor()

    # 1) stats + matches from the sample dataset
    cur.execute(
        f"""DELETE FROM player_match_stats
            WHERE match_id IN (
                SELECT match_id FROM matches
                WHERE match_desc IN ({",".join("?" * len(SAMPLE_MATCH_DESCS))})
            )""",
        SAMPLE_MATCH_DESCS,
    )
    print(f"Deleted {cur.rowcount} sample player_match_stats row(s)")

    cur.execute(
        f"""DELETE FROM matches
            WHERE match_desc IN ({",".join("?" * len(SAMPLE_MATCH_DESCS))})""",
        SAMPLE_MATCH_DESCS,
    )
    print(f"Deleted {cur.rowcount} sample match(es)")

    # 2) sample players (also drops any leftover stats tied to them)
    cur.execute(
        f"""DELETE FROM player_match_stats
            WHERE player_id IN (
                SELECT player_id FROM players
                WHERE full_name IN ({",".join("?" * len(SAMPLE_PLAYER_NAMES))})
            )""",
        SAMPLE_PLAYER_NAMES,
    )
    cur.execute(
        f"""DELETE FROM players
            WHERE full_name IN ({",".join("?" * len(SAMPLE_PLAYER_NAMES))})""",
        SAMPLE_PLAYER_NAMES,
    )
    print(f"Deleted {cur.rowcount} sample player(s)")

    # 3) sample venues, but only if no remaining match uses them
    cur.execute(
        f"""DELETE FROM venues
            WHERE venue_name IN ({",".join("?" * len(SAMPLE_VENUE_NAMES))})
              AND venue_id NOT IN (SELECT venue_id FROM matches WHERE venue_id IS NOT NULL)""",
        SAMPLE_VENUE_NAMES,
    )
    print(f"Deleted {cur.rowcount} unused sample venue(s)")

    # 4) sample series, but only if no remaining match uses them
    cur.execute(
        f"""DELETE FROM series
            WHERE series_name IN ({",".join("?" * len(SAMPLE_SERIES_NAMES))})
              AND series_id NOT IN (SELECT series_id FROM matches WHERE series_id IS NOT NULL)""",
        SAMPLE_SERIES_NAMES,
    )
    print(f"Deleted {cur.rowcount} unused sample series")

    conn.commit()
    conn.close()
    print("\nDone. Sample data removed, real fetched data untouched.")


if __name__ == "__main__":
    main()

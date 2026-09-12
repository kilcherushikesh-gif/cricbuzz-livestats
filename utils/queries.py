"""
The 25 SQL practice questions from the project brief, written against the
schema in database/schema.sql. Adjust freely once you load real data.
"""

QUERIES = {
    "Q1 (Beginner): Players who represent India": """
        SELECT full_name, playing_role, batting_style, bowling_style
        FROM players p JOIN teams t ON p.team_id = t.team_id
        WHERE t.country = 'India';
    """,

    "Q2 (Beginner): Matches in the last 30 days": """
        SELECT match_desc, t1.team_name AS team1, t2.team_name AS team2,
               v.venue_name, v.city, match_date
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE date(match_date) >= date('now', '-30 days')
        ORDER BY match_date DESC;
    """,

    "Q3 (Beginner): Top run scorers": """
        SELECT p.full_name, SUM(s.runs_scored) AS total_runs,
               ROUND(AVG(s.runs_scored), 2) AS batting_avg
        FROM player_match_stats s JOIN players p ON s.player_id = p.player_id
        GROUP BY p.player_id
        ORDER BY total_runs DESC
        LIMIT 10;
    """,

    "Q4 (Beginner): Venues with capacity > 50,000": """
        SELECT venue_name, city, country, capacity
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC;
    """,

    "Q5 (Beginner): Matches won per team": """
        SELECT t.team_name, COUNT(*) AS total_wins
        FROM matches m JOIN teams t ON m.winning_team_id = t.team_id
        GROUP BY t.team_id
        ORDER BY total_wins DESC;
    """,

    "Q6 (Beginner): Player count per playing role": """
        SELECT playing_role, COUNT(*) AS player_count
        FROM players
        GROUP BY playing_role;
    """,

    "Q7 (Beginner): Highest score per format": """
        SELECT m.match_format, MAX(s.runs_scored) AS highest_score
        FROM player_match_stats s JOIN matches m ON s.match_id = m.match_id
        GROUP BY m.match_format;
    """,

    "Q8 (Beginner): Series started in 2024": """
        SELECT series_name, host_country, match_type, start_date, total_matches
        FROM series
        WHERE start_date LIKE '2024%';
    """,

    "Q9 (Intermediate): All-rounders with 1000+ runs & 50+ wickets": """
        SELECT p.full_name, SUM(s.runs_scored) AS total_runs,
               SUM(s.wickets_taken) AS total_wickets
        FROM player_match_stats s JOIN players p ON s.player_id = p.player_id
        WHERE p.playing_role = 'All-rounder'
        GROUP BY p.player_id
        HAVING total_runs > 1000 AND total_wickets > 50;
    """,

    "Q10 (Intermediate): Last 20 completed matches": """
        SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
               w.team_name AS winner, victory_margin, victory_type, v.venue_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN teams w ON m.winning_team_id = w.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        ORDER BY match_date DESC
        LIMIT 20;
    """,

    "Q11 (Intermediate): Performance across formats": """
        SELECT p.full_name,
               SUM(CASE WHEN m.match_format='Test' THEN s.runs_scored ELSE 0 END) AS test_runs,
               SUM(CASE WHEN m.match_format='ODI' THEN s.runs_scored ELSE 0 END) AS odi_runs,
               SUM(CASE WHEN m.match_format='T20I' THEN s.runs_scored ELSE 0 END) AS t20i_runs,
               ROUND(AVG(s.runs_scored), 2) AS overall_avg
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        GROUP BY p.player_id
        HAVING COUNT(DISTINCT m.match_format) >= 2;
    """,

    "Q12 (Intermediate): Home vs away performance": """
        SELECT t.team_name,
               SUM(CASE WHEN v.country = t.country AND m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
               SUM(CASE WHEN v.country != t.country AND m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
        FROM matches m
        JOIN venues v ON m.venue_id = v.venue_id
        JOIN teams t ON t.team_id IN (m.team1_id, m.team2_id)
        GROUP BY t.team_id;
    """,

    "Q13 (Intermediate): Partnerships >= 100 (consecutive batting positions)": """
        SELECT p1.full_name AS batsman_1, p2.full_name AS batsman_2,
               (s1.runs_scored + s2.runs_scored) AS partnership_runs, s1.match_id
        FROM player_match_stats s1
        JOIN player_match_stats s2
          ON s1.match_id = s2.match_id AND s2.batting_position = s1.batting_position + 1
        JOIN players p1 ON s1.player_id = p1.player_id
        JOIN players p2 ON s2.player_id = p2.player_id
        WHERE (s1.runs_scored + s2.runs_scored) >= 100;
    """,

    "Q14 (Intermediate): Bowling performance by venue (3+ matches, 4+ overs)": """
        SELECT p.full_name, v.venue_name,
               ROUND(AVG(s.economy_rate), 2) AS avg_economy,
               SUM(s.wickets_taken) AS total_wickets,
               COUNT(*) AS matches_played
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE s.overs_bowled >= 4
        GROUP BY p.player_id, v.venue_id
        HAVING matches_played >= 3;
    """,

    "Q15 (Intermediate): Performance in close matches": """
        SELECT p.full_name, ROUND(AVG(s.runs_scored), 2) AS avg_runs_close,
               COUNT(*) AS close_matches_played,
               SUM(CASE WHEN m.winning_team_id = s.team_id THEN 1 ELSE 0 END) AS close_matches_won
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        WHERE (m.victory_type = 'runs' AND m.victory_margin < 50)
           OR (m.victory_type = 'wickets' AND m.victory_margin < 5)
        GROUP BY p.player_id;
    """,

    "Q16 (Intermediate): Yearly batting trend since 2020": """
        SELECT p.full_name, strftime('%Y', m.match_date) AS year,
               ROUND(AVG(s.runs_scored), 2) AS avg_runs,
               ROUND(AVG(s.strike_rate), 2) AS avg_strike_rate,
               COUNT(*) AS matches
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        WHERE date(m.match_date) >= '2020-01-01'
        GROUP BY p.player_id, year
        HAVING matches >= 5;
    """,

    "Q17 (Advanced): Toss impact on match result": """
        SELECT m.toss_decision,
               ROUND(100.0 * SUM(CASE WHEN m.toss_winner_id = m.winning_team_id THEN 1 ELSE 0 END) / COUNT(*), 2)
               AS win_pct_after_winning_toss
        FROM matches m
        WHERE m.toss_winner_id IS NOT NULL
        GROUP BY m.toss_decision;
    """,

    "Q18 (Advanced): Most economical limited-overs bowlers": """
        SELECT p.full_name,
               ROUND(SUM(s.runs_conceded) * 1.0 / NULLIF(SUM(s.overs_bowled), 0), 2) AS economy_rate,
               SUM(s.wickets_taken) AS total_wickets,
               COUNT(*) AS matches
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        WHERE m.match_format IN ('ODI', 'T20I') AND s.overs_bowled > 0
        GROUP BY p.player_id
        HAVING matches >= 10 AND (SUM(s.overs_bowled) * 1.0 / matches) >= 2;
    """,

    "Q19 (Advanced): Most consistent batsmen (since 2022)": """
        SELECT p.full_name,
               ROUND(AVG(s.runs_scored), 2) AS avg_runs,
               ROUND(
                 SQRT(AVG(s.runs_scored * s.runs_scored) - AVG(s.runs_scored) * AVG(s.runs_scored)), 2
               ) AS stddev_runs
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        WHERE s.balls_faced >= 10 AND date(m.match_date) >= '2022-01-01'
        GROUP BY p.player_id
        ORDER BY stddev_runs ASC;
    """,

    "Q20 (Advanced): Format-wise match count & average (20+ total matches)": """
        SELECT p.full_name,
               SUM(CASE WHEN m.match_format='Test' THEN 1 ELSE 0 END) AS test_matches,
               SUM(CASE WHEN m.match_format='ODI' THEN 1 ELSE 0 END) AS odi_matches,
               SUM(CASE WHEN m.match_format='T20I' THEN 1 ELSE 0 END) AS t20_matches,
               ROUND(AVG(s.runs_scored), 2) AS batting_avg
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        GROUP BY p.player_id
        HAVING (test_matches + odi_matches + t20_matches) >= 20;
    """,

    "Q21 (Advanced): Weighted performance ranking": """
        SELECT p.full_name,
               ROUND(SUM(s.runs_scored) * 0.01 + AVG(s.runs_scored) * 0.5 + AVG(s.strike_rate) * 0.3, 2) AS batting_points,
               ROUND(SUM(s.wickets_taken) * 2 + (50 - AVG(NULLIF(s.economy_rate,0))) * 0.5 + (6 - AVG(NULLIF(s.economy_rate,0))) * 2, 2) AS bowling_points,
               (SUM(s.catches) * 3 + SUM(s.stumpings) * 5) AS fielding_points
        FROM player_match_stats s JOIN players p ON s.player_id = p.player_id
        GROUP BY p.player_id
        ORDER BY batting_points DESC;
    """,

    "Q22 (Advanced): Head-to-head analysis": """
        SELECT t1.team_name AS team_a, t2.team_name AS team_b,
               COUNT(*) AS total_matches,
               SUM(CASE WHEN m.winning_team_id = m.team1_id THEN 1 ELSE 0 END) AS team_a_wins,
               SUM(CASE WHEN m.winning_team_id = m.team2_id THEN 1 ELSE 0 END) AS team_b_wins,
               ROUND(AVG(m.victory_margin), 2) AS avg_victory_margin
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        WHERE date(m.match_date) >= date('now', '-3 years')
        GROUP BY t1.team_id, t2.team_id
        HAVING total_matches >= 5;
    """,

    "Q23 (Advanced): Recent form & momentum": """
        SELECT p.full_name,
               ROUND(AVG(s.runs_scored), 2) AS avg_runs_last_10,
               ROUND(AVG(s.strike_rate), 2) AS avg_strike_rate,
               SUM(CASE WHEN s.runs_scored > 50 THEN 1 ELSE 0 END) AS scores_above_50,
               CASE
                 WHEN AVG(s.runs_scored) >= 50 THEN 'Excellent Form'
                 WHEN AVG(s.runs_scored) >= 35 THEN 'Good Form'
                 WHEN AVG(s.runs_scored) >= 20 THEN 'Average Form'
                 ELSE 'Poor Form'
               END AS form_category
        FROM (
            SELECT s.*, m.match_date
            FROM player_match_stats s JOIN matches m ON s.match_id = m.match_id
            ORDER BY m.match_date DESC
        ) s
        JOIN players p ON s.player_id = p.player_id
        GROUP BY p.player_id;
    """,

    "Q24 (Advanced): Successful batting partnerships": """
        SELECT p1.full_name AS batsman_1, p2.full_name AS batsman_2,
               ROUND(AVG(s1.runs_scored + s2.runs_scored), 2) AS avg_partnership_runs,
               SUM(CASE WHEN (s1.runs_scored + s2.runs_scored) > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
               MAX(s1.runs_scored + s2.runs_scored) AS highest_partnership,
               COUNT(*) AS total_partnerships
        FROM player_match_stats s1
        JOIN player_match_stats s2
          ON s1.match_id = s2.match_id AND ABS(s2.batting_position - s1.batting_position) = 1
        JOIN players p1 ON s1.player_id = p1.player_id
        JOIN players p2 ON s2.player_id = p2.player_id
        WHERE p1.player_id < p2.player_id
        GROUP BY p1.player_id, p2.player_id
        HAVING total_partnerships >= 5
        ORDER BY avg_partnership_runs DESC;
    """,

    "Q25 (Advanced): Career trajectory (quarterly trend)": """
        SELECT p.full_name,
               strftime('%Y', m.match_date) || '-Q' ||
                 ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
               ROUND(AVG(s.runs_scored), 2) AS avg_runs,
               ROUND(AVG(s.strike_rate), 2) AS avg_strike_rate
        FROM player_match_stats s
        JOIN players p ON s.player_id = p.player_id
        JOIN matches m ON s.match_id = m.match_id
        GROUP BY p.player_id, quarter
        ORDER BY p.full_name, quarter;
    """,
}

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "cricbuzz.db"


def get_top_stats_from_db(stat_type="mostRuns", match_format="T20I", limit=20):
    conn = sqlite3.connect(DB_PATH)

    if stat_type == "mostRuns":
        query = """
            SELECT p.full_name AS "Batter",
                   COUNT(DISTINCT s.match_id) AS "Matches",
                   SUM(s.runs_scored) AS "Runs",
                   ROUND(AVG(s.strike_rate), 2) AS "Avg SR"
            FROM player_match_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN matches m ON s.match_id = m.match_id
            WHERE m.match_format = ?
            GROUP BY p.player_id
            ORDER BY "Runs" DESC
            LIMIT ?;
        """
    elif stat_type == "mostWickets":
        query = """
            SELECT p.full_name AS "Bowler",
                   COUNT(DISTINCT s.match_id) AS "Matches",
                   SUM(s.wickets_taken) AS "Wickets",
                   ROUND(AVG(s.economy_rate), 2) AS "Avg Economy"
            FROM player_match_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN matches m ON s.match_id = m.match_id
            WHERE m.match_format = ?
            GROUP BY p.player_id
            ORDER BY "Wickets" DESC
            LIMIT ?;
        """
    elif stat_type == "highestScore":
        query = """
            SELECT p.full_name AS "Batter",
                   s.runs_scored AS "Runs",
                   s.balls_faced AS "Balls",
                   s.strike_rate AS "SR",
                   m.match_desc AS "Match",
                   m.match_date AS "Date"
            FROM player_match_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN matches m ON s.match_id = m.match_id
            WHERE m.match_format = ?
            ORDER BY s.runs_scored DESC
            LIMIT ?;
        """
    elif stat_type == "bestBowling":
        query = """
            SELECT p.full_name AS "Bowler",
                   s.wickets_taken AS "Wickets",
                   s.runs_conceded AS "Runs Conceded",
                   s.economy_rate AS "Economy",
                   m.match_desc AS "Match",
                   m.match_date AS "Date"
            FROM player_match_stats s
            JOIN players p ON s.player_id = p.player_id
            JOIN matches m ON s.match_id = m.match_id
            WHERE m.match_format = ?
            ORDER BY s.wickets_taken DESC, s.runs_conceded ASC
            LIMIT ?;
        """
    else:
        conn.close()
        return pd.DataFrame()

    df = pd.read_sql_query(query, conn, params=(match_format, limit))
    conn.close()
    return df
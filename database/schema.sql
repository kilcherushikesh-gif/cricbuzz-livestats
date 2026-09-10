-- Cricbuzz LiveStats: SQLite schema
-- Run this once to create all tables.

DROP TABLE IF EXISTS player_match_stats;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS series;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS venues;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    team_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name   TEXT NOT NULL UNIQUE,
    country     TEXT NOT NULL
);

CREATE TABLE players (
    player_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    team_id         INTEGER,
    playing_role    TEXT,        -- Batsman / Bowler / All-rounder / Wicket-keeper
    batting_style   TEXT,
    bowling_style   TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE venues (
    venue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name  TEXT NOT NULL,
    city        TEXT,
    country     TEXT,
    capacity    INTEGER
);

CREATE TABLE series (
    series_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name     TEXT NOT NULL,
    host_country    TEXT,
    match_type      TEXT,        -- Test / ODI / T20I
    start_date      TEXT,
    total_matches   INTEGER
);

CREATE TABLE matches (
    match_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id       INTEGER,
    match_desc      TEXT,
    team1_id        INTEGER,
    team2_id        INTEGER,
    venue_id        INTEGER,
    match_date      TEXT,
    match_format    TEXT,        -- Test / ODI / T20I
    winning_team_id INTEGER,
    victory_margin  INTEGER,
    victory_type    TEXT,        -- runs / wickets
    toss_winner_id  INTEGER,
    toss_decision   TEXT,        -- bat / bowl
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (winning_team_id) REFERENCES teams(team_id)
);

CREATE TABLE player_match_stats (
    stat_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER,
    player_id       INTEGER,
    team_id         INTEGER,
    batting_position INTEGER,
    runs_scored     INTEGER DEFAULT 0,
    balls_faced     INTEGER DEFAULT 0,
    fours           INTEGER DEFAULT 0,
    sixes           INTEGER DEFAULT 0,
    strike_rate     REAL DEFAULT 0,
    overs_bowled    REAL DEFAULT 0,
    runs_conceded   INTEGER DEFAULT 0,
    wickets_taken   INTEGER DEFAULT 0,
    economy_rate    REAL DEFAULT 0,
    catches         INTEGER DEFAULT 0,
    stumpings       INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

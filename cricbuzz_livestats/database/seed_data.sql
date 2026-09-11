-- Sample data so you can test the SQL Analytics page right away.
-- This is small dummy data, NOT live data. Replace/expand it later
-- by pulling real data from the Cricbuzz API (see utils/api_utils.py).

INSERT INTO teams (team_name, country) VALUES
('India', 'India'),
('Australia', 'Australia'),
('England', 'England'),
('South Africa', 'South Africa');

INSERT INTO players (full_name, team_id, playing_role, batting_style, bowling_style) VALUES
('Virat Kohli', 1, 'Batsman', 'Right-hand bat', NULL),
('Jasprit Bumrah', 1, 'Bowler', 'Right-hand bat', 'Right-arm fast'),
('Ravindra Jadeja', 1, 'All-rounder', 'Left-hand bat', 'Left-arm orthodox'),
('Steve Smith', 2, 'Batsman', 'Right-hand bat', NULL),
('Pat Cummins', 2, 'Bowler', 'Right-hand bat', 'Right-arm fast'),
('Joe Root', 3, 'Batsman', 'Right-hand bat', NULL),
('Ben Stokes', 3, 'All-rounder', 'Left-hand bat', 'Right-arm fast-medium'),
('Kagiso Rabada', 4, 'Bowler', 'Right-hand bat', 'Right-arm fast');

INSERT INTO venues (venue_name, city, country, capacity) VALUES
('Melbourne Cricket Ground', 'Melbourne', 'Australia', 100024),
('Eden Gardens', 'Kolkata', 'India', 68000),
('Lord''s', 'London', 'England', 30000),
('Wankhede Stadium', 'Mumbai', 'India', 33000);

INSERT INTO series (series_name, host_country, match_type, start_date, total_matches) VALUES
('Border-Gavaskar Trophy 2024', 'Australia', 'Test', '2024-12-01', 5),
('India vs England ODI Series 2024', 'India', 'ODI', '2024-02-01', 3);

INSERT INTO matches (series_id, match_desc, team1_id, team2_id, venue_id, match_date, match_format,
                      winning_team_id, victory_margin, victory_type, toss_winner_id, toss_decision) VALUES
(1, 'India vs Australia, 1st Test', 1, 2, 1, '2024-12-06', 'Test', 2, 9, 'wickets', 1, 'bat'),
(2, 'India vs England, 1st ODI', 1, 3, 2, '2024-02-01', 'ODI', 1, 45, 'runs', 3, 'bowl');

INSERT INTO player_match_stats (match_id, player_id, team_id, batting_position, runs_scored, balls_faced,
                                 fours, sixes, strike_rate, overs_bowled, runs_conceded, wickets_taken,
                                 economy_rate, catches, stumpings) VALUES
(1, 1, 1, 4, 76, 130, 8, 0, 58.46, 0, 0, 0, 0, 1, 0),
(1, 2, 1, 11, 5, 10, 0, 0, 50.00, 22, 61, 4, 2.77, 0, 0),
(1, 4, 2, 4, 55, 120, 5, 0, 45.83, 0, 0, 0, 0, 0, 0),
(2, 1, 1, 3, 89, 94, 9, 2, 94.68, 0, 0, 0, 0, 0, 0),
(2, 6, 3, 3, 60, 70, 6, 1, 85.71, 0, 0, 0, 0, 1, 0);

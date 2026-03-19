
INSERT INTO dbo.fact_player_injury (
    player_id, team_id, league_id, season,
    date, type, reason
)
SELECT 
    player_id, team_id, league_id, season,
    date, type, reason
FROM staging.player_injuries;
-- fact_player_event merge
INSERT INTO dbo.fact_player_event (
    fixture_id, player_id, team_id,
    event_type, detail, comments, minute
)
SELECT 
    fixture_id, player_id, team_id,
    type, detail, comments, minute
FROM staging.player_events;
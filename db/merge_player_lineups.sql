-- fact_player_lineup merge
MERGE dbo.fact_player_lineup AS tgt
USING staging.player_lineups AS src
ON tgt.fixture_id = src.fixture_id
AND tgt.player_id = src.player_id

WHEN MATCHED THEN
    UPDATE SET
        team_id = src.team_id,
        number = src.number,
        position = src.position,
        grid = src.grid

WHEN NOT MATCHED THEN
    INSERT (fixture_id, player_id, team_id, number, position, grid)
    VALUES (src.fixture_id, src.player_id, src.team_id, src.number, src.position, src.grid);
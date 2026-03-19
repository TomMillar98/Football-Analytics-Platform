-- fact_standing merge
MERGE dbo.fact_standing AS tgt
USING (
    SELECT *
    FROM staging.standings
) AS src
ON tgt.comp_id = src.comp_id
AND tgt.season = src.season
AND tgt.team_id = src.team_id

WHEN MATCHED THEN
    UPDATE SET
        rank = src.rank,
        points = src.points,
        played = src.played,
        won = src.won,
        draw = src.draw,
        lost = src.lost,
        goals_for = src.goals_for,
        goals_against = src.goals_against,
        last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (comp_id, season, team_id, rank, points, played, won, draw, lost, goals_for, goals_against, last_updated)
    VALUES (
        src.comp_id, src.season, src.team_id,
        src.rank, src.points, src.played, src.won, src.draw, src.lost,
        src.goals_for, src.goals_against, SYSUTCDATETIME()
    );
-----------------------------------------------------------------------
-- MERGE: DIM PLAYER
-----------------------------------------------------------------------
MERGE dbo.dim_player AS tgt
USING (
    SELECT DISTINCT
        player_id,
        name,
        firstname,
        lastname,
        nationality,
        birth_date,
        height,
        weight
    FROM staging.players
) AS src
ON tgt.player_id = src.player_id

WHEN MATCHED THEN
    UPDATE SET
        tgt.name         = src.name,
        tgt.firstname    = src.firstname,
        tgt.lastname     = src.lastname,
        tgt.nationality  = src.nationality,
        tgt.birth_date   = src.birth_date,
        tgt.height       = src.height,
        tgt.weight       = src.weight,
        tgt.last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (player_id, name, firstname, lastname, nationality, birth_date, height, weight, last_updated)
    VALUES (src.player_id, src.name, src.firstname, src.lastname, src.nationality,
            src.birth_date, src.height, src.weight, SYSUTCDATETIME());


-----------------------------------------------------------------------
-- MERGE: FACT PLAYER SEASON
-- A player can have multiple entries per season AND league
-- Composite key = (player_id, comp_id, season)
-----------------------------------------------------------------------
MERGE dbo.fact_player_season AS tgt
USING (
    SELECT
        player_id,
        team_id,
        league_id AS comp_id,
        season,
        position,
        number,
        appearances,
        lineups,
        minutes,
        goals,
        assists,
        yellow,
        red
    FROM staging.players
) AS src
ON  tgt.player_id = src.player_id
AND tgt.comp_id   = src.comp_id
AND tgt.season    = src.season

WHEN MATCHED THEN
    UPDATE SET
        tgt.team_id     = src.team_id,
        tgt.position    = src.position,
        tgt.number      = src.number,
        tgt.appearances = src.appearances,
        tgt.lineups     = src.lineups,
        tgt.minutes     = src.minutes,
        tgt.goals       = src.goals,
        tgt.assists     = src.assists,
        tgt.yellow      = src.yellow,
        tgt.red         = src.red,
        tgt.last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (player_id, team_id, comp_id, season, position, number,
            appearances, lineups, minutes,
            goals, assists, yellow, red, last_updated)
    VALUES (src.player_id, src.team_id, src.comp_id, src.season, src.position, src.number,
            src.appearances, src.lineups, src.minutes,
            src.goals, src.assists, src.yellow, src.red, SYSUTCDATETIME());
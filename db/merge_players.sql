MERGE dbo.dim_player AS tgt
USING (
    SELECT 
        player_id,
        MAX(name) AS name,
        MAX(firstname) AS firstname,
        MAX(lastname) AS lastname,
        MAX(nationality) AS nationality,
        MAX(birth_date) AS birth_date,
        MAX(height) AS height,
        MAX(weight) AS weight,
        MAX(photo_url) AS photo_url
    FROM staging.players
    GROUP BY player_id
) AS src
ON tgt.player_id = src.player_id

WHEN MATCHED THEN
    UPDATE SET
        name = src.name,
        firstname = src.firstname,
        lastname = src.lastname,
        nationality = src.nationality,
        birth_date = src.birth_date,
        height = src.height,
        weight = src.weight,
        photo_url = src.photo_url,
        last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (player_id, name, firstname, lastname, nationality, birth_date,
            height, weight, photo_url, last_updated)
    VALUES (src.player_id, src.name, src.firstname, src.lastname,
            src.nationality, src.birth_date, src.height, src.weight,
            src.photo_url, SYSUTCDATETIME());


MERGE dbo.fact_player_season AS tgt
USING (
    SELECT *
    FROM (
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
            red,
            ROW_NUMBER() OVER (
                PARTITION BY player_id, league_id, season
                ORDER BY minutes DESC
            ) AS rn
        FROM staging.players
    ) AS x
    WHERE rn = 1      -- only keep best row per player/team/season
) AS src
ON tgt.player_id = src.player_id
AND tgt.comp_id = src.comp_id
AND tgt.season = src.season

WHEN MATCHED THEN
    UPDATE SET
        team_id = src.team_id,
        position = src.position,
        number = src.number,
        appearances = src.appearances,
        lineups = src.lineups,
        minutes = src.minutes,
        goals = src.goals,
        assists = src.assists,
        yellow = src.yellow,
        red = src.red,
        last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (player_id, team_id, comp_id, season, position, number,
            appearances, lineups, minutes, goals, assists, yellow, red, last_updated)
    VALUES (src.player_id, src.team_id, src.comp_id, src.season, src.position,
            src.number, src.appearances, src.lineups, src.minutes, src.goals,
            src.assists, src.yellow, src.red, SYSUTCDATETIME());